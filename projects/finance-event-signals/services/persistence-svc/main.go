// persistence-svc — writes the verified store. Consumes events.enriched, and in one
// transaction upserts the event row and its signal row (idempotent: signal_id is
// deterministic, both inserts are ON CONFLICT DO NOTHING). Never commits a Kafka
// batch past a failed DB write.
package main

import (
	"context"
	"encoding/json"
	"log/slog"
	"os"
	"os/signal"
	"strings"
	"syscall"
	"time"

	"github.com/finance-event-signals/common"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/twmb/franz-go/pkg/kgo"
	"go.opentelemetry.io/otel/attribute"
	"go.opentelemetry.io/otel/codes"
)

type Signal struct {
	Status         string   `json:"status"`
	EventType      string   `json:"event_type"`
	Direction      string   `json:"direction"`
	Magnitude      string   `json:"magnitude"`
	Confidence     *float64 `json:"confidence"`
	Rationale      string   `json:"rationale"`
	WithheldReason string   `json:"withheld_reason"`
}

type Event struct {
	EventKey    string  `json:"event_key"`
	Source      string  `json:"source"`
	Form        string  `json:"form"`
	EventType   *string `json:"event_type"`
	Ticker      string  `json:"ticker"`
	CIK         string  `json:"cik"`
	Company     string  `json:"company"`
	Title       string  `json:"title"`
	URL         string  `json:"url"`
	PublishedAt string  `json:"published_at"`
	FetchedAt   string  `json:"fetched_at"`
	Signal      *Signal `json:"signal"`
}

const insertEventSQL = `
INSERT INTO events
  (event_key, source, form, event_type, ticker, cik, company, title, url,
   published_at, fetched_at, signal_status, raw)
VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13)
ON CONFLICT (event_key) DO UPDATE
  SET ticker     = COALESCE(EXCLUDED.ticker, events.ticker),
      event_type = COALESCE(EXCLUDED.event_type, events.event_type),
      signal_status = EXCLUDED.signal_status`

const insertSignalSQL = `
INSERT INTO signals
  (signal_id, event_key, status, event_type, direction, magnitude, confidence,
   rationale, withheld_reason)
VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9)
ON CONFLICT (signal_id) DO NOTHING`

func main() {
	log := slog.New(slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{Level: slog.LevelInfo}))

	brokers := strings.Split(env("KAFKA_BROKERS", "redpanda:9092"), ",")
	topicIn := env("TOPIC_IN", "events.enriched")
	groupID := env("GROUP_ID", "persistence-svc")
	dsn := env("POSTGRES_DSN", "postgres://fes:fes@postgres:5432/fes?sslmode=disable")

	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer stop()

	shutdown, err := common.Init(ctx, "persistence-svc")
	if err != nil {
		log.Error("otel init", "err", err)
	}
	defer func() { _ = shutdown(context.Background()) }()
	tr := common.Tracer("persistence-svc")

	pool, err := pgxpool.New(ctx, dsn)
	if err != nil {
		log.Error("pg pool", "err", err)
		os.Exit(1)
	}
	defer pool.Close()
	if err := waitForPG(ctx, pool, log); err != nil {
		log.Error("pg not ready", "err", err)
		os.Exit(1)
	}

	cl, err := kgo.NewClient(
		kgo.SeedBrokers(brokers...),
		kgo.ConsumerGroup(groupID),
		kgo.ConsumeTopics(topicIn),
		kgo.DisableAutoCommit(),
	)
	if err != nil {
		log.Error("kafka client", "err", err)
		os.Exit(1)
	}
	defer cl.Close()

	log.Info("persistence-svc started", "topic", topicIn, "group", groupID)

	for {
		fetches := cl.PollFetches(ctx)
		if fetches.IsClientClosed() || ctx.Err() != nil {
			log.Info("shutting down")
			return
		}
		fetches.EachError(func(t string, p int32, err error) {
			log.Error("fetch error", "topic", t, "partition", p, "err", err)
		})

		insE, insS, skip, fail := 0, 0, 0, 0
		batchOK := true
		iter := fetches.RecordIter()
		for !iter.Done() {
			rec := iter.Next()
			cctx, span := common.ConsumeSpan(ctx, tr, "persist", rec)
			span.SetAttributes(attribute.String("event.key", string(rec.Key)))
			ne, ns, err := upsert(cctx, pool, rec.Value)
			if err != nil {
				span.RecordError(err)
				span.SetStatus(codes.Error, "upsert failed")
				span.End()
				log.Error("upsert", "err", err, "offset", rec.Offset)
				fail++
				batchOK = false
				break
			}
			span.SetAttributes(
				attribute.Int("events.inserted", ne),
				attribute.Int("signals.inserted", ns),
			)
			span.End()
			insE += ne
			insS += ns
			if ne == 0 {
				skip++
			}
		}

		if batchOK {
			if err := cl.CommitUncommittedOffsets(ctx); err != nil {
				log.Error("commit", "err", err)
			}
		}
		if insE+insS+skip+fail > 0 {
			log.Info("batch", "events_inserted", insE, "signals_inserted", insS,
				"events_skipped_dupe", skip, "failed", fail, "committed", batchOK)
		}
	}
}

func upsert(ctx context.Context, pool *pgxpool.Pool, raw []byte) (nEvent, nSignal int, err error) {
	var ev Event
	if err = json.Unmarshal(raw, &ev); err != nil {
		return 0, 0, err
	}

	tx, err := pool.Begin(ctx)
	if err != nil {
		return 0, 0, err
	}
	defer tx.Rollback(ctx)

	sigStatus := ""
	if ev.Signal != nil {
		sigStatus = ev.Signal.Status
	}
	tag, err := tx.Exec(ctx, insertEventSQL,
		ev.EventKey, ev.Source, nullStr(ev.Form), ev.EventType, nullStr(ev.Ticker),
		nullStr(ev.CIK), nullStr(ev.Company), nullStr(ev.Title), nullStr(ev.URL),
		parseTime(ev.PublishedAt), parseTime(ev.FetchedAt), nullStr(sigStatus), raw,
	)
	if err != nil {
		return 0, 0, err
	}
	nEvent = int(tag.RowsAffected())

	if ev.Signal != nil {
		s := ev.Signal
		et := firstNonEmpty(s.EventType, deref(ev.EventType))
		tag, err = tx.Exec(ctx, insertSignalSQL,
			"sig_"+ev.EventKey, ev.EventKey, s.Status, nullStr(et),
			nullStr(s.Direction), nullStr(s.Magnitude), s.Confidence,
			nullStr(s.Rationale), nullStr(s.WithheldReason),
		)
		if err != nil {
			return 0, 0, err
		}
		nSignal = int(tag.RowsAffected())
	}

	return nEvent, nSignal, tx.Commit(ctx)
}

func parseTime(s string) *time.Time {
	if s == "" {
		return nil
	}
	for _, l := range []string{time.RFC3339, "2006-01-02T15:04:05Z", "2006-01-02"} {
		if t, e := time.Parse(l, s); e == nil {
			return &t
		}
	}
	return nil
}
func nullStr(s string) *string {
	if s == "" {
		return nil
	}
	return &s
}
func deref(p *string) string {
	if p == nil {
		return ""
	}
	return *p
}
func firstNonEmpty(a, b string) string {
	if a != "" {
		return a
	}
	return b
}

func waitForPG(ctx context.Context, pool *pgxpool.Pool, log *slog.Logger) error {
	deadline := time.Now().Add(45 * time.Second)
	for {
		if err := pool.Ping(ctx); err == nil {
			return nil
		}
		if time.Now().After(deadline) || ctx.Err() != nil {
			return pool.Ping(ctx)
		}
		log.Info("waiting for postgres…")
		time.Sleep(2 * time.Second)
	}
}

func env(k, def string) string {
	if v := os.Getenv(k); v != "" {
		return v
	}
	return def
}
