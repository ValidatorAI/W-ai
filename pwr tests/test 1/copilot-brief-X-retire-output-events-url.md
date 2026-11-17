# Copilot brief X — retire OUTPUT_EVENTS_URL (events go to Hermes; retries via dispatch groups)

Repo: /home/siavash/Documents/codes/Pavel/W/pwr (branch installation, HEAD 966558d)
Decision it implements: the webhook-outbox model is dead. Events are delivered
to Hermes through OutputEvents::ProcessAndDispatchJob (grouped/merged via
OutputEventDispatchGroup, throttled by MAX_ACTIVE_AGENTS, retried via the
"hermes_busy" reschedule + ReconcileDispatchesJob). OUTPUT_EVENTS_URL must be
removed from the codebase. OUTPUT_EVENTS_TOKEN STAYS (it is the live REST /api
bearer secret — do not touch that).

SCOPE — the four surviving references (verified 2026-11-11):
  1. app/jobs/output_events/deliver_job.rb            — guarded dead path
  2. app/services/output_events/delivery_client.rb     — used only by (1) and (3)
  3. app/controllers/api/output_events_controller.rb#redeliver — replays legacy webhook; 409-gates on URL
  4. app/controllers/users/ai_admin_controller.rb#w_bridge_restart_url — parses OUTPUT_EVENTS_URL to build /restart
  Plus docs: docs/ENVIRONMENT_VARIABLES.md lines 46–47, .env.example lines 51–52,
  app/views/users/ai_admin/learn_skill_page.html.erb copy (~line 65),
  tests: test/jobs/output_events/deliver_job_test.rb, references inside
  test/services/output_events/recorder_test.rb,
  test/controllers/api/output_events_controller_test.rb, test/test_helper.rb.

--- TASKS ---

X1. Redeliver → re-drive the Hermes dispatch (controller rewrite)
  POST /api/output_events/:id: find event (404 standard) →
  OutputEvents::ProcessAndDispatchJob.perform_later(event.id) →
  render {id, event_type, requeued: true, dispatch_group: {...current group
  status if associated...}} :ok. No ENV guard, no 502/422 delivery semantics
  anymore (drop the Transient/Permanent rescues). Keep GET index/show untouched.

X2. Delete the dead webhook path
  Remove app/jobs/output_events/deliver_job.rb and
  app/services/output_events/delivery_client.rb and
  test/jobs/output_events/deliver_job_test.rb.
  grep -rn "DeliveryClient\|DeliverJob\|OUTPUT_EVENTS_URL" app/ must return ZERO
  hits after this (fix recorder_test/test_helper expectations accordingly —
  recorder_test likely asserts delivery; re-point to dispatch behavior or drop
  the delivery-specific case).

X3. AI-admin restart decoupling
  w_bridge_restart_url → build from a dedicated ENV["W_BRIDGE_URL"] (optional;
  value = full base, e.g. http://localhost:8031). Action behavior unchanged when
  configured; when unset: the existing failure path (alert
  "Hermes gateway restart failed"/not configured message — keep the same flash
  keys so views need no change). Document W_BRIDGE_URL in .env.example.

X4. Docs/copy
  - docs/ENVIRONMENT_VARIABLES.md: DELETE the OUTPUT_EVENTS_URL row; REWRITE the
    OUTPUT_EVENTS_TOKEN row: Required=yes, "Shared bearer secret for /api REST
    plane (auth) — not a webhook URL anymore"; ADD W_BRIDGE_URL row (optional).
  - .env.example: remove the two legacy lines (keep OUTPUT_EVENTS_TOKEN), add
    commented W_BRIDGE_URL line.
  - learn_skill_page copy: replace "OUTPUT_EVENTS_URL/W-bridge" wording with
    "the Hermes workspace profile via the output-events dispatch pipeline".

X5. Tests
  - redeliver: enqueues ProcessAndDispatchJob (assert_enqueued_with), 200 shape,
    404 missing; remove the 409-config test.
  - ai_admin restart: stub W_BRIDGE_URL set/unset → success/alert paths.
  - recorder/dispatch: no deliver-job expectations anywhere.
  - Full regression: bin/rails test test/jobs test/services/output_events
    test/controllers/api/output_events_controller_test.rb plus ai_admin tests.

NON-GOALS
  - Do not change ProcessAndDispatchJob/DispatchGroup/Reconcile logic (that IS
    the retry mechanism now).
  - Do not touch OUTPUT_EVENTS_TOKEN semantics (REST auth).
  - No new event types; FILTERED_EVENT_TYPES list unchanged.

ACCEPTANCE
  grep OUTPUT_EVENTS_URL app/ → empty; redeliver re-dispatches to Hermes path;
  restart decoupled to W_BRIDGE_URL; docs honest; suite green.
  Test-suite consequence (they will update their own docs): roadmap OUT-02/04
  retry assertions move to dispatch-group states (pending→hermes_busy→
  dispatched) instead of webhook backoff; OUT-08 "legacy webhook" item becomes
  an assertion that the legacy path NO LONGER EXISTS; HI-15 payload checks read
  /api/output_events rows unchanged.
