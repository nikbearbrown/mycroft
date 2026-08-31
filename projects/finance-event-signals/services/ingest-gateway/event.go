package main

import "encoding/json"

// Event is the envelope on the wire. See data/verified/SCHEMA_REFERENCE.md.
type Event struct {
	EventKey    string          `json:"event_key"`
	Source      string          `json:"source"`
	Form        string          `json:"form,omitempty"`
	Ticker      string          `json:"ticker,omitempty"`
	CIK         string          `json:"cik,omitempty"`
	Company     string          `json:"company,omitempty"`
	Title       string          `json:"title,omitempty"`
	URL         string          `json:"url,omitempty"`
	Items       []string        `json:"items,omitempty"` // 8-K item codes, e.g. ["1.01","9.01"]
	PublishedAt string          `json:"published_at,omitempty"`
	FetchedAt   string          `json:"fetched_at"`
	EventType   *string         `json:"event_type"`
	Signal      json.RawMessage `json:"signal,omitempty"`
	Raw         any             `json:"raw"`
}
