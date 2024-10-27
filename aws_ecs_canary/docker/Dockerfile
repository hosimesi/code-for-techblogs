FROM golang:1.23-alpine3.19 AS builder

WORKDIR /app
COPY go.mod ./
RUN go mod download
COPY src/main.go ./
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -ldflags="-s -w" -o main main.go

# ランタイムステージ
FROM alpine:3.19
WORKDIR /app
COPY --from=builder /app/main .
USER 1001
CMD ["/app/main"]
