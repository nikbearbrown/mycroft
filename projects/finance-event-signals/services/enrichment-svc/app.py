"""enrichment-svc — Week 2: LangGraph agent. Week 3: OTel traces + metrics.

Consumes events.validated, runs each event through the graph
(classify -> extract -> self-consistency -> verify -> emit | withhold),
attaches the resulting `signal`, produces events.enriched. The trace context is
carried in the Kafka record headers so one accession = one trace across services.
Nothing here decides or acts — a human clears the gate downstream.
"""

import json
import os
import signal
import sys
import time
from datetime import datetime, timezone

from confluent_kafka import Consumer, Producer
from opentelemetry import trace

from graph import build_graph
from llm import make_llm
from obs import ctx_from_headers, headers_from_ctx, init as init_otel

BROKERS = os.getenv("KAFKA_BROKERS", "redpanda:9092")
TOPIC_IN = os.getenv("TOPIC_IN", "events.validated")
TOPIC_OUT = os.getenv("TOPIC_OUT", "events.enriched")
GROUP_ID = os.getenv("GROUP_ID", "enrichment-svc")

_running = True


def log(**kw):
    print(json.dumps({"ts": datetime.now(timezone.utc).isoformat(), **kw}), flush=True)


def _stop(*_):
    global _running
    _running = False


def main():
    signal.signal(signal.SIGINT, _stop)
    signal.signal(signal.SIGTERM, _stop)

    tracer, meter = init_otel()
    dur_ms = meter.create_histogram("enrichment.graph.duration_ms", unit="ms")
    sig_ctr = meter.create_counter("enrichment.signals")

    llm = make_llm()
    graph = build_graph(llm)

    consumer = Consumer(
        {
            "bootstrap.servers": BROKERS,
            "group.id": GROUP_ID,
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
        }
    )
    producer = Producer({"bootstrap.servers": BROKERS, "acks": "all", "linger.ms": 50})
    consumer.subscribe([TOPIC_IN])

    log(event="started", topic_in=TOPIC_IN, topic_out=TOPIC_OUT, group=GROUP_ID, llm=llm.provider)

    emitted, withheld, errors = 0, 0, 0
    while _running:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            log(event="consume_error", error=str(msg.error()))
            continue

        parent = ctx_from_headers(msg.headers())
        with tracer.start_as_current_span(
            "enrich", context=parent, kind=trace.SpanKind.CONSUMER
        ) as span:
            try:
                ev = json.loads(msg.value())
            except Exception as e:
                errors += 1
                span.record_exception(e)
                log(event="bad_json", error=str(e), offset=msg.offset())
                consumer.commit(msg)
                continue

            t0 = time.perf_counter()
            try:
                result = graph.invoke({"event": ev})
                ev["event_type"] = result.get("event_type")
                ev["signal"] = result["signal"]
            except Exception as e:
                errors += 1
                ev["event_type"] = None
                ev["signal"] = {"status": "withheld", "withheld_reason": f"agent error: {e}"}
                span.record_exception(e)
                log(event="agent_error", error=str(e), key=ev.get("event_key"))

            elapsed = (time.perf_counter() - t0) * 1000
            status = ev["signal"]["status"]
            dur_ms.record(elapsed, {"llm": llm.provider})
            sig_ctr.add(1, {"status": status, "event_type": ev.get("event_type") or "none"})
            span.set_attribute("event.key", ev.get("event_key") or "")
            span.set_attribute("event.type", ev.get("event_type") or "none")
            span.set_attribute("signal.status", status)
            if status == "withheld":
                withheld += 1
                span.set_attribute("withheld.reason", ev["signal"].get("withheld_reason", ""))
            else:
                emitted += 1
                span.set_attribute("signal.direction", ev["signal"].get("direction", ""))

            producer.produce(
                TOPIC_OUT,
                key=(ev.get("event_key") or "").encode(),
                value=json.dumps(ev).encode(),
                headers=headers_from_ctx(),  # carry the trace onward
            )
            producer.poll(0)
            consumer.commit(msg)

        if (emitted + withheld) % 25 == 0:
            log(event="progress", emitted=emitted, withheld=withheld, errors=errors)

    log(event="draining", emitted=emitted, withheld=withheld, errors=errors)
    producer.flush(10)
    consumer.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
