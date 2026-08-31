"""OTel setup for enrichment-svc. No-op if OTEL_EXPORTER_OTLP_ENDPOINT is unset."""

import os

from opentelemetry import metrics, propagate, trace
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

SERVICE = "enrichment-svc"


def init():
    if not os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"):
        return trace.get_tracer(SERVICE), metrics.get_meter(SERVICE)

    res = Resource.create({"service.name": SERVICE})

    tp = TracerProvider(resource=res)
    tp.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(insecure=True)))
    trace.set_tracer_provider(tp)

    mp = MeterProvider(
        resource=res,
        metric_readers=[PeriodicExportingMetricReader(OTLPMetricExporter(insecure=True))],
    )
    metrics.set_meter_provider(mp)

    return trace.get_tracer(SERVICE), metrics.get_meter(SERVICE)


def ctx_from_headers(headers):
    carrier = {k: (v.decode() if isinstance(v, bytes) else v) for k, v in (headers or [])}
    return propagate.extract(carrier)


def headers_from_ctx():
    carrier: dict = {}
    propagate.inject(carrier)
    return [(k, v.encode()) for k, v in carrier.items()]
