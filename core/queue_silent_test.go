package core

import "testing"

func TestSilentQueueNoticePreservesQueueAndErrors(t *testing.T) {
	for _, silent := range []bool{false, true} {
		p := &stubPlatformEngine{n: "test"}
		sess := newQueuingSession("silent-queue")
		e := NewEngine("test", &controllableAgent{nextSession: sess}, []Platform{p}, "", LangEnglish)
		e.SetSilentQueueNotice(silent)
		e.SetMaxQueuedMessages(1)
		key := "test:user"
		state := &interactiveState{agentSession: sess, platform: p, replyCtx: "ctx"}
		e.interactiveStates[key] = state
		msg := &Message{SessionKey: key, Content: "keep this message", ReplyCtx: "ctx"}
		if !e.queueMessageForBusySession(p, msg, key) {
			t.Fatal("not queued")
		}
		if len(state.pendingMessages) != 1 || state.pendingMessages[0].content != msg.Content {
			t.Fatal("queue lost")
		}
		want := 1
		if silent {
			want = 0
		}
		if len(p.getSent()) != want {
			t.Fatalf("silent=%v receipt count=%d", silent, len(p.getSent()))
		}
		if !e.queueMessageForBusySession(p, msg, key) {
			t.Fatal("overflow not handled")
		}
		if len(p.getSent()) != want+1 {
			t.Fatal("queue-full warning suppressed")
		}
	}
}
