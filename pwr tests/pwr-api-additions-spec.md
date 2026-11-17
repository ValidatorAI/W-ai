# PWR API Additions Spec — what code to add so the full test suite runs automated

> Target repo: `~/Documents/codes/Pavel/W/pwr` (branch `installation` @ cd62fab).
> Goal: remove every blocker identified by `pwr-semantic-checklist.md` (246 items),
> `pwr-functionality-checklist.md` (191), `transcript-semantic-validation-mapping.md`,
> `transcript-v2-completing-replay.md` and `pwr-api-reference.md` §"gap map", so the
> roadmap phases execute end-to-end without web-browser seeding, DB surgery, or
> fabricated echoes.
> Each section = required functionality, behavior contract (must MIRROR existing
> web-controller semantics — same model callbacks, same events, same side effects),
> and the exact test ids it unblocks.
>
> Cross-cutting acceptance for ALL additions:
> (AC1) mutations emit their outbound events through `OutputEvents::Recorder`
> exactly as the web path does; (AC2) every new write respects the shared-secret
> auth of `/api` (OUTPUT_EVENTS_TOKEN) or the scoped MCP token (MCP_AUTH_TOKEN);
> (AC3) implementation must reuse the SAME service objects the web controllers use
> — no parallel logic paths (behavioral parity is itself a test target);
> (AC4) README/routes docs updated (fixes the stale `/mcp/health` claim on the way);
> (AC5) each endpoint/tool ships with a request/response example added to
> `pwr-api-reference.md`.

---

## A. Projects plane — create/update/delete (REST + MCP)  [PRIORITY 1]

**Why:** project creation is the entry point of the product story and is web-only
today (`Users::ProjectsController#create`). Without it: no headless fixtures, and
the entire PJ + EV-40 batteries are un-runnable.

**Required functionality**
- `POST /api/projects` — inputs: `name?`, `path` (required; slug derives via the
  model's `generate_slug_from_path`), `description?`, `private? (bool)`,
  `short_code?` (normalized per `normalize_short_code`).
  Validation: model rules; duplicate `path` → idempotent response: return the
  EXISTING project with `"created": false` (mirror `find_or_create_for_path`)
  — never a silent second row, never a 500.
  Side effects (must match web path exactly): `after_create_commit :announce_creation`
  → SystemMessage `project_created` to meta room (slug+path only — PJ-02 depends
  on this staying dumb), output-event recorded, NO eager project room (PJ-05
  asserts laziness).
  Output: project public attributes (same shape as GET /api/projects/:id).
  Status: 201 on create, 200 on idempotent hit, 422 `{"error": ...}` on invalid.
- `PATCH /api/projects/:id` — same field set + `current_phase`, `roadmap`,
  `recently_completed`, `budget_total/spent`; must route through the same
  `project_updated` materiality logic as the web (cosmetic vs material →
  material_changes only on scope-like diffs; PJ-11, EV-39).
- `DELETE /api/projects/:id` — archive or destroy per model capability; 204;
  refuses (409 + error body) if rooms hold open approvals — document chosen rule.
- MCP additions (action-mcp): `add_project`, `edit_project`, `delete_project`
  wrappers over the same service, fuzzy `path|project_name` inputs; config-mcp
  read twin `get_project_summary` optional.

**Unblocks:** PJ-01 PJ-02 PJ-03 PJ-04 PJ-05 PJ-06 PJ-07 PJ-08 PJ-09 PJ-10 PJ-11
PJ-12 · EV-40 (project_created handler, no DB surgery) · HA-58, HA-105 · CMP-05 ·
headless fixtures for roadmap Phase 0/6 (XD-01 pass-2 needs a fresh full stack
per run).

## B. Users, membership, direct rooms (REST)  [PRIORITY 1]

**Why:** the replay script's world contains guest partners joining rooms, DM
privacy, and non-member refusal — all web-only today
(`account/users`, `rooms/projects/users_settings`, `rooms/directs`).

**Required functionality**
- `POST /api/users` — `name`, `email_address`, `role (human|bot)`, `password?`
  (or join-code path); mirrors `Accounts::UsersController#create` incl. activate
  semantics; returns public user attrs. `PATCH /api/users/:id`, `DELETE` = ban/
  deactivate mirror.
- `GET /api/rooms/:id/members` — explicit parity with MCP `get_room_members`
  (currently MCP-only; REST-only harnesses are blind here).
- `POST /api/rooms/:id/members {user_id}` / `DELETE .../members/:user_id` —
  mirror users_settings add/remove incl. any mention/attention side effects the
  web creates; events recorded.
- `POST /api/directs {user_a, user_b}` — creates/returns the DM room exactly as
  `Rooms::DirectsController` (same lookup-if-exists rule — idempotent);
  `GET /api/directs/:id/messages` reuse existing message subtree.

**Unblocks:** MS-02 (private→private) · WA-03 WA-04 WA-05 WA-06 (two-membership
battery, HA-74/75) · ST-09 (non-member read refusal) · membership flips for
v1 beats 125/176/215 without DB inserts · fixture guests 11–15 creation
(roadmap Phase 0 seed script becomes API-only, no sqlite writes).

## C. File reservations — expose the promised capability (REST + MCP)  [PRIORITY 1]

**Why:** README promises agents "inspect conflicts / reserve / renew / release";
the model + cleanup job exist but there is NO API on any plane (gap ledger item 1,
worst offender: an advertised feature untestable and unusable by agents).

**Required functionality**
- REST under `/api`:
  - `GET /api/reservations?project_id=&path=` → `[{path, holder_user_id,
    expires_at, conflict: bool}]`
  - `POST /api/reservations {project_id, path, user_id, ttl_seconds?}` → 201 or
    **409** `{"error":"conflict","holder":...}` (409 shape asserted by RES-02)
  - `PATCH /api/reservations/:id` — renew: extends expiry; only holder (or admin)
    may renew/release (assert 403 otherwise)
  - `DELETE /api/reservations/:id` — release; idempotent (204 even if expired)
- TTL expiry: existing `FileReservationCleanupJob` must run on schedule and be
  observable (RES-03 timed test); config knob documented.
- MCP tools (action-mcp): `check_file_conflicts`, `reserve_file`,
  `renew_file_reservation`, `release_file_reservation` — same service the REST
  controller uses; every call logged to tool_cal_logs automatically by registry.

**Unblocks:** RES-01…RES-05 functional · IA-09 lineage, TP/ST conditional rows,
v1 beats 109/132/204/235 real execution · the flagship two-agent demo (AGT-16)
finally able to demonstrate the collision story it claims.

## D. Decision = state + echo, one service (refactor)  [PRIORITY 1]

**Why:** HI-01…04/16 assert that every human click produces ledger + event +
room echo. Today the echo is a side effect of the web controller only; REST
`decisions#create` transitions silently. Tests must not need Playwright to prove
product behavior.

**Required functionality**
- Extract the web approval-click flow into `ApprovalFlow.decide!(approval_request,
  actor, decision: approve|confirm|deny|cancel, note:)` performing, atomically:
  model transition + transition-ledger row + decision message in the room
  (citing: actor name, `approval request <id>`, anchor message id) + outbound
  event. Web controller refactored to call it (no behavior change — regression:
  existing HI clicks still work).
- REST `POST /api/rooms/:rid/decisions` and `PATCH /api/approval_requests/:id`
  route through the SAME service — echo now appears on API-driven decisions.
- MCP: `add_approve_request_with_message` remains atomic create; `add_decision_message`
  gains server-side rule: a decision targeting an ApprovalRequest MUST go through
  ApprovalFlow (so MCP human decisions also echo) — closes AP-07/AP-01 server-side
  enforcement (currently SOUL-only; decision_authority check: reject if caller
  profile ≠ human user_type, assertable error body).
- Cancel vocabulary preserved (canceled ≠ denied) — already in model; ensure
  the service keeps distinct statuses + events.

**Unblocks:** HI-01 HI-02 HI-03 HI-04 HI-10 HI-16 · AP-14 (approval-id cited in
echo/log) · AP-01/AP-07 become SERVER-enforced → APP-07/DS-01 upgrade from
behavioral to hard assertion · every Phase-1 checkpoint on the click family.

## E. AI-config mutations via API (REST admin plane)  [PRIORITY 2]

**Why:** the config plane is read-only outside web screens; AIC-06 (attach/detach
→ reflection without restart) and several AGT setups can't be automated.

**Required functionality**
Mirror `AiAdmin` controller actions 1:1 as REST (admin-gated, same secret):
`POST/PATCH/DELETE /api/ai_profiles` (incl. clone, reset-ai-config), `/api/ai_settings`,
`/api/mcps`, `/api/tools`, `/api/skills` CRUD + toggles
(`PATCH /api/ai_profile_tools/:profile_id/:tool_id {enabled}` etc.),
`POST /api/ai_profile_mcps`, and the `restart-w-bridge`/`reset-ai-config-all`
operations (guarded, idempotent, evented). Never expose secret VALUES — names
only (mirror existing contract AIC-05).

**Unblocks:** AIC-06 · HA-101 live-change legs · AGT-01/04/05 re-verification
without browser · config-drift checks in Phase 5.

## F. Message surface upgrades  [PRIORITY 2]

- List ergonomics: `GET /api/rooms/:rid/messages` gains `include=body`, filters
  `creator_id, system, since, until, q=substring`; add batch
  `GET /api/messages?ids=137,164,182` (cap 100). (Removes N+1 for every judge
  scan: AN-13/14, MS-05/06/08/09, HI-16 citation regex.)
- MCP: add `edit_message` to action-mcp mirroring REST PATCH (author-only rule
  enforced server-side; system messages admin-only) — closes gap ledger #3 and
  makes v1 beats 130/156/174 real API tests instead of browser probes.
- `search_messages_of_room` results should return message bodies (assertion-grade).

**Unblocks:** MSG-07/08 hardening · ledger #3 · all body-level scan families at
practical speed · RH-02/XD-09 text joins.

## G. Observability: read the planes that currently exist only as internals  [PRIORITY 2]

- `GET /api/output_events?status=&event_type=&since=` (id, type, status, attempts,
  dedup_key, knowledge_path, payload digest — NOT secrets) and
  `POST /api/output_events/:id/redeliver` (admin). Today OUT-* tests can only be
  inferred from a webhook sink; with this, delivery state is directly assertable.
- `GET /api/mcp/health` (GET, token-free or token-gated — pick one and FIX the
  README either way) → closes PRE-05/INV-12 class mismatches permanently.
- `GET /api/tool_cal_logs` REST mirror of the knowledge-mcp plane (filters:
  user, tool, target_entity_id, since) — lets pure-REST auditors verify OR-*/XD-*
  orderings; MCP keeps the write tools per audit discipline.

**Unblocks:** OUT-01…08 direct assertions · HI-15 payload inspection without
sink-only evidence · PJ-07 · HA-90 simplification · XD conservation queries.

## H. Small browser-independents (nice-to-have)  [PRIORITY 3]

- `POST /api/messages/:id/boost` (web parity) → MSG-14 headless.
- `PATCH /api/users/:id/presence` + broadcast (parity with channel presence) →
  MSG-13 headless.
- Unfurl as API: `POST /api/unfurl {url}` returning the opengraph asset → MSG-17.
These three have low test-blocker weight; do only if cheap.

---

## Scope-assignment table for new MCP tools (keeps registry conventions)

| New tool | action-mcp | read-mcp | knowledge-mcp | config-mcp | task-mcp |
|---|---|---|---|---|---|
| add_project / edit_project / delete_project | ✓ | – | – | – | – |
| check_file_conflicts | ✓ | ✓ | – | – | – |
| reserve_file / renew_file_reservation / release_file_reservation | ✓ | – | – | – | – |
| edit_message | ✓ | – | – | – | – |
| list_output_events / redeliver_output_event | ✓ | ✓ | – | – | – |
| (decision echo) — no new tool; add_decision_message now routes through ApprovalFlow | ✓ | – | – | – | – |

## Build order & effort (Rails-side, single dev)

1. D — ApprovalFlow service + REST/MCP reroute (~0.5 d; unlocks the biggest HI
   family and makes AP/DS invariants server-enforced).
2. A — projects CRUD + idempotent create (~0.5 d).
3. C — reservations REST+MCP over existing model/job (~0.5 d).
4. B — users/members/directs (~0.5 d).
5. G — output_events read + redeliver, REST tool_cal_logs, health route (~0.5 d).
6. F — include/filters/batch + edit_message MCP (~0.5 d).
7. E — ai-admin mirror (~1 d).
8. H — optional trio (~0.25 d).
Total ≈ 4 dev-days, ordered so each step immediately converts blocked checklist
rows into runnable ones (D+A+C alone make ≈ 90% of currently-blocked semantic
items executable headless).

## Post-addition test-suite impact (the punchline)

With A–G merged, roadmap phases need NO web seeding, NO sqlite surgery, NO
Playwright, NO fabricated echoes:
- blocked-by-code rows all become PASS/FAIL verdicts: PJ 12, HI 16, MS-02, WA-03…06,
  ST-09, RES-family, AIC-06, plus every fixture/seed step in Phase 0/6.
- Remaining external needs shrink to harness-only pieces (sink, poller clients,
  event replayer, judges) — all client-side, none requiring PWR changes.
- The advertised product story ("agents reserve files, raise+get decisions with
  visible human judgment, all over MCP") finally has an API surface that proves
  it — which is exactly what PWR Work sells.
