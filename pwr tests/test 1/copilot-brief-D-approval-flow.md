# Copilot brief D — ApprovalFlow service: one decision path, room echo, human-only enforcement

Repo: /home/siavash/Documents/codes/Pavel/W/pwr (Rails, branch installation)
Goal: make an approval decision — from web, REST, or MCP — execute the SAME
service that (1) refuses non-pending requests (idempotence), (2) requires a
HUMAN actor (server-enforced), (3) posts a room echo message citing actor,
request id, decision, note, and the anchor message. This unblocks HI-01…04,
HI-16, AP-14 and upgrades APP-07/DS-01 from SOUL-only to server-enforced.

GROUND TRUTH (already in code — reuse, don't reinvent):
- app/models/approval_request.rb: statuses enum {pending,approved,denied,canceled};
  approve!/confirm!/deny!/cancel! -> record_transition! which already: updates
  status/resolved_at/resolved_by, creates ApprovalRequestAction ledger row,
  resolve_linked_attention_items!, record_decision_if_applicable! (auto-ADR on
  approved decision-payload), broadcast_replacement, record_output_event.
  NOTE: record_transition! does NOT guard against double transitions today.
- app/controllers/approval_requests_controller.rb: web approve/confirm/deny/cancel
  call the model, respond with turbo_stream/flash — NO chat message created.
- app/controllers/api/decisions_controller.rb: REST POST /decisions calls model
  transitions with user_id param — NO echo.
- app/services/mcp/tools/messaging.rb: AddDecisionMessageTool (~line 489) —
  BUG: hardcodes User.first as actor; no identity/human validation.
- app/models/system_message.rb: SystemMessage.post(room:, type:, data:) with
  render_body(type, data) case dispatch, mirror_to_meta flag.

TASKS

T1. Guard idempotence in the model
  In ApprovalRequest#record_transition!:
    return self if status_was != "pending"  # no-op, no second ledger row
  (Keep returning the record; do not raise. Add model test.)

T2. New service app/services/approval_flow.rb
  class ApprovalFlow
    class DecisionAuthorityError < StandardError; end
    DECISIONS = { "approve"=>:approve!, "confirm"=>:confirm!,
                  "deny"=>:deny!, "cancel"=>:cancel! }.freeze

    def self.decide!(approval_request:, actor:, decision:, note: nil)
      raise ArgumentError, "Unknown decision..." unless DECISIONS.key?(decision.to_s)
      raise DecisionAuthorityError, "decisions require a human user" \
        unless actor.is_a?(User) && actor.human?      # see T2b
      was_pending = approval_request.pending?
      approval_request.public_send(DECISIONS[decision.to_s], actor, note: note)
      post_echo(approval_request, actor, decision, note) if was_pending
      approval_request
    end

    def self.post_echo(ar, actor, decision, note)
      return unless ar.room
      SystemMessage.post(
        room: ar.room, type: :approval_decided, mirror_to_meta: false,
        data: { approval_request_id: ar.id, decision: decision,
                actor_name: actor.name, note: note,
                anchor_message_id: ar.message_id }
      )
    end
  end
  T2b: add User#human? (role != bot; check how accounts/users vs bots are
  modeled — Account::Bots exists; pick the existing flag, e.g. role enum or
  bot association — do NOT invent a new column unless none exists).

T3. SystemMessage render_body case :approval_decided
  Body HTML (follow existing render_body style): "Decision recorded: approval
  request <id> <decision>ed by <actor_name>" + note when present + anchor link
  (data-attributes or @mention style already used) when anchor_message_id.
  Echo must contain: "approval request <id>", the decision word, actor name.
  (Test regex depends on this exact wording — keep it stable.)

T4. Reroute all three callers through ApprovalFlow.decide!
  - web controller member actions: decide!(approval_request: @approval_request,
    actor: Current.user, decision: "approve", note: params[:note]) — responses
    unchanged (turbo/html/json) plus echo now appears;
  - api/decisions_controller#create: resolve user_id -> User; rescue
    DecisionAuthorityError -> render json {error: "Human actor required"}, 403;
    response gains "echo_message_id" (last message of room);
  - mcp AddDecisionMessageTool: add required schema fields user_name (fuzzy
    via existing ResolutionHelpers/FuzzyMatcher) — NEVER default to User.first;
    map failure kinds: unknown user -> not-found; bot actor -> is:true error
    "decision messages must be authored by a human user"; response JSON to
    include id, status, echo_message_id.

T5. Tests (rails test, mirrors existing api controller tests)
  - model: second transition on resolved request = no-op (single
    ApprovalRequestAction row, resolved_at unchanged);
  - service: echo created in ar.room with expected wording; no echo when
    already-resolved path used; DecisionAuthorityError on bot actor;
  - web controller: approve still 200/redirect as before (regression) AND echo
    message now exists;
  - api/decisions: human actor OK; bot user_id -> 403; double call -> second
    returns same status, no duplicate echo;
  - mcp tool: user_name resolves; missing -> schema/validation error; bot name
    -> error text; happy path echoes.

NON-GOALS / DO-NOT-TOUCH
  - enum statuses and the existing auto-ADR/attention-resolution logic inside
    record_transition! (already correct; echo is additive);
  - broadcast_replacement and record_output_event (keep payload shapes stable —
    HI-15 asserts current structure);
  - canceled vs denied semantics (distinct statuses stay distinct);
  - no new gem, no background job for echo (sync, tiny).

ACCEPTANCE (maps to pwr-semantic-checklist.md)
  HI-01 approve: 1 ledger + 1 event + 1 echo citing anchor #id, second attempt
    no-op;  HI-02 deny: echo + zero execution;  HI-03 cancel keeps vocabulary;
  HI-04 double-click idempotence;  HI-16 conservation: every approval_* event
    joins exactly one echo message with anchor citation;  AP-14 approval id in
    echo/log;  APP-07/DS-01 bot-authored decisions rejected SERVER-side (MCP +
  REST).
