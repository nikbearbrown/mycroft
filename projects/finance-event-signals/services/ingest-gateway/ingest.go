package main

import (
	"context"
	"crypto/sha1"
	"encoding/hex"
	"strings"
	"time"

	fesv1 "github.com/finance-event-signals/proto/gen/fes/v1"
)

// ingestServer is the manual / webhook entry point. It reuses the same dedup +
// produce path as the poller — a submitted event lands on events.raw exactly like
// a polled one.
type ingestServer struct {
	g *gateway
}

func (s *ingestServer) SubmitEvent(ctx context.Context, req *fesv1.SubmitEventRequest) (*fesv1.SubmitEventResponse, error) {
	if strings.TrimSpace(req.Title) == "" && strings.TrimSpace(req.Company) == "" {
		return &fesv1.SubmitEventResponse{Accepted: false, Reason: "need at least company or title"}, nil
	}

	h := sha1.Sum([]byte(req.Company + "|" + req.Title + "|" + req.Url + "|" + strings.Join(req.Items, ",")))
	key := "manual-" + hex.EncodeToString(h[:10])
	now := time.Now().UTC().Format(time.RFC3339)

	fresh, err := s.g.rdb.SetNX(ctx, "dedup:"+key, "1", s.g.cfg.DedupTTL).Result()
	if err != nil {
		return nil, err
	}
	if !fresh {
		return &fesv1.SubmitEventResponse{EventKey: key, Accepted: false, Reason: "duplicate (already submitted)"}, nil
	}

	ev := Event{
		EventKey:    key,
		Source:      "manual",
		Form:        req.Form,
		CIK:         req.Cik,
		Company:     req.Company,
		Title:       req.Title,
		Items:       req.Items,
		URL:         req.Url,
		PublishedAt: now,
		FetchedAt:   now,
		Raw: map[string]any{
			"submitted_via": "grpc",
			"company":       req.Company, "cik": req.Cik, "form": req.Form,
			"title": req.Title, "url": req.Url, "items": req.Items,
			"received_at": now,
		},
	}
	if err := s.g.produce(ctx, ev); err != nil {
		s.g.rdb.Del(ctx, "dedup:"+key)
		return nil, err
	}
	s.g.log.Info("manual event submitted", "key", key, "company", req.Company)
	return &fesv1.SubmitEventResponse{EventKey: key, Accepted: true}, nil
}
