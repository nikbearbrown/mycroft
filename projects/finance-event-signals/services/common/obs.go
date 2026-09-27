// Package common is the shared observability layer: OTel tracer/meter setup and
// trace-context propagation over Kafka record headers.
package common

import (
	"context"
	"os"

	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/exporters/otlp/otlpmetric/otlpmetricgrpc"
	"go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracegrpc"
	"go.opentelemetry.io/otel/propagation"
	sdkmetric "go.opentelemetry.io/otel/sdk/metric"
	"go.opentelemetry.io/otel/sdk/resource"
	sdktrace "go.opentelemetry.io/otel/sdk/trace"
	semconv "go.opentelemetry.io/otel/semconv/v1.26.0"
	"go.opentelemetry.io/otel/trace"
)

// Init wires OTLP/gRPC trace + metric exporters (endpoint from
// OTEL_EXPORTER_OTLP_ENDPOINT). If the endpoint is unset, tracing/metrics are
// no-ops and the service still runs. Returns a shutdown func.
func Init(ctx context.Context, service string) (func(context.Context) error, error) {
	if os.Getenv("OTEL_EXPORTER_OTLP_ENDPOINT") == "" {
		otel.SetTextMapPropagator(propagation.TraceContext{})
		return func(context.Context) error { return nil }, nil
	}

	res, err := resource.New(ctx, resource.WithAttributes(semconv.ServiceName(service)))
	if err != nil {
		return nil, err
	}

	texp, err := otlptracegrpc.New(ctx, otlptracegrpc.WithInsecure())
	if err != nil {
		return nil, err
	}
	tp := sdktrace.NewTracerProvider(
		sdktrace.WithBatcher(texp),
		sdktrace.WithResource(res),
	)
	otel.SetTracerProvider(tp)

	mexp, err := otlpmetricgrpc.New(ctx, otlpmetricgrpc.WithInsecure())
	if err != nil {
		return nil, err
	}
	mp := sdkmetric.NewMeterProvider(
		sdkmetric.WithReader(sdkmetric.NewPeriodicReader(mexp)),
		sdkmetric.WithResource(res),
	)
	otel.SetMeterProvider(mp)

	otel.SetTextMapPropagator(propagation.NewCompositeTextMapPropagator(
		propagation.TraceContext{}, propagation.Baggage{},
	))

	return func(c context.Context) error {
		_ = tp.Shutdown(c)
		return mp.Shutdown(c)
	}, nil
}

// Tracer is a convenience getter.
func Tracer(name string) trace.Tracer { return otel.Tracer(name) }
