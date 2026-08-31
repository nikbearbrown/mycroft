package main

import (
	"encoding/json"
	"net/http"
	"strconv"
	"strings"

	fesv1 "github.com/finance-event-signals/proto/gen/fes/v1"
	"google.golang.org/grpc/status"
)

// A thin JSON front for the same queryServer methods. grpc-gateway codegen is
// Week 3 polish; this proves the REST surface now.
func restMux(q *queryServer) http.Handler {
	mux := http.NewServeMux()

	mux.HandleFunc("GET /healthz", func(w http.ResponseWriter, r *http.Request) {
		if err := q.pool.Ping(r.Context()); err != nil {
			http.Error(w, "db down", http.StatusServiceUnavailable)
			return
		}
		w.Write([]byte("ok"))
	})

	mux.HandleFunc("GET /v1/signals", func(w http.ResponseWriter, r *http.Request) {
		limit, _ := strconv.Atoi(r.URL.Query().Get("limit"))
		resp, err := q.ListSignals(r.Context(), &fesv1.ListSignalsRequest{
			Status: r.URL.Query().Get("status"), Limit: int32(limit),
		})
		writeResult(w, resp, err)
	})

	mux.HandleFunc("GET /v1/signals/{id}", func(w http.ResponseWriter, r *http.Request) {
		s, err := q.GetSignal(r.Context(), &fesv1.GetSignalRequest{SignalId: r.PathValue("id")})
		writeResult(w, s, err)
	})

	mux.HandleFunc("POST /v1/signals/{id}/clear", func(w http.ResponseWriter, r *http.Request) {
		var body struct {
			Reviewer string `json:"reviewer"`
			Verdict  string `json:"verdict"`
			Note     string `json:"note"`
		}
		if err := json.NewDecoder(r.Body).Decode(&body); err != nil {
			http.Error(w, `{"error":"bad json body"}`, http.StatusBadRequest)
			return
		}
		resp, err := q.ClearGate(r.Context(), &fesv1.ClearGateRequest{
			SignalId: r.PathValue("id"), Reviewer: body.Reviewer,
			Verdict: body.Verdict, Note: body.Note,
		})
		writeResult(w, resp, err)
	})

	return withJSON(mux)
}

func withJSON(h http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		h.ServeHTTP(w, r)
	})
}

func writeResult(w http.ResponseWriter, v any, err error) {
	if err != nil {
		code := http.StatusInternalServerError
		if st, ok := status.FromError(err); ok {
			code = httpCode(st.Code().String())
		}
		w.WriteHeader(code)
		json.NewEncoder(w).Encode(map[string]string{"error": err.Error()})
		return
	}
	json.NewEncoder(w).Encode(v)
}

func httpCode(grpcCode string) int {
	switch strings.ToLower(grpcCode) {
	case "invalidargument":
		return http.StatusBadRequest
	case "notfound":
		return http.StatusNotFound
	case "failedprecondition":
		return http.StatusConflict
	default:
		return http.StatusInternalServerError
	}
}
