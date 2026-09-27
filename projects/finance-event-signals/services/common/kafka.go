package common

import (
	"context"

	"github.com/twmb/franz-go/pkg/kgo"
	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/trace"
)

// recordCarrier is a TextMapCarrier over a kgo.Record's headers — this is how the
// trace context crosses the Kafka topic boundary so gateway -> validation ->
// enrichment -> persistence is ONE trace.
type recordCarrier struct{ rec *kgo.Record }

func (c recordCarrier) Get(key string) string {
	for _, h := range c.rec.Headers {
		if h.Key == key {
			return string(h.Value)
		}
	}
	return ""
}

func (c recordCarrier) Set(key, val string) {
	for i := range c.rec.Headers {
		if c.rec.Headers[i].Key == key {
			c.rec.Headers[i].Value = []byte(val)
			return
		}
	}
	c.rec.Headers = append(c.rec.Headers, kgo.RecordHeader{Key: key, Value: []byte(val)})
}

func (c recordCarrier) Keys() []string {
	ks := make([]string, len(c.rec.Headers))
	for i, h := range c.rec.Headers {
		ks[i] = h.Key
	}
	return ks
}

// ProduceSpan starts a producer span and injects the context into rec.Headers.
// Call span.End() after the produce completes.
func ProduceSpan(ctx context.Context, tr trace.Tracer, name string, rec *kgo.Record) (context.Context, trace.Span) {
	ctx, span := tr.Start(ctx, name, trace.WithSpanKind(trace.SpanKindProducer))
	otel.GetTextMapPropagator().Inject(ctx, recordCarrier{rec})
	return ctx, span
}

// ConsumeSpan extracts the parent context from rec.Headers and starts a consumer
// span linked to the producer's trace.
func ConsumeSpan(ctx context.Context, tr trace.Tracer, name string, rec *kgo.Record) (context.Context, trace.Span) {
	ctx = otel.GetTextMapPropagator().Extract(ctx, recordCarrier{rec})
	return tr.Start(ctx, name, trace.WithSpanKind(trace.SpanKindConsumer))
}

// Inject writes the trace context of ctx into rec.Headers (no span) — for a
// transform service that consumes one record and produces another.
func Inject(ctx context.Context, rec *kgo.Record) {
	otel.GetTextMapPropagator().Inject(ctx, recordCarrier{rec})
}
