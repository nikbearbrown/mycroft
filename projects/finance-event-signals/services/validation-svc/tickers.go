package main

import (
	"encoding/json"
	"os"
	"strconv"
	"strings"
)

// CIK -> ticker, loaded from SEC's company_tickers.json (baked into the image).
type tickerMap map[string]string

type tickerEntry struct {
	CIK    int    `json:"cik_str"`
	Ticker string `json:"ticker"`
	Title  string `json:"title"`
}

func loadTickers(path string) (tickerMap, error) {
	b, err := os.ReadFile(path)
	if err != nil {
		return nil, err
	}
	var raw map[string]tickerEntry
	if err := json.Unmarshal(b, &raw); err != nil {
		return nil, err
	}
	m := make(tickerMap, len(raw))
	for _, e := range raw {
		if e.Ticker != "" {
			m[strconv.Itoa(e.CIK)] = e.Ticker
		}
	}
	return m, nil
}

func (m tickerMap) resolve(cik string) string {
	if cik == "" {
		return ""
	}
	return m[strings.TrimLeft(cik, "0")]
}
