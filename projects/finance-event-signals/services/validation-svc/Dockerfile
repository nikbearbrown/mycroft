# build context = repo root (see docker-compose.yml) so ../common resolves.
FROM golang:1.23-alpine AS build
WORKDIR /src
COPY services/common ./services/common
COPY services/validation-svc ./services/validation-svc
WORKDIR /src/services/validation-svc
RUN go mod download
RUN CGO_ENABLED=0 go build -trimpath -o /out/validation-svc .

FROM alpine:3.20
RUN apk add --no-cache ca-certificates && adduser -D -u 10001 app
USER app
COPY --from=build /out/validation-svc /usr/local/bin/validation-svc
COPY services/validation-svc/data/company_tickers.json /app/data/company_tickers.json
ENTRYPOINT ["/usr/local/bin/validation-svc"]
