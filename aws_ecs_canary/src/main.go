package main

import (
	"fmt"
	"net/http"
	"os"
)

func main() {
    appName := os.Getenv("APP_NAME")
    http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
        fmt.Fprintf(w, "APP_NAME: %s", appName)
    })
    http.ListenAndServe(":8080", nil)
}
