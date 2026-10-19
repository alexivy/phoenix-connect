package main

import (
	"github.com/tasercake/pi-connect/core"
	"strings"
	"testing"
)

func TestPhoenixCLIUsesCoreUpdatePublisher(t *testing.T) {
	if githubRepo != core.UpdateRepository {
		t.Fatal("CLI and chat update publishers diverged")
	}
	for _, u := range []string{githubAPI, githubAllAPI, downloadBase} {
		if !strings.Contains(u, "/alexivy/phoenix-connect/") {
			t.Fatalf("unexpected update source: %s", u)
		}
	}
}
