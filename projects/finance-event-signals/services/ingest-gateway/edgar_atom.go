package main

import (
	"bytes"
	"context"
	"encoding/xml"
	"fmt"
	"log/slog"
	"regexp"
	"strings"
	"time"

	"golang.org/x/net/html/charset"
)

const atomBase = "https://www.sec.gov/cgi-bin/browse-edgar"

type atomFeed struct {
	XMLName xml.Name    `xml:"feed"`
	Entries []atomEntry `xml:"entry"`
}

type atomEntry struct {
	Title   string `xml:"title"`
	Updated string `xml:"updated"`
	ID      string `xml:"id"`
	Summary string `xml:"summary"`
	Links   []struct {
		Rel  string `xml:"rel,attr"`
		Href string `xml:"href,attr"`
	} `xml:"link"`
	Category struct {
		Term string `xml:"term,attr"`
	} `xml:"category"`
}

var cikRe = regexp.MustCompile(`\((\d{7,10})\)`)
var itemRe = regexp.MustCompile(`Item\s+(\d\.\d{2})`)

// fetchAtom pulls the EDGAR "latest filings" Atom feed. XML path — deliberately a
// different parser and shape from fetchFTS, so we exercise two ingestion code paths.
func fetchAtom(ctx context.Context, c *secClient, cfg Config, log *slog.Logger) ([]Event, error) {
	u := fmt.Sprintf("%s?action=getcurrent&type=%s&company=&dateb=&owner=include&count=100&output=atom",
		atomBase, cfg.AtomForms)

	body, status, err := c.Get(ctx, u)
	if err != nil {
		return nil, fmt.Errorf("atom get: %w", err)
	}
	if status != 200 {
		return nil, fmt.Errorf("atom status %d: %s", status, truncate(body, 200))
	}

	dec := xml.NewDecoder(bytes.NewReader(body))
	dec.CharsetReader = charset.NewReaderLabel
	var feed atomFeed
	if err := dec.Decode(&feed); err != nil {
		return nil, fmt.Errorf("atom decode: %w", err)
	}

	now := time.Now().UTC()
	var out []Event
	for _, e := range feed.Entries {
		ev, ok := atomEntryToEvent(e, now)
		if !ok {
			log.Warn("atom entry skipped (no accession)", "title", e.Title)
			continue
		}
		out = append(out, ev)
	}
	return out, nil
}

func atomEntryToEvent(e atomEntry, fetchedAt time.Time) (Event, bool) {
	acc := strings.TrimPrefix(strings.TrimSpace(e.ID), "urn:tag:sec.gov,2008:accession-number=")
	if acc == "" || acc == strings.TrimSpace(e.ID) {
		return Event{}, false
	}

	form := strings.TrimSpace(e.Category.Term)
	company := strings.TrimSpace(e.Title)
	if i := strings.Index(company, " - "); i >= 0 {
		if form == "" {
			form = strings.TrimSpace(company[:i])
		}
		company = strings.TrimSpace(company[i+3:])
	}
	cik := ""
	if m := cikRe.FindStringSubmatch(company); m != nil {
		cik = m[1]
		company = strings.TrimSpace(company[:strings.Index(company, m[0])])
	}
	company = strings.TrimSuffix(company, " (Filer)")

	url := ""
	for _, l := range e.Links {
		if l.Rel == "alternate" && l.Href != "" {
			url = l.Href
			break
		}
	}

	published := strings.TrimSpace(e.Updated)
	if t, err := time.Parse(time.RFC3339, published); err == nil {
		published = t.UTC().Format(time.RFC3339)
	}

	// the <summary> lists "Item 1.01: Entry into a Material Definitive Agreement" lines
	var items []string
	seen := map[string]bool{}
	for _, m := range itemRe.FindAllStringSubmatch(e.Summary, -1) {
		if !seen[m[1]] {
			seen[m[1]] = true
			items = append(items, m[1])
		}
	}

	// store the entry itself as provenance
	raw := map[string]any{
		"title":    e.Title,
		"updated":  e.Updated,
		"id":       e.ID,
		"summary":  strings.TrimSpace(e.Summary),
		"category": e.Category.Term,
	}

	return Event{
		EventKey:    acc,
		Source:      "edgar_atom",
		Form:        form,
		CIK:         cik,
		Company:     company,
		Title:       strings.TrimSpace(e.Title),
		Items:       items,
		URL:         url,
		PublishedAt: published,
		FetchedAt:   fetchedAt.Format(time.RFC3339),
		EventType:   nil,
		Raw:         raw,
	}, true
}
