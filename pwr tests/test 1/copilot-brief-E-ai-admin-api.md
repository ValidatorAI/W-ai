# Copilot brief E — AI-Admin mutation APIs on /api (mirror of users/ai_admin_controller)

Repo: /home/siavash/Documents/codes/Pavel/W/pwr (branch installation, HEAD f52a72b)
Goal: the AI-config plane (profiles/settings/mcps/tools/skills + toggles + ops)
is read-only on /api and mutable only through session-cookie web screens.
Unlocks AIC-06 (attach/detach → reflection) and all admin-plane setup steps in
HA-101/AGT audits without a browser. Same rule as before: API mirrors web
semantics EXACTLY — same guards, same events, same transactions.

READ FIRST (truth sources, do not guess):
  app/controllers/users/ai_admin_controller.rb (685 L). Key mechanics verified:
  - every mutation: before_action ensure_can_administer; profile flows also
    ensure_profile_editable! / ensure_profile_toolset_editable!.
  - events: record_ai_admin_event(event_type:, record:, data: builders
    ai_setting_event_data/ai_profile_event_data) — types include
    ai_setting_created, ai_profile_created/updated/destroyed (read the file for
    the full set incl. mcp/skill).
  - create_profile = TRANSACTION { normalize_profile_bot_name(profile);
    profile.save!; AiProfiles::BotSync.call(profile:, previous_bot: false,
    previous_bot_name: nil) } then event. update_profile passes previous_bot/
    previous_bot_name. destroy_profile goes through a service (rescue pattern
    uses error.record.errors) — find it and REUSE it.
  - toggles (profile_tool / profile_skill / profile_mcp):
    find_or_initialize_by(tool_id:) → enabled = cast_boolean(params[:enabled]) → save.
  - learn_skill: queues a skill-learning request, returns flash "…queued" (202
    equivalent). restart_w_bridge: system("hermes gateway restart").
    reset_ai_config(_all): perform_ai_config_reset! raising
    AiConfig::XmlLoader::ConfigError | ActiveRecord::RecordInvalid | KeyError.
  - existing READ serialization in app/controllers/api/ai_*_controller.rb —
    REUSE its field allowlists verbatim for mutation responses (AIC-05: secret
    VALUES must never appear; names-only contract).

--- TASKS ---

E1. Shared web/API logic extraction (smallest honest slice):
  app/controllers/concerns/ai_admin_events.rb — move record_ai_admin_event +
  the *_event_data builders into this concern, included by the web controller
  AND the new API controllers (no behavior change on web). If destroy_profile
  already uses a service object, reuse as-is; otherwise extract
  AiProfiles::Destroy mirroring current rescue semantics (error.record…).
  Do NOT extract the whole 685-line controller.

E2. Routes (extend existing api resources from index/show to CRUD + ops):
  resources :ai_profiles,  only: %i[index show create update destroy]
  resources :ai_settings,  only: %i[index show create update destroy]
  resources :mcps,         only: %i[index show create update destroy]
  resources :skills,       only: %i[index show create update destroy] +
      member patch :toggle_default ; collection post :learn
  resources :tools,        only: %i[index show] + member patch :toggle
  nested toggles (mirror toggle_profile_* actions):
    patch "/ai_profiles/:profile_id/tools/:tool_id/enabled",   to ai_profile_tools#toggle_enabled
    patch "/ai_profiles/:profile_id/skills/:skill_id/enabled", to ai_profile_skills#toggle_enabled
    patch "/ai_profiles/:profile_id/mcps/:mcp_id/enabled",     to ai_profile_mcps#toggle_enabled
  ops:
    post "/ai_admin/restart_w_bridge"
    post "/ai_admin/reset_ai_config"            (all-company)
    post "/ai_profiles/:id/reset_ai_config"     (per-profile)

E3. Controller semantics (one module, base = Api::BaseController):
  Strong params: copy from web (ai_setting_params / mcp_params / skill_params /
  profile_params — READ the private defs and match the allowlists exactly).
  Error mapping (uniform):
    record not found              → 404 {"error":"…not found"}
    validation                    → 422 {"error": errors.full_messages.to_sentence}
    ensure_profile_editable!      → 403 {"error":"profile not editable"}
    ensure_toolset_editable!      → 403 {"error":"profile tool sets not editable"}
    reset ConfigError/RecordInvalid/KeyError → 422 {"error": message}
    learn_skill invalid           → 422; queued → 202 {"status":"queued"}
    restart_w_bridge              → run same system() call; 200 {"triggered":true}
      / 500 {"triggered":false} — keep identical command, add a comment that
      this is a server-local op.
  Responses: serialized with the EXISTING read-side field allowlists (AIC-05 —
  never values). destroy → 204. toggle_enabled → object incl. enabled + ids.
  Events: every mutation calls record_ai_admin_event (concern) with
  actor from optional params[:actor_user_id]/[:user_name] (resolve_user
  pattern from B/D; nil allowed, NEVER User.first default).
  Guards parity: API plane has no Current.user, so the admin check = bearer
  token (documented, same as all /api writes); BUT the profile-editability /
  toolset guards MUST be enforced identically (they protect data integrity,
  not just UI).
  create/update/destroy profile MUST run the same transaction + BotSync
  sequence (reuse extracted service from E1; write an integration test proving
  bot user sync happens on create/update/destroy via API exactly like web).

E4. Tests (mirror existing users/ai_admin controller tests, adapted):
  - CRUD happy/validation/not-found for ai_settings, mcps, skills, ai_profiles
    (profile: non-editable → 403; delete via service guard; BotSync side effect
    asserted).
  - toggles: profile tool initialize-or-update semantics (second toggle flips),
    403 toolset-not-editable.
  - events: each mutation produces the same event_type + data shape as web
    (snapshot-compare payloads), actor nil vs provided.
  - value-non-leak: response JSONs contain no secret values for settings/mcps
    (assert names present, values absent — construct a setting with a token-ish
    value and grep response).
  - ops: reset error mapping (stub to raise ConfigError → 422); restart returns
    200/500 based on system() result (stub).
  - web regression: ai_admin_controller_test stays green unchanged.

--- ACCEPTANCE (checklist rows this closes) ---
  AIC-06 (attach/detach via API → get_ai_profile_mcp reflects), AIC-01…05
  re-verifiable headless, HA-101 mutation legs, AP-15/AGT-01 admin-plane setup
  without browser, roadmap Phase 5 fully API-driven for the config plane.

--- NON-GOALS ---
  - No new authn (shared bearer stays; no per-admin tokens).
  - No hot-reload promises: after config mutation, agents need restart —
    do NOT add push/reload logic (documented behavior AGT-05).
  - Do not change AiProfiles::BotSync, AiConfig::XmlLoader, or the restart
    command itself.
  - No bulk import/export endpoints.
