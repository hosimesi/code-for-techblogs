FROM golang:1.20-alpine

WORKDIR /app
COPY src/main.go .
RUN go build -o server main.go

ARG RESPONSE_TYPE
ENV RESPONSE_TYPE=${RESPONSE_TYPE}

EXPOSE 8080
CMD ["./server"]
