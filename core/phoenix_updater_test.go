package core

import (
	"io"
	"net/http"
	"strings"
	"testing"
)

type phoenixUpdateTransport func(*http.Request) (*http.Response, error)

func (f phoenixUpdateTransport) RoundTrip(r *http.Request) (*http.Response, error) { return f(r) }

func TestPhoenixUpdaterNeverFallsBackToOldPublisher(t *testing.T) {
	old := http.DefaultTransport
	defer func() { http.DefaultTransport = old }()
	var urls []string
	http.DefaultTransport = phoenixUpdateTransport(func(r *http.Request) (*http.Response, error) {
		urls = append(urls, r.URL.String())
		return &http.Response{StatusCode: 404, Body: io.NopCloser(strings.NewReader("not published")), Header: make(http.Header), Request: r}, nil
	})
	if _, err := CheckForUpdate("0.1.2", true); err == nil {
		t.Fatal("expected controlled unavailable release")
	}
	if err := SelfUpdate("v9.9.9", true); err == nil {
		t.Fatal("expected controlled missing asset")
	}
	if len(urls) != 2 {
		t.Fatalf("unexpected fallback requests: %v", urls)
	}
	for _, u := range urls {
		if !strings.Contains(u, "/alexivy/phoenix-connect/") || strings.Contains(u, "gitee.com") {
			t.Fatalf("wrong publisher: %s", u)
		}
	}
}
