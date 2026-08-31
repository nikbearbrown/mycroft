// validation-svc — the GIGO gate. Consumes events.raw, checks schema + freshness,
// resolves CIK -> ticker, and promotes to events.validated. Anything that fails a
// hard check goes to events.deadletter WITH A REASON — never silently dropped (P2/P3).
package main

import (
	"context"
	"encoding/json"
	"log/slog"
	"os"
	"os/signal"
	"strconv"
	"strings"
	"syscall"
	"time"

	"github.com/finance-event-signals/common"
	"github.com/twmb/franz-go/pkg/kgo"
	"go.opentelemetry.io/otel/attribute"
)

type Event struct {
	EventKey    string          `json:"event_key"`
	Source      string          `json:"source"`
	Form        string          `json:"form,omitempty"`
	Ticker      string          `json:"ticker,omitempty"`
	CIK         string          `json:"cik,omitempty"`
	Company     string          `json:"company,omitempty"`
	Title       string          `json:"title,omitempty"`
	URL         string          `json:"url,omitempty"`
	Items       []string        `json:"items,omitempty"`
	PublishedAt string          `json:"published_at,omitempty"`
	FetchedAt   string          `json:"fetched_at"`
	EventType   *string         `json:"event_type"`
	Signal      json.RawMessage `json:"signal,omitempty"`
	Raw         json.RawMessage `json:"raw"`

	// added on rejection
	RejectReason string `json:"reject_reason,omitempty"`
	RejectedAt   string `json:"rejected_at,omitempty"`
}

type config struct {
	brokers        []string
	topicIn        string
	topicValidated string
	topicDeadletter string
	groupID        string
	freshnessDays  int
	tickersPath    string
}

func main() {
	log := slog.New(slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{Level: slog.LevelInfo}))
	cfg := config{
		brokers:        strings.Split(env("KAFKA_BROKERS", "redpanda:9092"), ","),
		topicIn:        env("TOPIC_IN", "events.raw"),
		topicValidated: env("TOPIC_VALIDATED", "events.validated"),
		topicDeadletter: env("TOPIC_DEADLETTER", "events.deadletter"),
		groupID:        env("GROUP_ID", "validation-svc"),
		freshnessDays:  envInt("FRESHNESS_DAYS", 7),
		tickersPath:    env("TICKERS_PATH", "/app/data/company_tickers.json"),
	}

	tickers, err := loadTickers(cfg.tickersPath)
	if err != nil {
		log.Error("load tickers", "err", err, "path", cfg.tickersPath)
		os.Exit(1)
	}
	log.Info("validation-svc started", "tickers_loaded", len(tickers),
		"freshness_days", cfg.freshnessDays, "in", cfg.topicIn)

	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer stop()

	shutdown, err := common.Init(ctx, "validation-svc")
	if err != nil {
		log.Error("otel init", "err", err)
	}
	defer func() { _ = shutdown(context.Background()) }()
	tr := common.Tracer("validation-svc")

	cl, err := kgo.NewClient(
		kgo.SeedBrokers(cfg.brokers...),
		kgo.ConsumerGroup(cfg.groupID),
		kgo.ConsumeTopics(cfg.topicIn),
		kgo.DisableAutoCommit(),
		kgo.RequiredAcks(kgo.AllISRAcks()),
	)
	if err != nil {
		log.Error("kafka client", "err", err)
		os.Exit(1)
	}
	defer cl.Close()

	for {
		fetches := cl.PollFetches(ctx)
		if fetches.IsClientClosed() || ctx.Err() != nil {
			log.Info("shutting down")
			return
		}
		fetches.EachError(func(t string, p int32, err error) {
			log.Error("fetch", "topic", t, "partition", p, "err", err)
		})

		validated, rejected := 0, 0
		produceErr := false
		iter := fetches.RecordIter()
		for !iter.Done() {
			rec := iter.Next()
			cctx, span := common.ConsumeSpan(ctx, tr, "validate", rec)

			out, topic, reason := process(rec.Value, cfg, tickers)
			span.SetAttributes(
				attribute.String("event.key", string(rec.Key)),
				attribute.String("dest.topic", topic),
			)
			if topic == cfg.topicDeadletter {
				rejected++
				span.SetAttributes(attribute.String("reject.reason", reason))
				log.Warn("rejected", "reason", reason, "key", string(rec.Key))
			} else {
				validated++
			}

			outRec := &kgo.Record{Topic: topic, Key: rec.Key, Value: out}
			common.Inject(cctx, outRec) // carry the trace onward
			perr := cl.ProduceSync(cctx, outRec).FirstErr()
			span.End()
			if perr != nil {
				log.Error("produce — not committing, will retry", "err", perr)
				produceErr = true
				break
			}
		}

		if produceErr {
			continue
		}
		if err := cl.CommitUncommittedOffsets(ctx); err != nil {
			log.Error("commit", "err", err)
		}
		if validated+rejected > 0 {
			log.Info("batch", "validated", validated, "rejected", rejected)
		}
	}
}

// process returns (outBytes, destTopic, rejectReason).
func process(raw []byte, cfg config, tickers tickerMap) ([]byte, string, string) {
	var ev Event
	if err := json.Unmarshal(raw, &ev); err != nil {
		// unparseable — cannot even build a proper envelope; wrap the bytes
		dl := map[string]any{
			"reject_reason": "schema: not valid json (" + err.Error() + ")",
			"rejected_at":   nowRFC3339(),
			"raw_bytes":     string(raw),
		}
		b, _ := json.Marshal(dl)
		return b, cfg.topicDeadletter, "not-json"
	}

	if reason := hardChecks(ev, cfg); reason != "" {
		ev.RejectReason = reason
		ev.RejectedAt = nowRFC3339()
		b, _ := json.Marshal(ev)
		return b, cfg.topicDeadletter, reason
	}

	if ev.Ticker == "" {
		ev.Ticker = tickers.resolve(ev.CIK) // best-effort; empty is allowed
	}
	b, _ := json.Marshal(ev)
	return b, cfg.topicValidated, ""
}

func hardChecks(ev Event, cfg config) string {
	if strings.TrimSpace(ev.EventKey) == "" {
		return "schema: missing event_key"
	}
	if strings.TrimSpace(ev.Source) == "" {
		return "schema: missing source"
	}
	if len(ev.Raw) == 0 || string(ev.Raw) == "null" {
		return "schema: missing raw provenance"
	}
	// freshness — only when we have a parseable timestamp
	if ev.PublishedAt != "" {
		if t, ok := parseTime(ev.PublishedAt); ok {
			age := time.Since(t)
			if age > time.Duration(cfg.freshnessDays)*24*time.Hour {
				return "stale: published_at " + t.Format("2006-01-02") +
					" older than " + strconv.Itoa(cfg.freshnessDays) + "d"
			}
			if age < -24*time.Hour {
				return "future: published_at " + t.Format(time.RFC3339) + " is in the future"
			}
		}
	}
	return ""
}

func parseTime(s string) (time.Time, bool) {
	for _, l := range []string{time.RFC3339, "2006-01-02T15:04:05Z", "2006-01-02"} {
		if t, err := time.Parse(l, s); err == nil {
			return t, true
		}
	}
	return time.Time{}, false
}

func nowRFC3339() string { return time.Now().UTC().Format(time.RFC3339) }

func env(k, def string) string {
	if v := os.Getenv(k); v != "" {
		return v
	}
	return def
}
func envInt(k string, def int) int {
	if v := os.Getenv(k); v != "" {
		if n, err := strconv.Atoi(v); err == nil {
			return n
		}
	}
	return def
}
