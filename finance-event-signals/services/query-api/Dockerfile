# build context = repo root (see docker-compose.yml) so ../../proto and ../common resolve.
FROM golang:1.23-alpine AS build
WORKDIR /src
COPY proto ./proto
COPY services/common ./services/common
COPY services/query-api ./services/query-api
WORKDIR /src/services/query-api
RUN go mod download
RUN CGO_ENABLED=0 go build -trimpath -o /out/query-api .

FROM alpine:3.20
RUN apk add --no-cache ca-certificates && adduser -D -u 10001 app
USER app
COPY --from=build /out/query-api /usr/local/bin/query-api
ENTRYPOINT ["/usr/local/bin/query-api"]
