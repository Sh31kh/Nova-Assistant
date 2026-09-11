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

## 2026-09-10: LLM provider — Anthropic only, no abstraction layer [SUPERSEDED]
Chose: Call the Anthropic API directly.
Rejected: An LLMProvider interface supporting multiple backends (OpenAI, Ollama, etc.)
Why: Only one implementation exists. An interface with one implementation is
speculative complexity, not architecture. Add abstraction if/when a second
provider is actually needed.
SUPERSEDED — see "LLM provider — Ollama (local) over Anthropic API" below.
Pivoted to local due to API cost; no API key was ever purchased.

## 2026-09-10: Speech-to-text — test local Whisper before committing
Chose: Start with faster-whisper (local, small/base model) as the default assumption.
Rejected: Committing to a cloud STT API by default.
Why: Local keeps mic audio on-device (consistent with privacy goals) and avoids a
per-request API cost/dependency, but needs a real latency measurement on my own
hardware before trusting it for a responsive voice UX.
RESOLVED: measured at 0.77s for a 3-4s clip using faster-whisper "base" model,
int8, CPU. Reconfirmed in isolation testing during core.py integration —
consistently fast and accurate. Proceeding with local Whisper, no cloud fallback
needed for Phase 0.

## 2026-09-10: Global hotkey — user-mode hook, not a kernel driver
Chose: Use a standard user-mode global hook (`keyboard` library on Windows,
SetWindowsHookEx-based) for push-to-talk.
Rejected: Any kernel-level input driver (e.g. Interception-style drivers).
Why: Anti-cheat systems (Vanguard etc.) specifically flag kernel-mode input-faking
drivers because cheat tools use the same category of driver. Plain user-mode
hooks that don't touch the game process, inject code, or read memory sit in a
much lower-risk category by anti-cheat vendors' own stated detection criteria.
VERIFIED: tested with Valorant running and focused — hotkey fires correctly
whether the game or terminal has focus, and works identically with and without
running as admin (no UIPI elevation issue encountered). No need to run the
assistant elevated.

## 2026-09-10: Game mode — full hook teardown/reinstall, not an internal pause flag
Chose: On detecting a running game process, fully uninstall the global hook and
reinstall it only after the game process exits.
Rejected: Keeping the hook active and just gating on an internal `paused` flag.
Why: An internal pause flag doesn't change what's actually present at the OS
level — the hook itself is what could matter to some anti-cheat, not whether my
own code chooses to act on its events. Default to game-mode-on for any detected
game not explicitly allowlisted, since safe-by-default matters more than
convenience here.
STATUS: design decision only — not yet implemented. Deferred past Phase 0.

## 2026-09-10: Tool execution — structured allowlisted tools only
Chose: LLM can only call explicit, schema-validated Python functions
(open_application, close_application, browser_search, unsupported_request).
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
NOTE: not currently in active use — Phase 0 runs entirely local via Ollama, no
API key required. `.env`/`.env.example` kept in the repo as scaffolding for when
an API-based provider (or OAuth integration) is reintroduced.

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

## 2026-09-10: LLM provider — Ollama (local) over Anthropic API
Chose: Local model via Ollama, ROCm-accelerated on RX 7700 XT.
Rejected: Anthropic API (Claude Haiku).
Why: No cost, keeps everything local/private. Trade-off: weaker tool-calling
reliability than Claude, needed empirical testing per-command before trusting it.
FINAL MODEL: qwen2.5:14b — NOT llama3.1:8b. The 8B model was tested first and
failed adversarial testing (see entries below); 14B was required to pass.
GPU headroom: RX 7700 XT (12GB VRAM) comfortably runs the 14B model with room
to spare.

## 2026-09-10: Ollama + ROCm confirmed working on RX 7700 XT
Verified: `ollama ps` shows 100% GPU for the loaded model. No manual
HSA_OVERRIDE_GFX_VERSION needed — ROCm 7.2 native RDNA3 support worked
out of the box.
Also verified: Ollama's background service auto-starts with Windows and idles
at negligible resource cost; the model itself is loaded into VRAM on demand and
unloaded automatically after ~5 minutes idle (default keep_alive). Matches the
idle-vs-active resource design goal from the original spec without any extra
work — not overridden.

## 2026-09-10: llama3.1:8b rejected for tool-calling — verb-inversion failure
Test: 5 phrases against 2 tools (open_application, browser_search), no system
prompt constraint yet. 4/5 correct. "Close Discord" incorrectly called
open_application(Discord) — the opposite of the requested action, not just a
missed match.
Follow-up with explicit system prompt constraining tool use: no improvement.
8/8 phrases got a tool call despite the prompt instructing the model to decline
when nothing fit — "Close Discord" / "Shut down Discord" still both called
open_application(Discord); "Delete my downloads folder" silently substituted a
different action (browser-searched how to delete it); "Play some music" invented
a nonexistent "Music" application.
Conclusion: prompt-level constraints had no measurable effect on this model.
Rejected 8B for tool-routing; moved to testing a larger model (qwen2.5:14b).

## 2026-09-10: Tool-coverage vs escape-hatch — controlled comparison (qwen2.5:14b)
Test A (add close_application as an explicit tool, no escape hatch): fixed the
Discord open/close inversion cleanly. Both phrasings correct, clean output,
2/2.
Test B (add unsupported_request escape hatch instead, no close_application):
correctly avoided calling open_application on the first pass, but produced
unstable output on repeat runs — mixed Thai/Chinese garbled text, and in one
run failed to produce a structured tool call at all, leaking raw JSON-like
reasoning as plain content instead.
Decision: verb-pair actions (open/close, play/pause, etc.) must have BOTH
directions defined as explicit tools — this is a coverage gap, not a reasoning
or confidence problem, and prompting/escape-hatches do not substitute for it.

## 2026-09-10: Escape-hatch tool alone confirmed unreliable — non-deterministic
Re-ran "Shut down Discord" x3 against the Test B config (open_application,
browser_search, unsupported_request — no close_application).
Results varied every run: unsupported_request + garbled Thai; open_application
(the original bug, recurred despite the escape hatch being available); again
unsupported_request + garbled non-English text (Kyrgyz/Kazakh-looking).
Conclusion: the escape-hatch tool does not reliably prevent verb-inversion
errors on its own — not even as a secondary safeguard. Full symmetric tool
coverage (adding close_application) is the only approach that held up
consistently across repeated testing.
Rule for all future integrations: every verb-pair action needs both directions
implemented as explicit tools before shipping. Never rely on the model to
infer that it can't do the opposite of a defined tool.

## 2026-09-10: Content field is unreliable — do not trust or surface it
Combined all four tools (open_application, close_application, browser_search,
unsupported_request) and re-ran adversarial phrases. Full 8-phrase set: 8/8
correct tool selection.
Re-audit of 6 adversarial Discord-specific reruns on this final config:
tool_calls correct 5/6 (one run returned tool_calls: None with garbled content
instead). Separately, the `content` field itself was garbled (non-English /
leaked JSON) in 3/6 runs — roughly half — independent of whether tool_calls
fired correctly. Two of the three garbled-content cases still had a fully
correct tool call alongside the garbage text.
Rule, no exceptions: `content` must never be surfaced to the user or passed to
TTS, regardless of whether a tool call is present. Treat it as debug-only, if
logged at all. `tool_calls: None` must be treated as an explicit failure state
requiring a clear fallback response ("I didn't understand that") — never
silence.

## 2026-09-10: SUMMARY — final Phase 0 tool-calling configuration
(Supersedes the individual entries above on this topic — read this one first
if short on time, the others are the supporting evidence.)
Model: qwen2.5:14b via Ollama (ROCm, RX 7700 XT, confirmed 100% GPU).
Tools (all four required): open_application, close_application, browser_search,
unsupported_request.
Rules baked into core.py:
  - Never read or surface the `content` field when a tool call is present.
  - `tool_calls: None` → explicit fallback message, never silence.
  - Verb-pair actions require both directions as separate tools — do not rely
    on prompting or an escape-hatch tool to cover a missing pair.
Validated via repeated adversarial testing (not just happy-path phrasing) —
apply the same adversarial testing standard to every tool added in future
phases (Spotify play/pause, mute/unmute, etc.), since normal phrasing alone
did not surface any of the above failures.

## 2026-09-10: audio.py + stt.py confirmed working in isolation
record_while_held() → non-empty float32 array on F8 hold/release (confirmed
via shape/dtype check, e.g. (27456,) float32).
transcribe() correctly converted captured audio to matching text.
Both verified independently before wiring into core.py, per established
testing discipline this session.

## 2026-09-10: Development environment — do not develop inside OneDrive
Problem: `audio.py`, `core.py`, `llm.py`, `main.py`, `stt.py` all showed as
0 bytes on disk despite VS Code displaying full content in the editor, and
despite content pasting/looking correct. Initially suspected OneDrive
sync/placeholder corruption (project lives under
C:\Users\...\OneDrive\Documents\NOVA).
Actual cause: simpler than suspected — the files had never been saved
(Ctrl+S) after pasting; VS Code held the content in unsaved editor buffers
only. Confirmed by checking for the unsaved-changes dot on each tab; saving
resolved it immediately, byte counts became correct.
Still true and worth keeping as a standing risk, even though it wasn't the
cause this time: developing an actively-edited Python project (plus a git
repo) inside a OneDrive-synced folder is a known source of file-lock and
timestamp/cache issues (e.g. stale __pycache__ appearing valid due to
OneDrive touching mtimes). Git and OneDrive both trying to own
change-tracking on the same files is a bad combination.
Action: build the habit of Ctrl+S immediately after pasting any new file,
before running anything. Consider moving the project to a plain local folder
(e.g. C:\dev\NOVA) before this becomes a real problem, rather than after.

## 2026-09-10: requirements.txt / .env.example drift caught and fixed
Problem: requirements.txt listed `anthropic` and `python-dotenv` (unused —
project pivoted to Ollama, no Anthropic API code exists) and was missing
`requests` (used directly by llm.py to call Ollama's HTTP API). A fresh
`pip install -r requirements.txt` would have failed on the first Ollama call
with ModuleNotFoundError.
Also: .env.example still referenced ANTHROPIC_API_KEY despite it no longer
being used anywhere in the codebase.
Fix: requirements.txt corrected to {sounddevice, numpy, faster-whisper,
keyboard, requests}. .env.example updated to note the Anthropic key isn't
currently used and why.
Lesson: dependency files and example configs drift from actual code silently
and need to be checked against real imports periodically, not just written
once and trusted.

## 2026-09-10: open/close app resolution require separate lookup tables
Bug: close_application silently failed after open_application succeeded
(Spotify) once KNOWN_APPS was changed to store full launch paths instead
of bare names — close_application appended ".exe" to a full path,
producing a nonsense process name that never matched taskkill's target.
Root cause: one shared dict used for two different purposes (launch path
vs. process image name) that happened to have compatible-looking values
until the launch-path format changed.
Fix: OPEN_PATHS and CLOSE_PROCESS_NAMES as separate dicts.
Lesson: don't reuse one lookup table for two semantically different
purposes just because the data looks similar today — verify what each
consumer of shared data actually needs before assuming a schema change
is safe everywhere it's used.

## 2026-09-10: qwen2.5:14b baseline error rate on trivial input — ~1-in-5
"Open Chrome" x5, back to back, identical phrasing: 4/5 correct
open_application call, 1/5 returned tool_calls: None with no discernible
trigger (not adversarial, not verb-ambiguous, simplest possible command).
Latency: ~1s per response once warm; one earlier isolated case took
noticeably longer (~60-90s) — suspected first-request-after-idle GPU/
driver warmup, unconfirmed, not reproduced on demand.
Implication: even on easy commands, expect a nontrivial baseline failure
rate from this model/hardware combo. core.py's "no silent failure,
explicit fallback message" design is doing real, necessary work here —
this isn't a hypothetical safeguard, it's catching real failures roughly
1 in 5 times.

## 2026-09-10: First real external user test (informal)
Had a family member try it unprompted. Asked it to pause Spotify — no
tool exists for this yet (Phase 2). System correctly declined with a
clear explanation rather than failing silently or doing something wrong.
Confirms the "explicit fallback, never silent" design is pulling real
weight, not just satisfying a test script. Also confirms README/user-
facing docs will need to clearly state current capabilities up front —
a first-time user's expectations reasonably exceeded what exists.

## 2026-09-11: Config-driven application aliases and name resolution

Application names are resolved through a configurable alias layer rather than
hardcoding alternative names into the tools or LLM prompt. The LLM passes the
application name as the user said it, and config.py resolves aliases to the
canonical application key before looking up paths/process names.

This keeps the LLM responsible for intent rather than local machine-specific
details. It also means aliases can be changed or added in config.yaml
without modifying Python code.

The resolver is case-insensitive, so VAL, Val and val all resolve to
valorant through the same val: valorant entry. Known speech-to-text
misrecognitions can also be handled here; for example, valve is configured
as an alias for valorant because Whisper occasionally transcribes spoken
"VAL" that way.

## 2026-09-11: Steam application launch and launch_args

Applications can optionally define launch_args in config.yaml. This was
introduced primarily for Steam games such as Bloons TD 6, where the Steam
executable is the launcher but the desired application is identified by its
Steam App ID.

For example, Bloons TD 6 uses Steam with -applaunch 960090 rather than
trying to launch the game executable directly. This keeps the configuration
portable and avoids hardcoding Steam-specific behaviour into the general
application tool.

open_application therefore uses two launch paths. Applications without
arguments continue to use os.startfile, which preserves the simple behaviour
already working for .exe and .lnk files. Applications with launch_args
use subprocess.Popen, because os.startfile cannot pass command-line
arguments.

This split was chosen deliberately rather than replacing os.startfile
everywhere: the existing simple case stays simple, while applications that
need arguments get the additional functionality.

## 2026-09-11: Steam AutoLogin investigation — use Option A

Investigated whether Nova should handle Steam's login state automatically
when launching Steam games. The decision was to use Option A: rely on Steam
being already logged in and let Steam handle its own authentication/session
state.

Nova should launch applications, not attempt to manage account credentials,
passwords, authentication prompts or Steam's login process itself.

This was chosen because Steam already provides the correct mechanism for
maintaining its login session, while having Nova automate authentication would
add unnecessary security and reliability risks. It would also couple Nova to
Steam's internal login behaviour and potentially require handling credentials
that Nova has no reason to store or access.

The resulting design is intentionally simple: if Steam is already logged in,
Nova can launch the configured Steam application normally. If Steam requires
the user to log in, that remains a Steam/user interaction rather than a Nova
responsibility.

This keeps the integration within Nova's intended scope while avoiding
credential handling and unnecessary automation around a third-party
authentication system.