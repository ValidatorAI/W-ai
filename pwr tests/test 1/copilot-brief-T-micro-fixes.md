# Copilot brief T — micro-fixes PR: the six remaining tails

Repo: /home/siavash/Documents/codes/Pavel/W/pwr (branch installation, HEAD 17a2610)
Six small, independent fixes. One PR, separate commits, each with tests. Do NOT
refactor beyond scope.

T1. Project destroy guard (safety)
  app/controllers/api/projects_controller.rb#destroy: before destroying, if any
  ApprovalRequest joined to the project's rooms is still pending:
    ApprovalRequest.joins(:room).where(rooms: { project_id: project.id }, status: :pending).exists?
  → render json: {"error":"open approvals exist","pending_count":N}, status 409.
  Otherwise proceed as today (204). Mirror the same guard in the web destroy
  path if one exists (check users/projects or account screens — if web has no
  destroy, skip silently).
  Test: pending approval → 409 + project survives; resolve it → 204.

T2. Project members must exclude bots (parity with web)
  app/controllers/api/project_users_controller#create: after resolve_user_from_params,
    return render json: {"error":"bots cannot be project members"}, :unprocessable_entity if user.bot?
  (Web add_user uses User.active.without_bots — same rule; ROOM members keep
  allowing bots — do not change room_members controller.)
  Test: add bot user → 422; add human → existing behavior.

T3. MCP project wrappers
  New tools in app/services/mcp/tools/ (or extend project_items.rb) — names EXACT:
    add_project   : args path (required), name?, description?, private?, short_code?,
                    user_name?|actor_user_id? — same idempotent duplicate-path rule
                    as Api::ProjectsController#create (return existing + "created":false)
    edit_project  : project_id|project_name (fuzzy via FuzzyMatcher), same permitted
                    fields as REST PATCH; changed_fields → project_updated event
                    (reuse/extract shared logic with the controller — no duplication)
    delete_project: project_id|project_name; applies T1's 409-equivalent as
                    failure("open approvals exist: N")
  Register scopes: all+action (mutations). Response envelopes = repo success/failure
  standard. Tests: create/idempotent-create/edit-events/blocked-destroy.

T4. Remove silent Room.first fallback (misrouting hazard)
  app/services/mcp/tools/messaging.rb lines ~331 and ~396:
    room = resolve_room(args, project: project) || Room.first
  → room = resolve_room(args, project: project)
    return failure("Room not found: provide room_id or room_name") unless room
  Keep everything else identical. Search whole repo for any other "|| Room.first"
  in mcp tools and fix the same way. Test: add_message without room → isError,
  no message row created.

T5. add_decision_message actor contractual
  app/services/mcp/tools/messaging.rb (~line 505): change
    required: %w[approval_request_id decision]
  to also require the actor: user_name and user_id both optional individually BUT
  one required — since JSON Schema in this repo is simple, enforce in execute():
    return failure("user_id or user_name required") if both blank
  and add the same line to input_schema description. Behavior test already
  rejects bots; add: omitted actor → failure, no transition.

T6. README health claim
  README.md line ~121: replace
    curl http://localhost:3000/mcp/health
  with the true health check:
    curl http://localhost:3000/up
  (Do NOT add a new /mcp/health route in this PR — observability is section G,
  a separate larger brief.)

Acceptance mapping: T1→(A tail a; APP conservation), T2→(B deviation; WA/ST
fixture integrity), T3→(PJ agent-side rows), T4→(MS/MSG routing integrity;
REG-03 family), T5→(AP-03/DS-01 contractual), T6→PRE-05.
Run: bin/rails test test/controllers/api test/services/mcp (affected files) +
new tests. All green before review.
