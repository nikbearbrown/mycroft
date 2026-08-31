// query-api — serves signals over gRPC and REST, and owns ClearGate (the phase gate).
package main

import (
	"context"
	"log/slog"
	"net"
	"net/http"
	"os"
	"os/signal"
	"strings"
	"syscall"
	"time"

	"github.com/finance-event-signals/common"
	fesv1 "github.com/finance-event-signals/proto/gen/fes/v1"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/redis/go-redis/v9"
	"github.com/twmb/franz-go/pkg/kgo"
	"google.golang.org/grpc"
	"google.golang.org/grpc/reflection"
)

func main() {
	log := slog.New(slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{Level: slog.LevelInfo}))

	dsn := env("POSTGRES_DSN", "postgres://fes:fes@postgres:5432/fes?sslmode=disable")
	redisAddr := env("REDIS_ADDR", "redis:6379")
	brokers := strings.Split(env("KAFKA_BROKERS", "redpanda:9092"), ",")
	grpcAddr := env("GRPC_ADDR", ":9090")
	httpAddr := env("HTTP_ADDR", ":8080")
	actionableTopic := env("TOPIC_ACTIONABLE", "events.actionable")

	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer stop()

	shutdown, err := common.Init(ctx, "query-api")
	if err != nil {
		log.Error("otel init", "err", err)
	}
	defer func() { _ = shutdown(context.Background()) }()

	pool, err := pgxpool.New(ctx, dsn)
	if err != nil {
		log.Error("pg pool", "err", err)
		os.Exit(1)
	}
	defer pool.Close()
	for i := 0; i < 30; i++ {
		if pool.Ping(ctx) == nil {
			break
		}
		log.Info("waiting for postgres…")
		time.Sleep(2 * time.Second)
	}

	rdb := redis.NewClient(&redis.Options{Addr: redisAddr})
	defer rdb.Close()

	prod, err := kgo.NewClient(kgo.SeedBrokers(brokers...), kgo.RequiredAcks(kgo.AllISRAcks()))
	if err != nil {
		log.Error("kafka client", "err", err)
		os.Exit(1)
	}
	defer prod.Close()

	srv := &queryServer{
		pool: pool, rdb: rdb, prod: prod,
		actionableTopic: actionableTopic, log: log,
		tr: common.Tracer("query-api"),
	}

	// gRPC
	gs := grpc.NewServer()
	fesv1.RegisterQueryServiceServer(gs, srv)
	reflection.Register(gs)
	lis, err := net.Listen("tcp", grpcAddr)
	if err != nil {
		log.Error("grpc listen", "err", err)
		os.Exit(1)
	}
	go func() {
		log.Info("grpc listening", "addr", grpcAddr)
		if err := gs.Serve(lis); err != nil {
			log.Error("grpc serve", "err", err)
		}
	}()

	// REST
	hs := &http.Server{Addr: httpAddr, Handler: restMux(srv)}
	go func() {
		log.Info("http listening", "addr", httpAddr)
		if err := hs.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Error("http serve", "err", err)
		}
	}()

	<-ctx.Done()
	log.Info("shutting down")
	sctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	hs.Shutdown(sctx)
	gs.GracefulStop()
}

func env(k, def string) string {
	if v := os.Getenv(k); v != "" {
		return v
	}
	return def
}
