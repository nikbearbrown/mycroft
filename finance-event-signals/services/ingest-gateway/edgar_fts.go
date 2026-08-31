package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log/slog"
	"net/url"
	"strings"
	"time"
)

const ftsBase = "https://efts.sec.gov/LATEST/search-index"

type ftsHit struct {
	ID     string `json:"_id"`
	Source struct {
		CIKs         []string `json:"ciks"`
		DisplayNames []string `json:"display_names"`
		Form         string   `json:"form"`
		ADSH         string   `json:"adsh"`
		FileDate     string   `json:"file_date"`
		Items        []string `json:"items"`
		FileDesc     string   `json:"file_description"`
	} `json:"_source"`
}

// fetchFTS pulls recent filings from EDGAR full-text search. JSON REST path.
func fetchFTS(ctx context.Context, c *secClient, cfg Config, log *slog.Logger) ([]Event, error) {
	now := time.Now().UTC()
	start := now.AddDate(0, 0, -cfg.FTSLookbackDays).Format("2006-01-02")
	end := now.Format("2006-01-02")

	var out []Event
	const pageSize = 100
	for from := 0; from < cfg.FTSMaxHits; from += pageSize {
		q := url.Values{}
		q.Set("forms", cfg.FTSForms)
		q.Set("startdt", start)
		q.Set("enddt", end)
		q.Set("from", fmt.Sprint(from))
		if cfg.FTSQuery != "" {
			q.Set("q", cfg.FTSQuery)
		}
		u := ftsBase + "?" + q.Encode()

		body, status, err := c.Get(ctx, u)
		if err != nil {
			return out, fmt.Errorf("fts get: %w", err)
		}
		if status != 200 {
			return out, fmt.Errorf("fts status %d: %s", status, truncate(body, 200))
		}

		var resp struct {
			Hits struct {
				Total struct {
					Value int `json:"value"`
				} `json:"total"`
				Hits []json.RawMessage `json:"hits"`
			} `json:"hits"`
		}
		if err := json.Unmarshal(body, &resp); err != nil {
			return out, fmt.Errorf("fts decode: %w", err)
		}

		for _, raw := range resp.Hits.Hits {
			var h ftsHit
			if err := json.Unmarshal(raw, &h); err != nil {
				log.Warn("fts hit decode", "err", err)
				continue
			}
			if h.Source.ADSH == "" {
				continue
			}
			ev := ftsHitToEvent(h, raw, now)
			out = append(out, ev)
		}

		if from+pageSize >= resp.Hits.Total.Value || len(resp.Hits.Hits) == 0 {
			break
		}
	}
	return out, nil
}

func ftsHitToEvent(h ftsHit, raw json.RawMessage, fetchedAt time.Time) Event {
	cik := ""
	if len(h.Source.CIKs) > 0 {
		cik = h.Source.CIKs[0]
	}
	company := ""
	if len(h.Source.DisplayNames) > 0 {
		company = displayNameCompany(h.Source.DisplayNames[0])
	}
	title := h.Source.FileDesc
	if len(h.Source.Items) > 0 {
		title = fmt.Sprintf("%s — items %s", h.Source.Form, strings.Join(h.Source.Items, ", "))
	} else if title == "" {
		title = h.Source.Form
	}
	published := ""
	if h.Source.FileDate != "" {
		published = h.Source.FileDate + "T00:00:00Z"
	}
	return Event{
		EventKey:    h.Source.ADSH,
		Source:      "edgar_fts",
		Form:        h.Source.Form,
		CIK:         cik,
		Company:     company,
		Title:       title,
		Items:       h.Source.Items,
		URL:         filingURL(h.ID, cik),
		PublishedAt: published,
		FetchedAt:   fetchedAt.Format(time.RFC3339),
		EventType:   nil,
		Raw:         raw,
	}
}

// display_names entries look like "Monroe Capital Enhanced ... Fund  (CIK 0002061670)"
// and occasionally "LOCKHEED MARTIN CORP  (LMT)". Strip any trailing "  (...)".
func displayNameCompany(s string) string {
	if i := strings.LastIndex(s, "  ("); i >= 0 {
		return strings.TrimSpace(s[:i])
	}
	return strings.TrimSpace(s)
}

// _id "0002061670-26-000083:mlend-20260828.htm" + subject CIK -> archive URL.
// The archive path uses the SUBJECT company's CIK, not the accession-number
// prefix (which is the filing agent) — the latter 404s.
func filingURL(id, subjectCIK string) string {
	parts := strings.SplitN(id, ":", 2)
	adsh := parts[0]
	doc := ""
	if len(parts) == 2 {
		doc = parts[1]
	}
	adshNoDash := strings.ReplaceAll(adsh, "-", "")
	cik := strings.TrimLeft(subjectCIK, "0")
	if cik == "" {
		cik = strings.TrimLeft(strings.SplitN(adsh, "-", 2)[0], "0") // fallback
	}
	if doc == "" {
		return fmt.Sprintf("https://www.sec.gov/Archives/edgar/data/%s/%s/%s-index.htm", cik, adshNoDash, adsh)
	}
	return fmt.Sprintf("https://www.sec.gov/Archives/edgar/data/%s/%s/%s", cik, adshNoDash, doc)
}

func truncate(b []byte, n int) string {
	if len(b) <= n {
		return string(b)
	}
	return string(b[:n]) + "…"
}
