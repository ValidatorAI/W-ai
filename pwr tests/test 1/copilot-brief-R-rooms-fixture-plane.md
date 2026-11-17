# Copilot brief R — Rooms creation plane (the last fixture-bootstrap gap)

Repo: /home/siavash/Documents/codes/Pavel/W/pwr (branch installation, HEAD 231bd9a)
Why: automated test setup (roadmap Phase 0/6, transcript fixtures: 1 project +
4 rooms + memberships) currently CANNOT be headless — `POST /api/rooms` 404s,
MCP has no create-room tool, and the project room is lazily created only by
web controllers. This brief adds the room-creation API mirroring
`Rooms::OpensController#create` exactly. After it merges, fixture seeding is
100% REST and the browser/sqlite workaround dies.

GROUND TRUTH (verified — mirror, don't reinvent):
- Room STI types: Rooms::Open / Closed / Direct / Meta / Project / Task
  (app/models/rooms/). API creates ONLY Rooms::Open; Directs already have
  POST /api/directs; Meta/Project are system-managed.
- Rooms::OpensController#create (read it in full): assembles
  `project_id` (validated against Current.user's projects), `parent_id`
  (explicit parent OR defaults to `project.ensure_project_room!.id`; guard:
  parent must belong to same project), fallback project inheritance from
  parent when project omitted; then `Rooms::Open.create_for(attrs, users:
  Current.user)`; then broadcast_create_room + events with ONE shared group_id:
  room_created + room_member_added (data shape `{"member":{"type":"User","id":N}}`).
- Room.create_for: TRANSACTION { create! ; memberships.grant_to(users) };
  creator defaults to passed creator. Room callbacks: announce_creation →
  SystemMessage.room_created (self-skips for Meta or when no Rooms::Meta exists
  yet — first-run), auto_join_human_overseer grants the overseer membership.
- room_params web-permit: `name, description`; model validates `private`
  inclusion true/false; default_involvement applies on grant.
- Permission web-gate: account.settings.restrict_room_creation_to_administrators
  → head :forbidden.
- DecisionRoom (app/models/decision_room.rb) is NOT a Room subclass: it links
  an existing room to a project_adr (+economics), uniqueness room_id+adr,
  must_belong_to_same_project validation.

--- TASKS ---

R1. POST /api/rooms (namespace :api; extend rooms resource from index/show to
  +create; keep GET behavior untouched)
  Inputs: `name` (required), `description?`, `private?` (default false),
  `project_id` (id OR slug, consistent with find_project), `parent_room_id?`,
  `user_ids[]?` (extra members to grant at creation), actor params per plane
  convention (`actor_user_id`|`user_name`, fuzzy-resolved, optional).
  Logic (mirror OpensController#create):
   - unknown project → 404 Project not found; unknown parent → 404 Room not found;
   - parent.project_id != project.id → 422 {"error":"parent room does not belong
     to this project"};
   - project present && no parent_room_id → parent = project.ensure_project_room!.id;
   - no project && parent has project → inherit parent's project_id;
   - neither project nor parent → global shared Rooms::Open (web parity);
   - create via Room.create_for with users = [actor (if resolved User)] +
     user_ids (dedupe, humans AND bots allowed as room members — rooms admit
     bots; keep project-members rules untouched);
   - after create: broadcast parity + events room_created and ONE
     room_member_added per member, all sharing a single new group_id; actor =
     resolved actor (nil allowed — never User.first).
  Response 201: full room object (existing ROOM_FIELDS + `members:[{user_id,name}]`).
  422 on validation (blank name etc.).
  Permission parity note: API plane is the trusted-server surface (shared
  secret = admin-adjacent), so DO NOT replicate the administrator? gate on
  Current (no session exists); instead: if account setting
  restrict_room_creation_to_administrators is true AND an actor user resolves,
  that user MUST be administrator → 403 {"error":"room creation restricted to
  administrators"}; if no actor given → allowed (documented deviation in the
  controller comment).

R2. POST /api/projects/:project_id/ensure_room ★ (idempotent)
  Calls project.ensure_project_room! and returns the project room with
  {"created": true|false} (detect via new-record? — capture before/after).
  404 for unknown project. This is the PJ-05/fixture hook: laziness stays the
  model rule; seeding just triggers it explicitly.

R3. PATCH /api/rooms/:id (extend rooms resource; web edit parity)
  permit name, description (and private? — model allows; web form may not, but
  API should: document as superset); fires room_updated event + broadcast;
  archived rooms → 422 refuse (check room.archived? and mirror web behavior).

R4 (small, optional but requested by the fixture docs): POST /api/decision_rooms
  { room_id, project_adr_id } + GET /api/decision_rooms?room_id= ; respects the
  model's same-project + uniqueness validations (422 with the model's message);
  201 returns the join row. No mutations beyond create (delete = DELETE /:id → 204).

R5. MCP companion (one tool, action scope): `create_room` — args name,
  project_id|project_name (fuzzy), private?, user_names[]?/user_ids[], actor
  user_name. Wraps the SAME service you extract in R1 (see below) — no logic
  duplication. Returns same shape as REST response.
  (check_file_conflicts precedent for action+read scoping does NOT apply here;
  create is action-only.)

Structure requirement (parity pattern used by all previous briefs): extract
  app/services/room_creation_service.rb (resolve project/parent → create_for →
  broadcasts → grouped events) and have Api::RoomsController#create AND the MCP
  tool both call it; the web OpensController MAY be refactored to it too if all
  its existing tests stay green unchanged (preferred, same rule as brief B).

--- TESTS ---
  - service: parent auto-default to project room; cross-project parent 422;
    project inheritance from parent; global room path; grant list dedupe incl.
    bot member allowed; events share ONE group_id (room_created + N×
    member_added) with correct data shape; announce_creation behavior: meta
    exists in test fixtures? ensure SystemMessage.room_created fires once; when
    no Rooms::Meta exists → skip (assert the first-run quirk is preserved).
  - controller: 201 full shape incl. members; 404s; 422 blank name; private
    persisted; restricted-account + resolved non-admin actor → 403; ensure_room
    twice → created:false second time; PATCH rename fires room_updated;
    archived PATCH → 422.
  - MCP tool: create_room happy + fuzzy project_name + bot in user_names; scope
    battery: create_room via /read-mcp → refused.
  - decision_rooms: happy, same-project violation, uniqueness violation.
  - regression: existing rooms_controller/opens/closeds web tests unchanged green.

--- ACCEPTANCE (roadmap/test-1 consequences) ---
  Enables headless Phase-0/6 seeding: POST /api/projects → ensure_room →
  create receipts-growth/founders/partners rooms → members grant → directs →
  decision_room link; retires browser/sqlite fixture workarounds; PJ-05 gets a
  direct API assertion path; v1 beats 116/125/176/215 and WA/ST-09 fixtures
  become fully scripted; transcript mapping §N scoreboard end-state gets
  reproducible from zero.

--- NON-GOALS ---
  - No Rooms::Closed/Meta/Task creation via API (system/flow-managed).
  - No membership involvement editing here (involvement resource stays web).
  - No archive/unarchive API in this PR (unrelated).
  - Don't touch Membership.grant_to/default_involvement semantics.
