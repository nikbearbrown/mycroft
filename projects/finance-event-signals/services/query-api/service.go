package main

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"log/slog"
	"time"

	fesv1 "github.com/finance-event-signals/proto/gen/fes/v1"
	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/redis/go-redis/v9"
	"github.com/finance-event-signals/common"
	"github.com/twmb/franz-go/pkg/kgo"
	"go.opentelemetry.io/otel/attribute"
	"go.opentelemetry.io/otel/trace"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
)

type queryServer struct {
	pool            *pgxpool.Pool
	rdb             *redis.Client
	prod            *kgo.Client
	actionableTopic string
	log             *slog.Logger
	tr              trace.Tracer
}

const selectSignal = `
SELECT signal_id, status, COALESCE(event_type,''), COALESCE(direction,''),
       COALESCE(magnitude,''), COALESCE(confidence,0), COALESCE(rationale,''),
       COALESCE(withheld_reason,''), event_key, COALESCE(ticker,''), COALESCE(company,''),
       COALESCE(title,''), COALESCE(url,''),
       COALESCE(to_char(published_at,'YYYY-MM-DD"T"HH24:MI:SS"Z"'),''),
       to_char(created_at,'YYYY-MM-DD"T"HH24:MI:SS"Z"')
FROM signal_review`

func scanSignal(row pgx.Row) (*fesv1.Signal, error) {
	var s fesv1.Signal
	err := row.Scan(&s.SignalId, &s.Status, &s.EventType, &s.Direction, &s.Magnitude,
		&s.Confidence, &s.Rationale, &s.WithheldReason, &s.EventKey, &s.Ticker,
		&s.Company, &s.Title, &s.Url, &s.PublishedAt, &s.CreatedAt)
	if err != nil {
		return nil, err
	}
	return &s, nil
}

func (q *queryServer) ListSignals(ctx context.Context, req *fesv1.ListSignalsRequest) (*fesv1.ListSignalsResponse, error) {
	limit := int32(50)
	if req.Limit > 0 && req.Limit <= 500 {
		limit = req.Limit
	}
	cacheKey := fmt.Sprintf("signals:%s:%d", req.Status, limit)
	if b, err := q.rdb.Get(ctx, cacheKey).Bytes(); err == nil {
		var resp fesv1.ListSignalsResponse
		var rows []*fesv1.Signal
		if json.Unmarshal(b, &rows) == nil {
			resp.Signals = rows
			return &resp, nil
		}
	}

	sql := selectSignal + `
WHERE ($1 = '' OR status = $1)
ORDER BY created_at DESC
LIMIT $2`
	rs, err := q.pool.Query(ctx, sql, req.Status, limit)
	if err != nil {
		return nil, status.Errorf(codes.Internal, "query: %v", err)
	}
	defer rs.Close()

	var out []*fesv1.Signal
	for rs.Next() {
		s, err := scanSignal(rs)
		if err != nil {
			return nil, status.Errorf(codes.Internal, "scan: %v", err)
		}
		out = append(out, s)
	}
	if b, err := json.Marshal(out); err == nil {
		q.rdb.Set(ctx, cacheKey, b, 10*time.Second)
	}
	return &fesv1.ListSignalsResponse{Signals: out}, nil
}

func (q *queryServer) GetSignal(ctx context.Context, req *fesv1.GetSignalRequest) (*fesv1.Signal, error) {
	if req.SignalId == "" {
		return nil, status.Error(codes.InvalidArgument, "signal_id required")
	}
	s, err := scanSignal(q.pool.QueryRow(ctx, selectSignal+` WHERE signal_id = $1`, req.SignalId))
	if errors.Is(err, pgx.ErrNoRows) {
		return nil, status.Error(codes.NotFound, "no such signal")
	}
	if err != nil {
		return nil, status.Errorf(codes.Internal, "%v", err)
	}
	return s, nil
}

// ClearGate is THE phase gate. It writes a gate_decisions row and, only for an
// "actionable" verdict, publishes the enriched event to events.actionable.
// Nothing else in the system produces to that topic.
func (q *queryServer) ClearGate(ctx context.Context, req *fesv1.ClearGateRequest) (*fesv1.ClearGateResponse, error) {
	ctx, span := q.tr.Start(ctx, "ClearGate")
	defer span.End()
	span.SetAttributes(
		attribute.String("signal.id", req.SignalId),
		attribute.String("gate.reviewer", req.Reviewer),
		attribute.String("gate.verdict", req.Verdict),
	)

	if req.Reviewer == "" {
		return nil, status.Error(codes.InvalidArgument, "reviewer required — the gate needs a named human")
	}
	if req.Verdict != "actionable" && req.Verdict != "reject" {
		return nil, status.Error(codes.InvalidArgument, `verdict must be "actionable" or "reject"`)
	}

	tx, err := q.pool.Begin(ctx)
	if err != nil {
		return nil, status.Errorf(codes.Internal, "begin: %v", err)
	}
	defer tx.Rollback(ctx)

	var curStatus, eventKey string
	err = tx.QueryRow(ctx,
		`SELECT s.status, s.event_key FROM signals s WHERE s.signal_id = $1 FOR UPDATE`,
		req.SignalId).Scan(&curStatus, &eventKey)
	if errors.Is(err, pgx.ErrNoRows) {
		return nil, status.Error(codes.NotFound, "no such signal")
	}
	if err != nil {
		return nil, status.Errorf(codes.Internal, "lookup: %v", err)
	}
	if curStatus != "pending_review" && curStatus != "withheld" {
		return nil, status.Errorf(codes.FailedPrecondition,
			"signal already decided (status=%s)", curStatus)
	}

	newStatus := "rejected"
	if req.Verdict == "actionable" {
		newStatus = "actionable"
	}

	ct, err := tx.Exec(ctx,
		`INSERT INTO gate_decisions (signal_id, reviewer, verdict, note)
		 VALUES ($1,$2,$3,$4) ON CONFLICT (signal_id) DO NOTHING`,
		req.SignalId, req.Reviewer, req.Verdict, nullStr(req.Note))
	if err != nil {
		return nil, status.Errorf(codes.Internal, "insert decision: %v", err)
	}
	if ct.RowsAffected() == 0 {
		return nil, status.Error(codes.FailedPrecondition, "a decision already exists for this signal")
	}
	if _, err = tx.Exec(ctx, `UPDATE signals SET status = $2 WHERE signal_id = $1`,
		req.SignalId, newStatus); err != nil {
		return nil, status.Errorf(codes.Internal, "update signal: %v", err)
	}

	var rawEnvelope []byte
	if err = tx.QueryRow(ctx, `SELECT raw FROM events WHERE event_key = $1`, eventKey).
		Scan(&rawEnvelope); err != nil {
		return nil, status.Errorf(codes.Internal, "load envelope: %v", err)
	}
	if err = tx.Commit(ctx); err != nil {
		return nil, status.Errorf(codes.Internal, "commit: %v", err)
	}

	// only after the decision row is committed do we publish
	if req.Verdict == "actionable" {
		rec := &kgo.Record{Topic: q.actionableTopic, Key: []byte(eventKey), Value: rawEnvelope}
		pctx, pspan := common.ProduceSpan(ctx, q.tr, "produce events.actionable", rec)
		pspan.SetAttributes(attribute.String("event.key", eventKey))
		if perr := q.prod.ProduceSync(pctx, rec).FirstErr(); perr != nil {
			pspan.RecordError(perr)
			q.log.Error("actionable produce failed (decision stands; retry publish)",
				"err", perr, "signal", req.SignalId)
		}
		pspan.End()
	}
	q.rdb.FlushDB(ctx) // small dataset; simplest cache invalidation

	sig, err := q.GetSignal(ctx, &fesv1.GetSignalRequest{SignalId: req.SignalId})
	if err != nil {
		return nil, err
	}
	return &fesv1.ClearGateResponse{
		Signal: sig,
		Decision: &fesv1.GateDecision{
			SignalId: req.SignalId, Reviewer: req.Reviewer,
			Verdict: req.Verdict, Note: req.Note,
			DecidedAt: time.Now().UTC().Format(time.RFC3339),
		},
	}, nil
}

func nullStr(s string) *string {
	if s == "" {
		return nil
	}
	return &s
}
