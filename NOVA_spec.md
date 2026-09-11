# Personal AI Assistant — Revised Spec (Phased, No-Deadline Version)

## How to use this document

This is not a build order to execute top to bottom. It's a **north star + phased roadmap**.
The original 32-section spec is preserved at the bottom as the **long-term vision** — that's
fine to keep as an ambition, but it is *not* what you work on next. You work on the current
phase only. Do not start a phase until the previous one's "Definition of Done" is actually met
and demoable, not "basically working."

Rule for yourself: if you catch yourself building something from a later phase because it seems
easy or fun right now (e.g. writing the plugin loader while still in Phase 1), stop. That
impulse is exactly how these projects die.

---

## Guiding principles (condensed from the original)

- Python by default. Modular from day one — no single giant script — but "modular" at this
  scale means "a few files with clear responsibilities," not "abstract interfaces for every
  future provider."
- No LLM-generated arbitrary code execution. Tools are explicit, schema-validated functions.
- No hardcoded personal paths, usernames, or credentials — use config files and `.env`, gitignored,
  from the start. This one costs nothing to do early and is expensive to retrofit.
- Dangerous actions (shutdown, delete, restart, purchases) require explicit confirmation —
  implement this in Phase 1, not later, since retrofitting a confirmation layer into an
  already-built tool system is annoying.
- Treat web content and API responses as untrusted input into the LLM context.
- Defer generality until you have two concrete cases that need it. Not before.

---

## Phase 0 — Prove the core loop works (1–3 weeks)

**Goal:** prove that push-to-talk → speech-to-text → LLM tool call → action → response is
viable at all, before investing in anything else. This is a throwaway-quality spike. Ugly code
is fine here.

**Build:**
- Global hotkey listener (`keyboard` library) bound to a hardcoded key (F8).
- On hold: record mic audio. On release: stop.
- Transcribe locally with `faster-whisper` (small/base model) — verify latency is acceptable
  before committing to this as the STT approach.
- Send transcript to Claude (Anthropic API directly, no abstraction layer) with **two tools only**:
  - `open_application(name: str)`
  - `browser_search(query: str)`
- Execute the tool call, print result to console.
- No TTS yet, no tray icon, no config wizard, no scheduler, no database.

**Definition of Done:** You can hold F8, say "open Chrome and search for RTX 5070 benchmarks,"
release, and it happens, reliably, 9/10 times, in under ~3 seconds of processing latency.

**Explicitly test the risk items now, not later:**
- Does the global hotkey listener behave while Valorant (or any game with anti-cheat) is
  running and focused? If it doesn't, your entire "push-to-talk while gaming" premise is dead
  and you need to know that in week 1, not month 4.
- Is local Whisper transcription fast/accurate enough, or do you need a cloud STT API instead?
  Decide with data, not assumption.

If Phase 0 doesn't work reliably, **stop and fix this before adding anything else.** Everything
downstream depends on this loop being solid.

---

## Phase 1 — Actual MVP (a few weeks, no fixed number)

**Goal:** a genuinely useful daily-use tool for yourself, with the minimum structure needed to
not be a single script, but nothing more.

**Build:**
- Split into modules: `voice/`, `llm/`, `tools/`, `core.py` (the router), `config.py`. That's
  enough separation for now — no plugin loader, no provider interface classes yet.
- Config file (`config.yaml`, gitignored personal copy + `config.example.yaml` committed) for:
  hotkey, preferred browser, API key location (`.env`, never hardcoded).
- TTS response (Windows SAPI via `pyttsx3` is fine to start — don't build a TTS provider
  abstraction for one implementation).
- System tray icon (`pystray`) with Enable/Disable and Exit. Nothing fancier yet.
- Expand tools to whatever *you* actually use weekly. Suggested real candidates based on your
  own use cases: `open_application`, `close_application`, `browser_search`,
  `browser_open_url`, `take_screenshot`, `set_volume`.
- Confirmation flow for anything destructive (restart/shutdown/close_application on things like
  antivirus) — a simple "say yes to confirm" round-trip is enough.
- Basic logging to a file (timestamps, what was heard, what tool was called, result).
- A handful of real tests: tool input validation, and the router picking the right tool for a
  few sample transcripts (mock the LLM call for this — don't hit the real API in tests).

**Definition of Done:** You use this instead of manually opening apps/searching for at least
2 consecutive weeks, without it annoying you enough to go back to doing it manually. That's the
real bar — not "the demo works," but "I keep using it."

**Explicitly deferred, and why:**
- Provider abstraction (multiple LLM/STT/TTS backends) — you have one of each. Abstracting now
  is speculative generality with no second implementation to validate the interface against.
- Setup wizard — you're the only user. A YAML file you edit by hand is fine.
- Plugin system — there's nothing to plug in yet beyond what's in core.
- Database — a log file and a YAML config are enough at this scale. SQLite comes when you have
  actual relational data (e.g. automations with run history) in Phase 4+.

---

## Phase 2 — One real integration, done properly (Spotify)

**Goal:** learn what a *real* external integration costs (OAuth, token storage, error handling,
rate limits) using the one you'll use most.

**Build:**
- Spotify OAuth (`spotipy` or raw OAuth flow) — verify current Spotify API scopes/capabilities
  before assuming any given control works.
- Token storage via Windows Credential Manager (`keyring` library), not a plaintext file.
- Tools: `spotify_play_playlist`, `spotify_pause`, `spotify_skip`, `spotify_current_track`.
- Real error handling: expired token → tell the user to re-auth, not a silent failure.
- This is also where you introduce the concept of an "integration" as a distinct code unit
  (its own folder, its own tool registration) — but still not a formal plugin *system* with a
  loader/registry. One real example first; generalize after you have a second one (Phase 3).

**Definition of Done:** "Play my gym playlist" and "pause" work reliably including across token
expiry, with a clear spoken/logged error when Spotify isn't running or auth has lapsed.

---

## Phase 3 — Second integration + extract the real plugin pattern

**Goal:** now that you have two integrations (Spotify + one more — YouTube or Discord, your
choice, pick whichever you'll actually use), look at what's actually duplicated between them and
extract *that*, not a hypothetical future third-party plugin API.

**Before building YouTube features:** verify what the current YouTube Data API actually exposes.
Watched-history-based logic ("remove videos I've watched") is very likely not available through
the official API for privacy reasons — confirm this yourself against current docs before
designing around it, and if it's not available, tell yourself the alternative (e.g., the
assistant tracks "already surfaced to user" state itself, which is a different and doable thing)
rather than quietly assuming the feature works.

**Definition of Done:** two integrations working, and a genuinely reusable (not just imagined)
pattern for registering tools/config/OAuth for a new integration — proven by the fact you used
it twice, not designed in the abstract.

---

## Phase 4 — Scheduler (only once you have something worth scheduling)

Build the natural-language-to-structured-automation piece, and the generic academic-term-time
system, once you have at least two integrations to actually chain together (e.g. Spotify +
whatever launches your stream setup). Building the scheduler before this exists means designing
against imaginary automations.

**Definition of Done:** "Every Monday at 7pm during term time, play my Valorant playlist and open
Streamlabs" — created via natural language, confirmed by you, and it actually fires unattended
at least once correctly.

---

## Phase 1 addendum — small additions, same phase, not new scope

Three small features, added after actually finishing the config-driven
app system (Phase 1's core work). Each is cheap specifically *because*
the underlying architecture (config aliases, the `result["message"]`
field kept separate from the untrustworthy LLM `content` field, the
tray-icon plan already in the original vision) already exists to support
it — none of these are new subsystems.

- **TTS speaks `result["message"]` after every tool call.** Already
  architecturally ready — `message` was deliberately kept separate from
  raw model `content` during Phase 0 testing specifically so it would be
  safe to speak. Small addition (`pyttsx3` or similar), not a new phase.
- **Tray icon reflects listening state** (idle vs actively recording) —
  already scoped in the original vision (Section 20), just needed
  concrete detail: swap icon on hotkey press/release via `pystray`.
- **Site aliases, not just app aliases.** "Open Google Sheets" should go
  straight to sheets.google.com, not open Chrome and type a search.
  Reuses the exact alias-resolution mechanism already built for apps —
  add a `sites:` section to config.yaml (name → direct URL) and a
  `browser_open_site` tool alongside `browser_search`.

## Phase 2.5 — Modes & always-listening (future, not started)

Added from a real brainstorm, deliberately evaluated and scoped down
before being added here — not all of the original ideas made the cut,
and the reasoning for what didn't is kept below rather than silently
dropped, since it's worth remembering why later.

**Don't cross this bridge until Phase 1/2 (config system, one real
integration) are genuinely done.** This phase depends on real
architecture decisions (see below) that shouldn't be made speculatively.

### What's in scope for this phase, when it arrives

- **Always-listening as an alternative input mode to push-to-talk**, via
  a local wake-word engine (e.g. Porcupine, openWakeWord) — "Hey Nova"
  triggers listening instead of holding F8.
  - Real architectural tension to resolve, not paper over: this is a
    different privacy posture than Phase 0's "no continuous mic
    recording" principle — a wake-word engine continuously samples
    audio locally, even though it discards non-matches and sends
    nothing anywhere until triggered. Be explicit about this distinction
    in the README when it's built, don't blur the two.
  - Also conflicts with the "near-zero idle resource use while gaming"
    priority — a wake-word model has to run continuously, not
    on-demand. **First step when this phase starts: measure actual idle
    CPU/resource cost of a candidate wake-word engine on real hardware,
    same discipline as every Phase 0 latency test.** If it's not
    near-zero, that's a real finding that changes the design, not
    something to build around blindly.
- **General "modes" concept** (not just "game mode" as a one-off
  special case) — e.g. Game Mode (push-to-talk, notifications
  silenced except allowlisted senders, no work-app restrictions) vs.
  Work Mode (always-listening default, games blocked from opening).
  Config-driven: a `modes:` section, each mode declaring its input
  method and an allow/deny list of tools. This is a better
  generalization than a hardcoded "game mode" flag, and more in
  keeping with the project's own "don't hardcode for one use case"
  principle — but it explicitly **depends on** always-listening
  existing first, since "Work Mode defaults to listening" isn't
  buildable without it. Sequence matters, not parallel work.
- **Voice confirmation of actions** ("opening Valorant") — natural
  extension of the Phase 1 TTS addition above, not new architecture.

### Explicitly flagged, not simply added — needs more work before it's real scope

- **Notification silencing with an "important" exception.** Two
  unresolved problems, not just effort: (1) feasibility on Windows
  hasn't been verified against current OS APIs — don't assume it's
  possible until actually checked, per the project's own rule about
  verifying platform/API capability before designing around it; (2)
  "except important ones" is an unsolved design problem, not a detail —
  a hardcoded sender allowlist is simple but rigid; having the LLM
  classify notification importance in real time reintroduces the exact
  reliability problem Phase 0 spent hours characterizing (a model with
  a measured ~1-in-5 error rate on trivial commands deciding what
  interrupts you is a real concern, not a hypothetical one). Needs a
  real design pass before it becomes a roadmap line, not before.

### Deliberately dropped, not deferred

- **"Pull up an anime site" as an open-ended watch-something target.**
  General references to "anime sites" commonly point at unlicensed
  streaming aggregators. This is explicitly scoped OUT — the
  find-something-to-watch feature should only ever resolve to licensed
  platforms the user actually subscribes to (Netflix, Crunchyroll,
  YouTube, etc. — configured the same way as any other site alias), not
  an open-ended "find me an anime site" resolution. Given the intent to
  publish this project publicly under a real name, this isn't just a
  content-quality call, it's a real legal-exposure question worth
  taking seriously rather than building around quietly.

## Phase 5+ — Everything else in the original vision

Maps, Discord, OBS, browser automation, further providers, plugin system for third-party
developers, installer/packaging, public GitHub polish (SECURITY.md etc.), auto-update.

Do **not** plan these in detail now. When you get here, re-derive the spec for that phase the
same way this document was derived for phases 0–4: what do you actually need, based on what
you've learned building the earlier phases — not what sounded good in an initial brainstorm.

---

## A note on the CV framing

If you stop after Phase 1 or 2 and never touch this again, you *still* have something good to
show: a working voice-controlled automation tool with a real integration, clean module
boundaries, tests, and a sensible security model (tool allowlisting, confirmation for
destructive actions, credentials kept out of the LLM context). That is a legitimate, explainable
project in an interview. An unfinished 8-integration plugin platform is a worse story, not a
better one — "I designed for extensibility I never needed" is not the flex it sounds like.

So: work in phase order, keep each phase actually finished before moving on, and you'll never be
in a position where the project is worthless if you stop.

---

## Appendix: original full-vision spec

*(Preserved as-is for reference — this is the eventual ceiling, not the current task list.)*

See your original document for the complete 32-section spec covering the full architecture,
all integrations, plugin system, provider abstraction, installer/distribution, and open-source
release requirements. Nothing in it is wrong as a long-term direction — it was wrong only as a
*starting point*.