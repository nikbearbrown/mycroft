package main

import (
	"context"
	"encoding/json"
	"log/slog"
	"net"
	"os"
	"os/signal"
	"strconv"
	"strings"
	"syscall"
	"time"

	"github.com/finance-event-signals/common"
	fesv1 "github.com/finance-event-signals/proto/gen/fes/v1"
	"github.com/redis/go-redis/v9"
	"github.com/twmb/franz-go/pkg/kgo"
	"go.opentelemetry.io/otel/attribute"
	"go.opentelemetry.io/otel/trace"
	"google.golang.org/grpc"
	"google.golang.org/grpc/reflection"
)

type Config struct {
	UserAgent       string
	PollInterval    time.Duration
	FTSForms        string
	FTSQuery        string
	FTSLookbackDays int
	FTSMaxHits      int
	AtomEnabled     bool
	AtomForms       string
	RatePerSec      float64
	DedupTTL        time.Duration
	KafkaBrokers    []string
	RedisAddr       string
	TopicRaw        string
}

func loadConfig() Config {
	return Config{
		UserAgent:       env("EDGAR_USER_AGENT", "finance-event-signals unknown@example.com"),
		PollInterval:    time.Duration(envInt("POLL_INTERVAL_SECONDS", 60)) * time.Second,
		FTSForms:        env("EDGAR_FTS_FORMS", "8-K"),
		FTSQuery:        env("EDGAR_FTS_QUERY", ""),
		FTSLookbackDays: envInt("EDGAR_FTS_LOOKBACK_DAYS", 1),
		FTSMaxHits:      envInt("EDGAR_FTS_MAX_HITS", 300),
		AtomEnabled:     env("EDGAR_ATOM_ENABLED", "true") == "true",
		AtomForms:       env("EDGAR_ATOM_FORMS", "8-K"),
		RatePerSec:      envFloat("SEC_RATE_LIMIT_PER_SEC", 5),
		DedupTTL:        time.Duration(envInt("DEDUP_TTL_SECONDS", 604800)) * time.Second,
		KafkaBrokers:    strings.Split(env("KAFKA_BROKERS", "redpanda:9092"), ","),
		RedisAddr:       env("REDIS_ADDR", "redis:6379"),
		TopicRaw:        env("TOPIC_RAW", "events.raw"),
	}
}

func main() {
	log := slog.New(slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{Level: slog.LevelInfo}))
	cfg := loadConfig()

	if strings.Contains(cfg.UserAgent, "unknown@example.com") {
		log.Warn("EDGAR_USER_AGENT not set — SEC may return 403. Set it to '<name> <email>'.")
	}

	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer stop()

	shutdown, err := common.Init(ctx, "ingest-gateway")
	if err != nil {
		log.Error("otel init", "err", err)
	}
	defer func() { _ = shutdown(context.Background()) }()

	rdb := redis.NewClient(&redis.Options{Addr: cfg.RedisAddr})
	if err := rdb.Ping(ctx).Err(); err != nil {
		log.Error("redis ping failed", "err", err)
		os.Exit(1)
	}
	defer rdb.Close()

	rl := NewRateLimiter(rdb, "ratelimit:sec", cfg.RatePerSec, cfg.RatePerSec)
	sec := newSECClient(cfg.UserAgent, rl, log)

	kcl, err := kgo.NewClient(
		kgo.SeedBrokers(cfg.KafkaBrokers...),
		kgo.RequiredAcks(kgo.AllISRAcks()),
		kgo.ProducerLinger(50*time.Millisecond),
	)
	if err != nil {
		log.Error("kafka client", "err", err)
		os.Exit(1)
	}
	defer kcl.Close()

	g := &gateway{cfg: cfg, sec: sec, rdb: rdb, kcl: kcl, log: log, tr: common.Tracer("ingest-gateway")}

	// gRPC SubmitEvent (manual / webhook path)
	grpcAddr := env("GRPC_ADDR", ":9091")
	gs := grpc.NewServer()
	fesv1.RegisterIngestServiceServer(gs, &ingestServer{g: g})
	reflection.Register(gs)
	if lis, err := net.Listen("tcp", grpcAddr); err != nil {
		log.Error("grpc listen", "err", err)
	} else {
		go func() {
			log.Info("grpc IngestService listening", "addr", grpcAddr)
			if err := gs.Serve(lis); err != nil {
				log.Error("grpc serve", "err", err)
			}
		}()
		defer gs.GracefulStop()
	}

	log.Info("ingest-gateway started",
		"poll_interval", cfg.PollInterval.String(),
		"fts_forms", cfg.FTSForms, "atom_enabled", cfg.AtomEnabled,
		"rate_per_sec", cfg.RatePerSec)

	g.runCycle(ctx) // once immediately
	ticker := time.NewTicker(cfg.PollInterval)
	defer ticker.Stop()
	for {
		select {
		case <-ctx.Done():
			log.Info("shutting down")
			return
		case <-ticker.C:
			g.runCycle(ctx)
		}
	}
}

type gateway struct {
	cfg Config
	sec *secClient
	rdb *redis.Client
	kcl *kgo.Client
	log *slog.Logger
	tr  trace.Tracer
}

func (g *gateway) runCycle(ctx context.Context) {
	start := time.Now()
	var events []Event

	// Atom first: it is the lower-latency source (a filing appears there minutes
	// before EDGAR full-text search reindexes it). Whichever source publishes an
	// accession first wins the dedup race, so freshly-filed events land as
	// edgar_atom and older ones in the FTS lookback window land as edgar_fts.
	if g.cfg.AtomEnabled {
		atom, err := fetchAtom(ctx, g.sec, g.cfg, g.log)
		if err != nil {
			g.log.Error("fetchAtom", "err", err)
		} else {
			events = append(events, atom...)
		}
	}

	fts, err := fetchFTS(ctx, g.sec, g.cfg, g.log)
	if err != nil {
		g.log.Error("fetchFTS", "err", err)
	} else {
		events = append(events, fts...)
	}

	published, dupes, failed := 0, 0, 0
	for _, ev := range events {
		if ctx.Err() != nil {
			break
		}
		fresh, err := g.rdb.SetNX(ctx, "dedup:"+ev.EventKey, "1", g.cfg.DedupTTL).Result()
		if err != nil {
			g.log.Error("dedup setnx", "err", err, "key", ev.EventKey)
			failed++
			continue
		}
		if !fresh {
			dupes++
			continue
		}
		if err := g.produce(ctx, ev); err != nil {
			g.log.Error("produce", "err", err, "key", ev.EventKey)
			// undo the dedup mark so a later cycle retries
			g.rdb.Del(ctx, "dedup:"+ev.EventKey)
			failed++
			continue
		}
		published++
	}

	g.log.Info("cycle complete",
		"fetched", len(events), "published", published,
		"dupes", dupes, "failed", failed,
		"took_ms", time.Since(start).Milliseconds())
}

func (g *gateway) produce(ctx context.Context, ev Event) error {
	val, err := json.Marshal(ev)
	if err != nil {
		return err
	}
	rec := &kgo.Record{Topic: g.cfg.TopicRaw, Key: []byte(ev.EventKey), Value: val}
	pctx, span := common.ProduceSpan(ctx, g.tr, "produce events.raw", rec)
	defer span.End()
	span.SetAttributes(
		attribute.String("event.key", ev.EventKey),
		attribute.String("event.source", ev.Source),
		attribute.String("event.form", ev.Form),
	)
	return g.kcl.ProduceSync(pctx, rec).FirstErr()
}

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
func envFloat(k string, def float64) float64 {
	if v := os.Getenv(k); v != "" {
		if f, err := strconv.ParseFloat(v, 64); err == nil {
			return f
		}
	}
	return def
}
