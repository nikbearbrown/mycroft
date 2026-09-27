package main

import (
	"context"
	"fmt"
	"io"
	"log/slog"
	"net/http"
	"time"
)

// secClient wraps http.Client with the SEC-required User-Agent and the shared
// Redis token bucket. Every outbound SEC request goes through Get().
type secClient struct {
	http *http.Client
	ua   string
	rl   *RateLimiter
	log  *slog.Logger
}

func newSECClient(ua string, rl *RateLimiter, log *slog.Logger) *secClient {
	return &secClient{
		http: &http.Client{Timeout: 20 * time.Second},
		ua:   ua,
		rl:   rl,
		log:  log,
	}
}

// Get performs a rate-limited GET and returns the body and status code.
// A non-2xx status is returned without error so callers can decide (SEC 403s
// on a bad User-Agent; a 429 means back off).
func (c *secClient) Get(ctx context.Context, url string) ([]byte, int, error) {
	if err := c.rl.Wait(ctx); err != nil {
		return nil, 0, err
	}
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, url, nil)
	if err != nil {
		return nil, 0, err
	}
	req.Header.Set("User-Agent", c.ua)
	// Do NOT set Accept-Encoding manually: Go's transport adds "gzip" and
	// transparently decompresses only when it owns the header.
	resp, err := c.http.Do(req)
	if err != nil {
		return nil, 0, err
	}
	defer resp.Body.Close()
	body, err := io.ReadAll(io.LimitReader(resp.Body, 8<<20))
	if err != nil {
		return nil, resp.StatusCode, fmt.Errorf("read body: %w", err)
	}
	return body, resp.StatusCode, nil
}
