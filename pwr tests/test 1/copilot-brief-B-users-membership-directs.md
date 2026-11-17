# Copilot brief B — Users / room-members / DM-rooms APIs (mirror of web semantics)

Repo: /home/siavash/Documents/codes/Pavel/W/pwr (Rails, branch installation, HEAD a3cec12)
Goal: today user creation, room/project membership, and direct rooms exist ONLY
as session-cookie web screens. The automated suite cannot create fixtures, flip
memberships, or open DMs without a browser or sqlite surgery. This brief mirrors
the existing web controllers onto the `/api` bearer plane with ZERO behavior
divergence (same validations, same OutputEvents shapes, same broadcasts, same
idempotence rules).

GROUND TRUTH (verified — reuse, do not reinvent):
- Accounts::UsersController#create: admin-gated; User.new(create_user_params);
  display_name defaults to name; on save records OutputEvents::Recorder
  user_activated {event_id: user.id, target_type:"User", data:{"created"=>true}};
  ActiveRecord::RecordNotUnique → email-already-in-use message.
  update/activate/destroy exist with ensure_can_administer.
- User: status enum active/deactivated/banned; bots identified by role/bot scopes
  (active_bots, without_bots exist — reuse them; SystemMessage#system_user uses
  role :bot as reference).
- Membership (app/models/membership.rb): polymorphic participant (User|bot
  users), involvement enum invisible/nothing/mentions/everything, grant_to used
  across rooms, after_destroy_commit resets participant connections.
- Rooms::Projects::UsersSettingsController add_user/remove_user (lines ~51+):
  add = TRANSACTION { project_users.create! ; each active room
  memberships.grant_to(user) } then broadcast + events project_member_added (+
  project_first_joined when first project) with shared group_id;
  remove mirrors with revocation and a cannot-remove-self guard.
- Rooms::DirectsController#create: Rooms::Direct.find_or_create_for(users incl.
  Current.user); optional initial message via create_with_attachment!; when
  previously_new_record: SAME group_id for room_created +
  direct_conversation_created + one room_member_added event per user; then
  message events per MessageEmissionPolicy (incl. ai_question_asked when bots
  in room); broadcast_prepend per membership.
- Auth plane: Api::BaseController — Bearer OUTPUT_EVENTS_TOKEN; lookups by
  find_by + {error} JSON (never raise); id-or-slug convention where applicable.

TASKS

T1. Shared services first (so web + API call the same code):
  app/services/user_admin_service.rb   — create(user_attrs, actor:) / activate /
    update / deactivate-destroy semantics identical to Accounts::UsersController;
    returns record or raises ValidationError / DuplicateEmailError
    (message: "Email address is already in use"). Records user_activated event
    (actor may be nil on API plane — see T5).
  app/services/project_membership_service.rb — add(project, user) /
    remove(project, user) lifted verbatim from UsersSettingsController private
    methods (transaction + grant_to loop + broadcasts + events; return value
    indicates no-op cases).
  app/services/direct_room_service.rb — open_for(users, initial_message: nil)
    wrapping find_or_create_for + message creation + the grouped event block
    exactly as Rooms::DirectsController#create.
  Refactor the three web controllers to CALL the services (no behavior change —
  existing tests must pass unmodified; if a test touches private methods, keep
  thin wrappers delegating to services).

T2. REST endpoints (routes under namespace :api; controllers < Api::BaseController):
  resources :users, only: %i[index show create update destroy]
    - GET /api/users?include_bots=false → [{id,name,display_name,email_address,
      role,status,created_at}] (User.active.ordered.without_bots default,
      mirroring web index).
    - POST /api/users {name, email_address, password?, role?, display_name?} →
      201 user JSON (params mirror create_user_params — reuse it via strong
      params moved to the service's allowlist) | 422 validation sentence |
      409 {"error":"Email address is already in use"} on duplicate (409 NEW here;
      web renders a flash — document divergence in response shape only).
    - PATCH /api/users/:id (role update mirror), POST /api/users/:id/activate,
      DELETE /api/users/:id (deactivate-or-destroy per web destroy semantics —
      READ the web action and mirror exactly; pick whatever it does, do not invent).
  Room membership:
    GET    /api/rooms/:id/members → [{user_id,name,role,involvement}] (parity
             with MCP get_room_members output; both sources: memberships
             .visible + include invisible via ?all=true)
    POST   /api/rooms/:id/members {user_id | user_name(fuzzy)} → grant_to;
             200 {"already_member":true} no-op vs 201 granted; records
             room_member_added event (target_type "Room", data per direct
             controller's shape); unknown user → 404; bot user → ALLOWED only
             when the web grant path allows it — CHECK Membership.grant_to usage
             for bots and mirror (rooms can contain bots; projects add_user
             explicitly excludes bots via without_bots — keep THAT distinction:
             room members may include bots, project members may not).
    DELETE /api/rooms/:id/members/:user_id → 204 always (idempotent); triggers
             existing after_destroy_commit connection reset.
  Project membership:
    GET/POST/DELETE /api/projects/:project_id/members via
      ProjectMembershipService (events + broadcasts identical; add of existing
      member → 200 already-member no-op, single event on real add).
  Directs:
    POST /api/directs {user_ids:[…], message:{body?}?, creator_user_id}
      → {room:{id,type,name,members…}, created:true|false} — find-or-create
      idempotence asserted (second call same room, created:false, NO duplicate
      events, per group_id rules); initial message follows create_with_attachment!
      + policy events incl. ai_question_asked.
    GET /api/directs?with_user_id=… → direct rooms the creator shares with a
      user (sidebar parity).

T3. Fuzzy inputs: accept user_name on all member/direct payloads resolved by the
  existing Mcp::FuzzyMatcher/ResolutionHelpers (reuse, not re-implement);
  ambiguous → 422 with candidate list (same message shape as MCP REG-02 probe).

T4. Tests (mirror existing controller-test style):
  - service tests extracted-behavior parity (event payload snapshots: user_activated,
    project_member_added/first_joined sharing group_id, direct trio with shared
    group_id, room_member_added).
  - users: 201/422/409-dup-email; activate/deactivate transitions.
  - members: grant idempotence (200 already), DELETE unknown → 204 silent,
    bot-in-room allowed vs bot-in-project refused, involvement read.
  - directs: first call created:true + 2+N events; second call created:false +
    ZERO new events (no-storm assertion, twin of PJ-12).
  - web regression: existing accounts/users, directs, users_settings tests pass
    unchanged after service extraction.

T5. Identity note (document in code comment): API plane has a shared secret, so
  event actor is passed as optional actor_user_id (mirrors D's user_name
  pattern); when absent → actor nil — do NOT default to User.first anywhere.

T6. Docs: add these endpoints to
  ../pwr tests/pwr-api-reference.md §1 table + enable list (already
  DISABLE_API_ROUTES=false live).

ACCEPTANCE (checklist rows this unblocks)
  MS-02 (private→private via /api/directs + message plane) ·
  WA-03 WA-04 WA-05 WA-06 (two-membership battery: create users 11–15, flip
  room membership, re-ask) · ST-09 (non-member read refusal needs real
  membership setup) · roadmap Phase-0 guest seeds become API-only (sqlite
  workaround retired) · v1 beats 125/176/215 executed for real · AUT-05 setup.

NON-GOALS
  - No per-user tokens / no auth model changes (shared bearer stays; attribution
    via actor params as in T5).
  - No presence API, no join-code email flows, no password reset.
  - Do NOT alter Membership involvement semantics or broadcasts.
  - Do NOT allow bots into project members (web forbids it — keep it).
