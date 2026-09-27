# build context = repo root (see docker-compose.yml) so ../common resolves.
FROM golang:1.23-alpine AS build
WORKDIR /src
COPY services/common ./services/common
COPY services/persistence-svc ./services/persistence-svc
WORKDIR /src/services/persistence-svc
RUN go mod download
RUN CGO_ENABLED=0 go build -trimpath -o /out/persistence-svc .

FROM alpine:3.20
RUN apk add --no-cache ca-certificates && adduser -D -u 10001 app
USER app
COPY --from=build /out/persistence-svc /usr/local/bin/persistence-svc
ENTRYPOINT ["/usr/local/bin/persistence-svc"]
