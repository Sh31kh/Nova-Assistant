# DECISIONS.md

## 2026-09-10: Overall scope — phased build, not the full original spec
Chose: Build in phases (Phase 0 proof-of-concept → Phase 1 MVP → integrations one at
a time → scheduler → everything else later).
Rejected: Building the full architecture (plugin system, provider abstraction, OAuth
integrations, installer) up front as originally planned.
Why: No user validation yet that the core loop even works reliably. Premature
generalization for hypothetical future needs (multiple providers, third-party
plugins) with zero current instances of that need. Revisit generalizing anything
only after a second concrete case demands it.

## 2026-09-10: LLM provider — Anthropic only, no abstraction layer
Chose: Call the Anthropic API directly.
Rejected: An LLMProvider interface supporting multiple backends (OpenAI, Ollama, etc.)
Why: Only one implementation exists. An interface with one implementation is
speculative complexity, not architecture. Add abstraction if/when a second
provider is actually needed.

## 2026-09-10: Speech-to-text — test local Whisper before committing
Chose: Start with faster-whisper (local, small/base model) as the default assumption.
Rejected: Committing to a cloud STT API by default.
Why: Local keeps mic audio on-device (consistent with privacy goals) and avoids a
per-request API cost/dependency, but needs a real latency measurement on my own
hardware before I trust it for a responsive voice UX. [Update this entry once
Phase 0 latency testing is done — record actual ms and final decision.]

## 2026-09-10: Global hotkey — user-mode hook, not a kernel driver
Chose: Use a standard user-mode global hook (e.g. keyboard/pynput on Windows,
SetWindowsHookEx-based) for push-to-talk.
Rejected: Any kernel-level input driver (e.g. Interception-style drivers).
Why: Anti-cheat systems (Vanguard etc.) specifically flag kernel-mode input-faking
drivers because cheat tools use the same category of driver. Plain user-mode
hooks that don't touch the game process, inject code, or read memory sit in a
much lower-risk category by anti-cheat vendors' own stated detection criteria.

## 2026-09-10: Game mode — full hook teardown/reinstall, not an internal pause flag
Chose: On detecting a running game process, fully uninstall the global hook and
reinstall it only after the game process exits.
Rejected: Keeping the hook active and just gating on an internal `paused` flag.
Why: An internal pause flag doesn't change what's actually present at the OS
level — the hook itself is what could matter to some anti-cheat, not whether my
own code chooses to act on its events. Default to game-mode-on for any detected
game I haven't explicitly allowlisted, since safe-by-default is more important
than convenience here.

## 2026-09-10: Tool execution — structured allowlisted tools only
Chose: LLM can only call explicit, schema-validated Python functions
(open_application, browser_search, etc.).
Rejected: Giving the LLM arbitrary shell/Python execution.
Why: Arbitrary code execution from LLM output is an unacceptable security surface
for something with mic/filesystem/account access, regardless of how convenient
it would be for prototyping.

## 2026-09-10: Credentials and secrets
Chose: `.env` for API keys (gitignored), never hardcoded; OS credential store
(`keyring`) for OAuth tokens once Phase 2 (Spotify) needs it.
Rejected: Storing tokens/keys in a plain config file long-term.
Why: Committing to this convention from day one costs nothing now and avoids an
annoying retrofit later, and is required if this is ever going to be public on
GitHub.

## 2026-09-10: No database yet
Chose: Plain YAML config + log file for Phase 0/1.
Rejected: SQLite from the start.
Why: No relational data exists yet (no automations, no run history). Introduce
a database when Phase 4 (scheduler) actually needs to store structured records,
not before.

## 2026-09-10: Documentation approach
Chose: One growing README.md (kept honest about current capabilities only) +
this DECISIONS.md log, started from Phase 0.
Rejected: Full GitHub-repo scaffolding (CONTRIBUTING.md, SECURITY.md, docs site)
this early.
Why: No contributors, no public users, no plugin API yet — that documentation
would describe things that don't exist. Write it when Phase 5+ makes it real.