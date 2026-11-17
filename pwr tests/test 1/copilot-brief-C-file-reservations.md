# Copilot brief C — File Reservations: expose the promised capability (REST + MCP)

Repo: /home/siavash/Documents/codes/Pavel/W/pwr (Rails, branch installation, HEAD 3650aab)
Goal: the README promises agents "inspect conflicts / reserve files / renew /
release" and the model+job implement most of it — but NOTHING is callable: no
route, no MCP tool, holder identity is missing, and the cleanup schedule is
commented out. Close that so RES-01…05 and the two-agent collision demo
(AGT-16) become testable, and the advertised story is true.

GROUND TRUTH (reuse, don't reinvent — verified in code):
- app/models/file_reservation.rb: fields project_id, patterns (JSON array of
  glob patterns), exclusive (bool, default true), reason (text), expires_at
  (default 1.hour.from_now via set_default_expiry). Methods ALREADY correct:
  conflicts_with? (symmetric fnmatch + shared-prefix), conflicting_reservations
  (active+exclusive+other), renew!(ttl_seconds: 3600), time_remaining,
  self.cleanup_expired!, scopes active/expired/exclusive/shared,
  broadcast_acquired/released ActionCable hooks.
- app/jobs/file_reservation_cleanup_job.rb exists.
- config/initializers/scheduled_jobs.rb lines ~29 and ~48: file_reservation_cleanup
  is COMMENTED OUT — the job never runs today.
- db/schema.rb file_reservations: NO user/holder column — ownership is unrepresentable.
- No Api:: / Mtc exposure anywhere (verified).
- Auth conventions: Api::BaseController (Bearer OUTPUT_EVENTS_TOKEN); MCP tools
  subclass Mcp::BaseTool, register with Mcp::Registry scopes (action/read/knowledge/
  task/config), use Concerns::ResolutionHelpers/FuzzyMatcher for names→ids, and
  CallLogger records every call automatically.

TASKS

T1. Ownership migration (the minimal one)
  add_column :file_reservations, :holder_user_id, :integer, null: true
  (index: true; FK-less is acceptable per repo style — check how other tables
  reference users and MATCH that style). Model: belongs_to :holder,
  class_name: "User", optional: true. nil = legacy/unowned (admin can manage).
  Do NOT touch existing columns/semantics.

T2. Service: app/services/file_reservation_service.rb
  Result objects (no controller logic):
  - conflicts?(project:, patterns:) → list of active exclusive reservations that
    conflict (reuse conflicting_reservations by building an unsaved probe or a
    class-level finder mirroring its scope).
  - reserve(project:, patterns:, holder:, exclusive: true, reason: nil,
    ttl_seconds: nil) → if conflicts nonempty raise/reserve returns
    ConflictError with the conflicting rows (ids, patterns, holder name,
    time_remaining); else FileReservation.create!.
  - renew(reservation:, holder:) → ForbiddenError unless holder matches
    reservation.holder_user_id (or reservation unowned → allow first claim? NO:
    renew only by holder; admin escape hatch only at controller layer).
    Expired reservation → ExpiredError (cannot renew the dead).
  - release(reservation:, holder:) → idempotent no-op if already gone; ownership
    check as renew.
  Keep glob-conflict logic ONLY in the model (single source of truth).

T3. REST surface — routes in config/routes.rb under namespace :api:
  resources :file_reservations, only: %i[index show create update destroy]
  (path: "reservations" is fine — pick ONE and use it consistently; mirror the
  projects id-or-slug convention for the parent project filter.)
  Controller Api::FileReservationsController < Api::BaseController:
  - GET /api/reservations?project_id=<id|slug>&include_expired=false →
    [{id, patterns, exclusive, reason, holder:{id,name}, expires_at,
      time_remaining_seconds}]
  - POST /api/reservations {project_id, patterns:[…], holder_user_id,
    exclusive?, reason?, ttl_seconds?}
    → 201 reservation JSON | 409 {"error":"conflict","conflicting":[…]}
    (409 SHAPE IS ASSERTED by tests — do not replace with 422) | 422 invalid
    patterns (blank array/nil) | 422 unknown holder.
  - PATCH /api/reservations/:id → renew; 403 {"error":"not holder"}; 410 gone/expired.
  - DELETE /api/reservations/:id → release; 204 always-successful (idempotent,
    even if already expired/deleted).
  Validation parity: patterns must be an array of strings; reject absolute-path
  or ".." patterns with 422 (glob scope is project-relative).

T4. MCP tools — new file app/services/mcp/tools/reservations.rb
  (register via the same mechanism project_items.rb uses; name strings exact):
  - check_file_conflicts  (scopes: action + read) — args: project_id|project_name
    (fuzzy), patterns:[…] → {conflicts:[{id,patterns,holder_name,expires_at,
    time_remaining_seconds}]} success even when empty list (NOT an error).
  - reserve_file          (action) — args: project, patterns (required),
    user_name|user_id (required, resolve via ResolutionHelpers; bot actors ARE
    allowed here — only decisions were human-gated), exclusive?, reason?,
    ttl_seconds? → success(reservation json) | failure("conflict: …") INCLUDING
    conflicting holders in the message; conflicts must ALSO be written as an
    attention 'blockers'-style note? NO — keep pure, echo is a later concern.
  - renew_file_reservation(action) — reservation_id (+ fuzzy project not needed);
    user_name required; ownership enforced at service → failure("not holder").
  - release_file_reservation(action) — same; always success if absent.
  All four return the repo-standard success/failure envelopes; CallLogger
  captures them automatically — do not log manually here (tool_cal_logs tool is
  an agent-side contract, not this plane's job).

T5. Enable the sweeper
  Un-comment/add the file_reservation_cleanup schedule in
  config/initializers/scheduled_jobs.rb following the existing pattern (interval:
  match how other jobs are scheduled, default 60s); ensure cleanup_expired!
  preserves broadcast_released per row (currently destroy_all fires
  after_destroy_commit per record — verify with a test, if not, loop
  find_each.destroy).

T6. Tests (rails test; mirror existing api + mcp tool test styles)
  - model: no changes (already covered) — but add holder association test.
  - controller: create 201; duplicate exclusive pattern 409 with conflicting
    payload shape; non-holder PATCH 403; holder PATCH extends expires_at;
    expired renew 410; DELETE idempotent 204 twice; unknown project 404;
    patterns [] → 422.
  - service: conflict detection parity with model method (same results).
  - mcp: check_file_conflicts on clean project → success + empty list;
    reserve→check→conflict flow between two user_names; renew/release ownership
    messages; scope leak battery: reserve_file via /read-mcp must be refused
    (registry scope), check_file_conflicts via /action-mcp and /read-mcp both OK.
  - sweeper: create expired row, run job, row gone + broadcast_released invoked.

ACCEPTANCE (pwr-semantic/functional-checklist.md rows this lights up)
  RES-01 (surface exists on both planes), RES-02 (409 conflict shape), RES-03
  (renew extends; TTL expiry via job), RES-04 (explicit release frees others),
  RES-05 (ownership refusal), INV-09 addition to scope-leak battery, v1 replay
  beats 109/132/204/235 executed for real, IA-09 lineage + AGT-16 collision leg
  of the flagship demo.

NON-GOALS
  - Do NOT change conflict semantics (fnmatch symmetry + prefix overlap is the
    tested truth).
  - Do NOT gate reservations behind human-only actors (agents are the USERS of
    this feature).
  - No new gems, no WS protocol changes, no renames of existing model methods.

OPTIONAL QUICK TAILS (same PR or a second small one; unrelated to T1–T6)
  a) Api::ProjectsController#destroy: return 409 {"error":"open approvals
     exist"} when ApprovalRequest.joins(:room).where(rooms:{project_id: …})
     .pending.any? (spec A tail; today destroy cascades silently).
  b) MCP project wrappers: add_project/edit_project/delete_project over the
     SAME controller code paths (extract or reuse services) — required for
     agent-side PJ tests.
  c) add_decision_message schema: move user_id/user_name into `required`
     (currently optional with runtime failure — make it contractual).
  d) Docs: fix README stale `GET /mcp/health` claim (PRE-05) — one line.
