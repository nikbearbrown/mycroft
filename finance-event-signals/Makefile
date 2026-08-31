SHELL := /bin/sh
COMPOSE := docker compose -f deploy/docker-compose.yml --env-file .env

.PHONY: help up down logs ps psql topics deadletter rebuild clean proto tidy test signals verify report clear grade scorecard k8s-sync

help:
	@echo "make up         - start the full stack"
	@echo "make down       - stop everything (keep data)"
	@echo "make clean      - down + remove volumes"
	@echo "make rebuild    - rebuild images and restart"
	@echo "make logs       - tail all service logs"
	@echo "make ps         - container status"
	@echo "make psql       - psql on the events db"
	@echo "make topics     - list kafka topics"
	@echo "make deadletter - dump events.deadletter with reasons"
	@echo "make proto      - regenerate Go stubs from proto/fes/v1/*.proto (buf, via docker)"
	@echo "make tidy       - 'go mod tidy' for every Go module via docker (no local Go needed)"

up:
	$(COMPOSE) up -d --build

down:
	$(COMPOSE) down

rebuild:
	$(COMPOSE) up -d --build --force-recreate

logs:
	$(COMPOSE) logs -f --tail=100

ps:
	$(COMPOSE) ps

psql:
	$(COMPOSE) exec postgres psql -U fes -d fes

topics:
	$(COMPOSE) exec redpanda rpk topic list

deadletter:
	$(COMPOSE) exec redpanda rpk topic consume events.deadletter -o :end -f '%v\n' || true

proto:
	docker run --rm -v "$(CURDIR):/w" -w /w/proto bufbuild/buf:1.45.0 generate

test:
	docker run --rm -v "$(CURDIR)/services/enrichment-svc:/app" -w /app \
	  python:3.12-slim sh -c "pip -q install langgraph==0.2.45 >/dev/null && python test_graph.py"

# machine half of P4 — deterministic checks, halts on failure
verify:
	docker run --rm -v "$(CURDIR):/w" -w /w python:3.12-slim \
	  sh -c "pip -q install pyyaml >/dev/null && python scripts/conformance.py"
	docker run --rm -v "$(CURDIR):/w" -w /w/proto bufbuild/buf:1.45.0 lint

# human report (P5) — needs the stack up
report:
	python scripts/run_report.py

# Week 4: grade actionable signals against realized price moves (one-shot Job in k8s)
grade:
	kubectl -n fes delete job outcome-grader-run --ignore-not-found
	kubectl apply -f deploy/k8s/grader-job.yaml
	kubectl -n fes wait --for=condition=complete job/outcome-grader-run --timeout=120s
	kubectl -n fes logs job/outcome-grader-run

scorecard:
	python scripts/scorecard.py

# copy otel/ + deploy/postgres/ configs into deploy/k8s/_config/ (kustomize can't
# read outside its own tree); `make verify` fails if these drift from source
k8s-sync:
	cp otel/collector-config.yaml otel/prometheus.yml otel/grafana-datasources.yaml deploy/k8s/_config/
	cp deploy/postgres/*.sql deploy/k8s/_config/

signals:
	@curl -s "http://localhost:18080/v1/signals?status=$(STATUS)&limit=20" | python -m json.tool

# clear a signal:  make clear SIG=sig_... WHO=alice VERDICT=actionable
clear:
	curl -s -X POST "http://localhost:18080/v1/signals/$(SIG)/clear" \
	  -H 'content-type: application/json' \
	  -d '{"reviewer":"$(WHO)","verdict":"$(VERDICT)","note":"$(NOTE)"}' | python -m json.tool

tidy:
	for m in proto services/ingest-gateway services/persistence-svc services/validation-svc services/query-api; do \
	  echo "== tidy $$m =="; \
	  docker run --rm -v "$(CURDIR)/$$m:/app" -v "$(CURDIR)/proto:/proto" -w /app golang:1.23 go mod tidy; \
	done

clean:
	$(COMPOSE) down -v
