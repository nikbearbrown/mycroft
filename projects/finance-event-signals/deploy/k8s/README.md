# Kubernetes deploy (kind)

Learning cluster — single-replica infra, `emptyDir` storage, images loaded from the
local Docker daemon. Not production.

## Prereqs

- `kind`, `kubectl`
- images built: `make up` once (or `docker compose -f deploy/docker-compose.yml build`)

## Deploy

```bash
# 1. cluster
kind create cluster --name fes

# 2. load the 6 app images the compose build produced
for s in ingest-gateway validation-svc enrichment-svc persistence-svc query-api dashboard; do
  kind load docker-image "finance-event-signals-$s:latest" --name fes
done

# 3. metrics-server (for the HPA), patched for kind's self-signed kubelet cert
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
kubectl -n kube-system patch deploy metrics-server --type=json \
  -p '[{"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--kubelet-insecure-tls"}]'

# 4. apply everything
kubectl apply -k deploy/k8s

# 5. watch it come up
kubectl -n fes get pods -w
```

## Use it

```bash
kubectl -n fes port-forward svc/query-api 18080:8080 &
kubectl -n fes port-forward svc/jaeger    16686:16686 &
kubectl -n fes port-forward svc/grafana   13000:3000 &
kubectl -n fes port-forward svc/dashboard 18501:8501 &
curl -s localhost:18080/v1/signals?status=pending_review | python -m json.tool
```

## Chaos / HPA demo

```bash
# kill the ingest pod — the pipeline keeps draining what's already on the topics
kubectl -n fes delete pod -l app=ingest-gateway
kubectl -n fes get pods -l app=ingest-gateway -w      # it reschedules; no data lost

# drive load: scale the poller lookback up so it re-scans a wide window, or replay
kubectl -n fes set env deploy/ingest-gateway EDGAR_FTS_LOOKBACK_DAYS=5
kubectl -n fes get hpa enrichment-svc -w              # replicas 1 -> 2 -> 3 under CPU
kubectl -n fes set env deploy/ingest-gateway EDGAR_FTS_LOOKBACK_DAYS=1
```

## Validate manifests without a cluster

```bash
kubectl kustomize deploy/k8s | kubectl apply --dry-run=client -f -
```

## Teardown

```bash
kind delete cluster --name fes
```
