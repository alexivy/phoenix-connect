# Phoenix Connect (0.1.0 candidate)

Personal development fork of tasercake/pi-connect. Base for this branch: 0b4b34992be71c5bbe34a573198e7e32e78d35a1, matching the installed phone bridge. Keep the upstream remote and history; reconcile upstream changes through reviewed merges.

This package owns the Go messaging bridge and its Pi management extension. Phoenix Core is a separate Pi package owning all cases, queue and workers; the existing pi-a2a package remains the A2A protocol adapter. The Connect Pi extension never starts duplicate workers or modifies the Core's active tools.

Install with `pi install /absolute/path/phoenix-connect`. Register its transport explicitly using `python /absolute/path/phoenix-connect/phoenix/configure.py`. `/phoenix-connect` checks bridge reachability only. The existing bridge must be configured with its owner allowlist; registration does not create bots, copy secrets or launch services.

The versioned transport reads an explicit target and message from stdin. A successful Go /send acknowledgement maps to accepted; failure returns a safe category. It never picks the first active chat. Notification IDs currently provide correlation, not platform deduplication.

Imported deployed patches: silent queue acknowledgement and idle-close notice respecting silent_idle_reset, with regression tests. These and the adapter are candidates in this repository; production remains on the separately protected working version until package migration and proactive Feishu delivery are verified. Configuration, chats and business data are outside this repo.

Tests: upstream Go suite, Core Python suite, isolated dual-Pi shared-case test, and transport contract tests. Android/Termux is the supported initial test target. Preserve upstream provenance and notices; no new license is assigned to upstream code by this packaging.

Project configuration adds `silent_idle_reset` and `silent_queue_notice`, both false by default. The first hides routine close/new-session notices; the second hides accepted-message queue receipts while preserving queue errors. Startup and reload both apply them.

Termux portability: process-loop tests use t.TempDir() rather than a non-existent /tmp. Repository text uses LF so embedded shell probes retain valid shebangs. Full Go tests require actual web/dist assets; these are built from the unchanged upstream UI in the isolated validation tree.

2026-10-19 candidate validation: 23 isolated Core/transport regressions passed; the two package manifests loaded together in actual Pi 1.3.0 sessions and shared a synthetic handoff. Connect full Go suite passed across 21 packages after building the real upstream web assets. No candidate package has replaced production, and real proactive Feishu delivery is still an acceptance gate.

0.1.1 migration support: package-owned bridge controller/front launcher, supervisor ownership guards, package-version health, and durable holding of legacy unsent results. 28 isolated tests and actual dual-package Pi loading passed. Runtime migration preserves the original database and private owner configuration.
