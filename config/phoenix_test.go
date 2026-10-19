package config

import (
	"github.com/BurntSushi/toml"
	"testing"
)

func TestPhoenixSilenceFlagsDecode(t *testing.T) {
	var config struct {
		Projects []ProjectConfig `toml:"projects"`
	}
	_, err := toml.Decode(`[[projects]]
name = "test"
silent_idle_reset = true
silent_queue_notice = true
`, &config)
	if err != nil {
		t.Fatal(err)
	}
	if len(config.Projects) != 1 || !config.Projects[0].SilentIdleReset || !config.Projects[0].SilentQueueNotice {
		t.Fatal("silence settings were lost")
	}
}
