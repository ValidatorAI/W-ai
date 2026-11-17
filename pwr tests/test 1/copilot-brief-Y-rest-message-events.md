# Copilot brief Y — REST message creation must emit the web event trio (last Phase-1 blocker)

Repo: /home/siavash/Documents/codes/Pavel/W/pwr (branch installation, HEAD 329f4ba)
Finding (live-verified 2026-11-11): POST /api/rooms/:id/messages creates the
message (row + ActionCable broadcast) but records ZERO output events. The whole
agent-wake chain therefore never starts from the REST plane. Web parity target
is app/controllers/messages_controller.rb#record_created_message_events
(lines ~105–142) which records, under MessageEmissionPolicy, sharing ONE
group_id: message_created {room_id, content_type} → message_attachment_uploaded
{room_id, filename} when attachment? → ai_question_asked {room_id, bot_user_ids,
mode} when human sender AND (mode=="ask" OR mentionees.active_bots.any() OR
room.direct? expansion to all active bots). api/messages_controller.rb contains
no Recorder references at all — that's the gap, not a misread.

--- TASKS ---
Y1. Extract app/services/message_creation_events.rb (name per house style):
  `MessageCreationEvents.record(message:, room:)` mirroring the web private
  method EXACTLY: policy gate first (return silently when filtered — bot-sender
  messages emit nothing); group_id = SecureRandom.uuid shared across the trio;
  same event types/ids/actor/target_type/data shapes; bot_recipients_for
  semantics incl. direct-room all-bots expansion; mode comes from the message
  (see Y2). Then MessagesController#record_created_message_events becomes a
  one-line delegation (its existing tests MUST stay green unchanged).
Y2. Api::MessagesController#create calls MessageCreationEvents.record after the
  successful create (same position as web: after broadcast). API create must
  accept `mode` ("ask"|"message", default "message") in params and pass it
  through — mirror how web reads it; if web derives mode from
  message_params[:mode], the service should read message mode the same way
  (check how web stores/modes it — @message_mode ivar vs column — and keep the
  service honest; document what you find).
Y3. Edit path check, one sentence of rigor: grep for Recorder in web
  messages#update path. If the web edit emits NO events (current assumption —
  MessageUpdateService has no Recorder), the API/MCP edit plane is already
  correct: emit nothing, and say so in the PR description. If web DOES emit,
  move those emissions into MessageUpdateService so all three planes share
  them. Do not invent edit events.
Y4. Tests:
  - service: trio recorded with shared group; policy-filtered (bot sender)
    records nothing; direct room records ai_question_asked with ALL active bot
    ids; ask-mode records ai_question_asked with empty bot_user_ids; mention
    records mentioned bot ids.
  - api controller: POST /api/rooms/:rid/messages with @mention → message
    rows appear in GET /api/output_events?event_type=message_created and
    ai_question_asked (reuse the existing token-auth test pattern); attachment
    variant asserts message_attachment_uploaded with filename; filtered case:
    message authored by a bot user id → zero new events.
  - regression: messages_controller web tests + existing api messages tests green.

NON-GOALS: no new event types; don't touch Recorder/FILTERED_EVENT_TYPES; no
dispatch changes; ai_task flow untouched.

ACCEPTANCE = the G0 gate passing end-to-end: REST-posted "@coder status?" in
receipts-growth produces message_created (→ OUTPUT_MESSAGE_PROFILE=
message_analyzer) + ai_question_asked with coder's bot_user_ids (→ resolve_
profile routes to coder's AiProfile), ProcessAndDispatchJob dispatches both to
http://127.0.0.1:8642, group lands status=dispatched, and coder replies into
room 2. Until this PR merges, Phase 1 replay through REST wakes nobody — web
replay works today, which is why this is the only remaining event blocker.
Retry semantics of the dispatch (hermes_busy reschedule, reconcile job,
redeliver→perform_later from brief X) are already in place and untouched.
