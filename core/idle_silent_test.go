package core

import (
	"testing"
	"time"
)

func TestIdleResetSilentPreservesRotation(t *testing.T) {
	for _, silent := range []bool{false, true} {
		p := &stubPlatformEngine{n: "test"}
		e := NewEngine("test", &resultAgent{session: newResultAgentSession("reply")}, []Platform{p}, "", LangEnglish)
		e.SetResetOnIdle(4 * time.Hour)
		e.SetSilentIdleReset(silent)
		key := "test:user"
		old := e.sessions.GetOrCreateActive(key)
		old.AddHistory("user", "old history")
		old.mu.Lock()
		old.UpdatedAt = time.Now().Add(-5 * time.Hour)
		old.mu.Unlock()
		if !old.TryLock() {
			t.Fatal("lock")
		}
		next := e.maybeAutoResetSessionOnIdle(p, &Message{SessionKey: key, ReplyCtx: "ctx"}, e.sessions, key, old)
		if next == nil || next.ID == old.ID {
			t.Fatal("rotation not preserved")
		}
		next.UnlockWithoutUpdate()
		if len(old.GetHistory(0)) != 1 {
			t.Fatal("history lost")
		}
		want := 1
		if silent {
			want = 0
		}
		if got := len(p.getSent()); got != want {
			t.Fatalf("silent=%v messages=%v", silent, p.getSent())
		}
	}
}
