---
name: ov-wspace-lifecycle-registration
description: Use when registering W-space lifecycle events in OV.
---

# Registering W-space lifecycle events in OpenViking (knowledge profile)

## Trigger
A kanban card assigned to `knowledge` whose body is a W-space lifecycle or account event
(`room_created`, `project_created`, `room_member_added`, `project_member_added`,
`direct_conversation_created`, `account_settings_updated`, `account_bot_access_updated`, ...) and
whose task is "register/ensure the OV structure" or "capture the account state". These arrive from
the delegator with templated `/company/<numeric_id>/...` paths and often omit the created object's
id.

## Ground rules learned the hard way
1. **Two roots, one namespace.** The event payload carries the NUMERIC company id
   (`/company/1/projects/5/knowledge`) but the deployed OV namespace is SLUG-rooted:
   `company_id 1 == ai-lab`, so memory lives at
   `viking://user/hermes/memories/company/ai-lab/projects/<pid>/...`.
   Never build a second content tree under `/company/<numeric>/`; serve numeric lookups with
   small pointer notes (see step 4). Check
   `company/ai-lab/infra/ov-memory-structure-conventions.md` and
   `company/ai-lab/projects/<pid>/context.md` first — a sibling card may have written the
   convention and already built the tree.
2. **Writes are namespace-confined** to `viking://user/hermes/...` and go through ONE helper:
   `~/.hermes/scripts/ov.py`. It resolves `OPENVIKING_API_KEY` itself (env, then
   `$HERMES_HOME/.env`) — never `source .env`, never hand-rolled curl/urllib, never
   `curl | python3` (that chain trips the command-parser guard). The ROOT key is rejected
   on data APIs. Use:
   * `ov.py write --uri <uri> --file <path> --mode create --verify` — one path-exact record; the
     helper reads back through the API and fails loudly on mismatch. **`--mode create` is required
     for a NEW record**: the flag defaults to `replace`, which answers
     `404 NOT_FOUND "File not found: <uri>"` on a path that does not exist yet (cost one wasted
     round on card t_d712395a). `mkdir` the parents first — `write` does not create them.
   * `ov.py batch --root-uri <dir> --ops ops.json` — a record family or a read-modify-write
     flip in ONE round-trip, with server-enforced preconditions:
     `create_if_absent` answers `409 CONFLICT ... target already exists` when the node is
     already there (that 409 IS the "ALREADY EXISTS — do not re-create" check), and
     `replace_if_hash` (base_hash = current content hash) stops a concurrent sibling's write
     being clobbered silently. Both verified live 2026-09-25.
   * `ov.py mkdir --uri <dir>` for structure; `ov.py read|stat|ls|abstract --uri <uri>` for recon.
   `viking_remember` can NOT write these records: it targets an auto-generated
   `mem_<uuid>.md` path under its own category subdir. Use it only for narrative
   facts/summaries where any path will do.
3. **Do not do a sibling card's work.** The board penalises duplicate dispatch. Cards for
   sibling rooms/members are separate owners — register only your subject and name the others
   in your record. `project_member_added` / `project_first_joined` cards: write only
   `projects/<pid>/members/<your user_id>.md`, and list the other members in
   `projects/<pid>/members/context.md` as *pending* against their owning cards. If a sibling
   card closed itself as "duplicate of <your card>", YOUR card is canonical and must do the
   work — never mirror that closure onto yourself.

## When the session has NO shell (MCP-only toolset) — verified on card t_e96128a7, 2026-09-25
Some dispatches hand the worker the OpenViking MCP tools only and no terminal, so `ov.py`, curl and
the Rails runner are all unreachable. The tools are deferred: `tool_describe` then
`tool_call(name="mcp__workspace_memory_mcp__<read|write|edit|list|grep>", arguments={...})`.
* `write(uri, content, mode="create")` — `create` still fails loudly on an existing node
  ("File already exists"), which IS the dedup check, and it **creates missing parent directories**.
  Consequence: **directories cannot be pre-created empty**. Give each child dir (and any `threads/<id>`
  link) a small `context.md` provenance note instead of a `mkdir` abstract, and record that carrier
  divergence in the room node + registry — the sibling cards did exactly this on projects 6 and 7.
* **`grep(uri, pattern=[...])` is the RMW ANCHOR source.** It returns each matching line as
  `L<n> [pattern]: <exact line text>`, and that line text is byte-identical to the stored content,
  so it is a valid `old_string` as-is (verified on the project-6 members and project-7 rooms
  registries, 2026-09-28: 7/7, 3/3 and 10/10 grep lines were exact substrings of the stored file).
  Cost on a grown registry: 500-1,700 chars, versus 18,000-37,000 chars for a full `read` — 15-46x
  cheaper. Line numbers are **1-BASED** (the API's `content/read?offset=` is 0-based), so ask for
  `offset=<line-2>&limit=6` when you need a multi-line anchor's surroundings. Patterns are regex:
  use a bare token (`members/7.md`, `rooms/41`, `User \d`); `|` misbehaves and `(`, `)`, `**` must be
  escaped. A pattern returning 0 matches for a row you can see in a read means the *pattern* is
  wrong — re-pattern before you re-read.
* **Use `read` for an anchor only when the file is small** (roughly under 2-3k chars: per-member
  records, freshly created files, activity entries) or when grep cannot match it. Never `read` a
  `*/members/context.md`, `*/rooms/context.md`, a project `context.md` or an `_index.md` merely to
  obtain an anchor. `read(uris=[...])` does return FULL content (no truncation, unlike
  `viking_read`'s `full` level) — which is exactly why it must stay the *last* resort, not the
  first. Also note grep is index-backed: a file written seconds ago may not be greppable yet, but
  such a file is small, so read it.
* RMW with `edit(uri, old_string, new_string)`; when the anchor answers "not found" it is usually a
  **concurrent sibling card** having just rewritten that region — **re-grep** (one fresh single-file
  grep is the anchor oracle; see the concurrency note below) and retry, never force a whole-file
  rewrite. Do **not** follow `edit`'s own advice to "re-read the file with the read tool": re-grep
  first (15-46x cheaper), escalate to a window read (`content/read?offset=&limit=`), and use a full
  read only if both miss. Each failed `edit` also costs a ~60 s MCP circuit-breaker pause, so a
  cheap correct anchor beats a cheap wrong one.
* `grep(uri, pattern=[...])` doubles as the cheap read-back + stale-marker check; `list(uri, recursive=True)`
  replaces `fs/ls`. `viking_browse tree` still works for the initial recon.
* Membership STATE (`Room#users` / `.memberships`), the Rails/bridge ledger row pair and every REST
  read are NOT reachable. Cite the delegator's routing-time resolution, and mark each claim that
  depends on them as **not read in this run** (events-only). Never present a delivered payload as
  ledger-proven.
* Twin split is unchanged (`room_created` card builds the room; `room_member_added` card writes
  `members/<user_id>.md` + flips the registry row + de-stales the room node's membership section), and
  a concurrent sibling may merge your filing into its own files **mid-run** — finish with a grep sweep
  for your card id and for stale markers instead of assuming your edits stand.

## Session discipline (token discipline — measured, not stylistic)
Every API round re-bills the whole context, so reading this file twice is a real cost.
Measured across 34 recorded cards:
* Read this SKILL.md **once** per session. Do not re-view a skill you already viewed; when
  something fails, open `references/pitfalls.md` (20 KB) instead of re-reading this file.
* Read the card **once** at session start (`kanban_show`), and the thread **once** before
  closing. One card read the same `show ... | head -100` shape 30 times.
* Never open `/home/ubuntu/.hermes/kanban/**/kanban.db` directly. `kanban_show`,
  `kanban_list` and `hermes kanban show|runs` are the interface; each hand-written SQL
  re-derivation costs a full API round.
* Prefer `ov.py` over ad-hoc HTTP, and `kanban_*` tools over `hermes kanban` shell-outs.
  Every shell round-trip is one full API round at ~100–146k input tokens.

## Company-scope events (no room, no project) — `events/` + `accounts/`
Events such as `account_settings_updated` / `account_bot_access_updated` carry no `room_id` and
no `project_id`, so neither the room nor the project template applies. Verified layout
(2026-09-18):
```
company/ai-lab/events/context.md                                  index node (convention owner)
company/ai-lab/events/<date>_<event>_<HHMMSS>Z.md                  one record per firing
company/ai-lab/accounts/<account_id>/bot-access.md                 account-scope STATE register
```
Record frontmatter: `capture_type: w_space_event` + `source_event`, `company_id: ai-lab`,
`company_numeric_id`, `target_type`, `target_id`, `actor`, `occurred_at`, `captured_by_profile`,
`kanban_card`; sections `raw_event / intent_summary / context / routing / signals / follow_up`.
Filename event name uses dashes (`account-bot-access-updated`). Two firings in the same second =>
two records, never merged.

Rules that keep sibling cards correct:
* One record per firing, owned by that firing's card. A card never writes a sibling's record.
* A state register needs the *current* value, so a known-but-unfiled sibling firing is carried in
  the register marked **known-but-unfiled** (sourced from that card's RAW EVENT on the board) —
  don't invent it, and say which card owns it.
* **The card that owns the later firing does the flip** (verified on card t_d813b187, the
  07:06:36Z twin of t_b926a02c): after recon shows your record is still 404, write your record,
  then read-modify-write the register's history row from *not yet filed (card blocked)* to
  `<record path>` — **filed**, rewrite the `Current state` sourcing note to cite your own record
  instead of the unfiled carrier, and bump the register frontmatter
  (`last_updated_by: knowledge (card <id>)`). Do the same de-staling on `events/context.md`: add
  your bullet to `## Records`, flip your bullet in the "related firings" list to **now recorded**,
  and take over `last_updated_by`. Never leave a stale `not yet filed` / `known-but-unfiled`
  sentence behind — grep the read-back for both strings before closing.
* **A newly added bot id may deserve a roster entry outside the company tree.** When the event
  adds an id that OV has no identity node for, file
  `viking://user/hermes/memories/entities/user/user_<id>.md` in the shape of the existing
  `user_6.md` (name/email/status, account-access grant timestamp + source record, membership
  noted but **not** filed — the `projects/<pid>/members/<id>.md` record belongs to whoever owns
  the `project_member_added` card). Field-visible W-space name ≠ Hermes profile name: say the
  mapping is not asserted.
* `add_knowledge_activity_log` is project-scoped; for a company-scope record **do not** file it
  against a project (misattribution). The events index + register are the trail instead.
* `add_message` is not used when there is no room context.

Bot-access semantics, verified in the W-space source
(`app/controllers/users/companies_controller.rb#update`, `app/models/account.rb`) — check before
recording any such event:
* `allowed_bot_user_ids` is the **post-save resolved** list (submitted ids ∩ `User.active_bots`),
  so every id in it is an active bot user; the human owner can never appear in it.
* The event fires only when the resolved list changed, in the same transaction/`group_id` as the
  `account_settings_updated` firing at that second.
* `removed_bot_user_ids` = previous − next; non-empty also triggers `remove_bot_memberships!`
  (deletes `ProjectUser`/`Membership` rows ⇒ that bot is evicted from every room and project).
  Empty ⇒ nothing revoked, no cleanup work for execution profiles.
* Bot id → name roster: `GET http://localhost:3000/api/projects/<pid>/users` with
  `Authorization: Bearer $OUTPUT_EVENTS_TOKEN` returns the user roster (`id`, `name`,
  `email_address`) — the only live listing found; `/api/users`, `/api/accounts/1`,
  `/api/accounts/1/bots`, `/api/rooms/<id>/users` are all 404. `/api/projects/<pid>` also works.

## Company-scope ROOMS (`project_id = null`) — registry + room-scope activity trail
Verified on card t_3898e963 (Direct room 34, 2026-09-18). A Direct/Open/Meta room has no project, so
there is **no** `projects/<pid>/` segment and no project activity log:
```
company/ai-lab/rooms/context.md                       company-scope room REGISTRY (create once)
company/ai-lab/rooms/<room_id>/context.md             room node: identity + creation event
company/ai-lab/rooms/<room_id>/activities/<record>.md room-scope activity trail
company/ai-lab/rooms/<room_id>/members/context.md     room membership registry (created by the room card)
company/ai-lab/rooms/<room_id>/members/<user_id>.md   per-member room record (membership-event card)
company/1/rooms/<room_id>/context.md                  numeric-id pointer (room_id_alias_pointer)
```
Verified end-to-end on card t_3af1f7e2 (room_member_added, member User 6, room 34, 2026-09-18):
the company-scope room membership node is the **same shape as the project-room one in §2d, minus
the `projects/<pid>/` segment** — the room card (`room_created`) creates the `members/` resource +
the membership-event card creates exactly one `members/<user_id>.md` and flips its registry row.
Re-confirmed on card t_51db917e (room 36, member User 4, 2026-09-18): same one-file delta plus the
room-scope activity entry, with measured RMW dropped-line counts of 2 (members registry), 3 (room
node — its related-card bullet's first line is byte-identical after the flip, so it is preserved,
not dropped: rung exactly the assertion case documented below), 3 (company registry) and 2 (numeric
pointer). De-stale the sibling-written *pending* sentences in the room node, the company registry
**and** the numeric pointer as well, or the tree keeps a false "`members/<user_id>.md` pending"
claim after the record is filed.
registry row. The convention paragraph now lives in
`company/ai-lab/infra/ov-memory-structure-conventions.md` §2e ("Company-scope room membership").

* **`output_events` is the authoritative row set for one room-creation transaction.** For room 34
  the four firings sit in adjacent rows: `room_created` 66, `direct_conversation_created` 67,
  `room_member_added` member User 1 → 68, `room_member_added` member User 6 → 69 — all
  `event_id 34`, all one `group_id`. The member id is nested in `event_data` as
  `{"member" => {"type" => "User", "id" => N}, "actor" => {...}}`, so a runner can print
  `OutputEvent.where("group_id LIKE '<prefix>%'")` and pick your row by *member id*, not by
  timestamp. `space_events` in the bridge mirrors the same four rows (49-52) with different row
  numbers — cite both when the card references the ledger.
* **Membership columns are `participant_id` / `participant_type` / `room_id` / `involvement`.**
  `Room.find(<id>).memberships` has no `user_id` or `member_type` attribute; resolve names with
  `User.find_by(id: m.participant_id)`. `Room.find(<id>).users` returns the participant ids.
* **Read the newest comment before writing — it may be a sibling card's handoff, not the
  delegator's.** t_3af1f7e2's newest comment (10:49) was posted by the *room* card
  (`room_created`) and stated exactly what already existed and what this card's delta was, which
  avoided re-creating the room node and the `members/` resource. A card can also be
  `blocked → unblocked` while waiting on its room twin: that is a dependency wait, not a
  prior run, so the absence check in step 2 still holds.
* **Do not create a record per Direct room in place of an index.** Nothing enumerated the company's
  rooms before t_3898e963, so that card created `rooms/context.md` as *one* registry holding the
  path template, a Direct-room table (every room, with `not registered` where that is the truth), the
  ownership rule, and a `## Known divergences` section. Later room cards append to it (read-modify-write,
  idempotent sentinel check) instead of opening a second index.
* `add_knowledge_activity_log` / `knowledge_activities` are **project-scoped**: without a project the
  tool hits `/api/projects/None/knowledge_activities` and returns **404**. A company-scope room
  therefore carries its filing entry at room scope (`rooms/<id>/activities/`) — never misattribute it
  to an unrelated project.
* Sibling lifecycle cards for one room moment (`direct_conversation_created`, `room_created`,
  `room_member_added` sharing a second) are **separate owners**: register the room node once (the
  card you are on, if it is first), and name the others in the room node + registry so they append
  the `members/` edge instead of re-creating the room. Re-read the newest delegator *comment* — it
  carries corrections the body lacks (t_3af1f7e2's body said member User 1; its comment corrected it
  to User 6).
* Probes on a room whose children were pre-created empty return the **directory summary nodes**
  first: measured in-scope ranks for the records were 3 (registry), 5 (activity record), 6 (room
  node). That is index shape, not a missing record — report the rank honestly and record the
  divergence; do not chase it with more probes.
* **Company-scope room card, verified on card t_6b9b5929 (Direct room 36, 2026-09-18).** Same shape
  as room 34 (`rooms/<id>/{messages,approval_requests,decisions,activities,members}` + room node +
  members registry + numeric pointer, then RMW the company registry). Details this card added:
  - The transaction's ledger rows are contiguous in both stores (Rails `output_events` 83-86,
    w-bridge `space_events` 66-69, group `e912660d-79ea-4746-ad8b-08a14286f495`, all `event_id 36`),
    and a room created here again emits **two `room_member_added` rows** (creator self-add + one
    bot, User 4) with a board card only for the bot.
  - Bot label without a project: `Account.find(1).allowed_bot_user_ids == [2,3,4,5,6,7]` is the
    evidence (the room has no project, so `GET /api/projects/<pid>/users` does not apply).
  - **Registry RMW assertion fix — a preserved anchor is not a removed anchor.** Appending a new
    table row *after* an existing row leaves that row in place, so putting it in the "OLD marker
    gone" set fails a correct write; keep preserved anchors in a separate `KEEP` list. Also, the
    dropped-line check must exclude the **physical** lines a multi-line replacement touches (a
    logical old-string spanning two lines never equals either physical line), so a clean RMW of a
    ~90-line registry legitimately reports 3-4 "dropped" lines — list exactly those as intentional.
  - Recall shape once two Direct rooms exist: the company room registry ranks **1** for registry
    wording but **12** in the `rooms` scope for a generic query (behind 11 child directory-summary
    nodes), and the room node ranks **6-8** in its own scope for generic room wording vs **1** for
    its own creation-event wording. Probe with `limit=15` and assert "retrievable within the
    directory", and give canonical-wording probes the strict `rank 1-3` expectation.
  - The room numeric pointer note ranks **1** scoped to `company/1/rooms` (its canonical entry
    point), **5-8** under `company/1` (sibling project-room records win) and `None` unscoped —
    the sub-directory scope is the honest probe target.
* **Twin split when the `room_created` card runs FIRST (verified on card t_1de9da77, room 36,
  2026-09-18).** Room 34's order was the reverse (its `direct_conversation_created` card created the
  node), so always state the order you found. With the node already landed by t_6b9b5929, this card's
  delta was: (1) **create**
  `rooms/36/activities/direct_conversation_created_event_registered.md` — the filename mirrors the
  twin's `room_created_event_registered.md` and the frontmatter carries `capture_type:
  room_scope_activity`, `activity_type: direct_conversation_facet_registration`, `source_event*` keys
  and the ledger row pair; (2) **RMW** the room node — a new `## direct_conversation_created facet
  (addendum …)` section inserted immediately **before** `## Room content`, plus flipping the
  predecessor's pre-declared handoff bullet ("Owns the direct-conversation facet; must not register a
  second room node") to **Facet filed 2026-09-18** with the record path, plus `last_updated_by` and a
  `source_event_twin: … — facet filed` annotation; (3) **RMW** the company room registry row +
  `last_updated_by`; (4) **RMW** the numeric pointer (paragraph + `last_updated_by`); (5) optionally
  **RMW** `infra/ov-memory-structure-conventions.md` §2e with the twin-firing rule (this card added
  it: the room is registered once by whichever card runs first, the twin verifies with `fs/stat` and
  files only its own facet; the room-34 pair is cited as the counterpart). Still no
  `add_knowledge_activity_log` (404, no project), no second room node, no `members/` resource and no
  message capture — the "direct conversation" had `{"count": 0}` messages, so the facet is a room
  lifecycle fact, not correspondence.
  - **Assertion bug that WILL fire here:** the old handoff bullet's **first line is byte-identical**
    in the rewritten bullet, so it is preserved, not dropped — `dropped_lines` must be
    `old_bullet_lines[1:] + [old last_updated_by line] + [old source_event_twin line]`, otherwise a
    correct RMW reports 4 vs 5 and looks like a failure. A case-sensitive anchor ("registered once,
    by card …" vs the file's "Registered once, by card …") fails a healthy write the same way. Both
    are assertion bugs — fix the assert, never the record.
  - **Probe expectations for this delta** (measured on card t_1de9da77, hits under `result.memories`):
    activity record rank **1** in the room scope (0.8297) and rank 1 in `activities` (0.8031), rank
    **7** unscoped — an unscoped probe needs `limit: 30` *and* record-specific wording, or it returns
    7 `.abstract.md` summaries first; room node rank **2** for the addendum wording; the company
    registry ranks **13** for a generic "room 36 direct conversation" phrase (the 11 child directory
    summaries lead) but **1** for registry-own wording ("company-scope index of W-space rooms and
    their OpenViking memory nodes", 0.8168); numeric pointer rank **2** scoped to `company/1/rooms`,
    behind the sibling room-34 pointer; conventions doc rank **1** in the `infra` scope. Keep the
    missed wordings in the probe file as comments with their resolution — the fix is wording/scope,
    not re-indexing.
  - **Stray check for the numeric scope:** `fs/ls <NS>/1/rooms/<id>?recursive=true` returning only
    `context.md` is the cheapest proof that no parallel content tree was created (pair it with
    `fs/stat` on the would-be children asserting absent).
* **A `message_created`/`ai_question_asked` card from the `normal-message` profile can pre-create
  your room directory — re-check existence immediately before writing (verified on card
  t_d8a41fbe, Direct room 37, 2026-09-22).** Room 37's room-level `fs/stat <NS>/company/ai-lab/rooms/37`
  returned **404** at 10:16:42 and **200** a minute later: the concurrent message-capture card
  (`t_b05e731b`, msg 492) had created `rooms/37` **and** `rooms/37/messages` at 10:16:14Z as parents
  of its record. So the "pre-created children" divergence is not only a *knowledge*-card choice —
  any card whose record needs a room path materialises the directory. Consequence: run the
  existence check as step **0 of the write script itself** (not only in recon), `mkdir` only what
  is `404`, and never `mkdir` a directory a sibling already described (a second `mkdir` is 409, but
  you also lose the sibling's provenance description). Record the two cases separately in the room
  node: *created by this card* (`approval_requests/`, `decisions/`, `activities/`) vs *pre-existing,
  left untouched* (`rooms/<id>`, `rooms/<id>/messages`).
* **`members/` belongs to the `room_created` card whichever order it runs — not to "the first
  card".** §2e's parenthetical ("the card that runs first lands the room node (and the `members/`
  resource)") is loose. Evidence across three rooms: room 34 `members/` created by t_6f068477
  (`room_created`, ran **second**), room 36 by t_6b9b5929 (`room_created`, ran **first**), room 37
  left to t_12ec6e42 (`room_created`, ran **second**, still `ready` when t_d8a41fbe closed). So the
  **node** goes to the first card (room 37 = the `direct_conversation_created` card, i.e. the
  room-34 ordering) and the **`members/` resource** goes to the `room_created` card. A
  `direct_conversation_created` card that runs first creates `approval_requests/`, `decisions/`,
  `activities/`, the room node, the activity record and the numeric pointer — and states in the
  node, the registry and a handoff comment who owns `members/`.
* **`content/write` + `content/read` strip one trailing newline.** Read-back of a staged file is
  `disk.startswith(ov) == True` **and** `ov == disk[:-1]` — the byte count in
  `result.written_bytes` is `len(disk)+1`. A naive `got == want` equality check reports a false
  mismatch on every created record; assert the newline-stripped shape explicitly
  (`want.startswith(got) and got == want[:-1]`). Same family as the w-bridge message-API newline
  drop, but this one is OpenViking itself, so it affects every lifecycle record.
* **`content/read` ALSO strips a trailing `<!-- MEMORY_FIELDS ... -->` block** (verified on card
  t_268b8b66, 2026-09-25). Every record in this store ends with
  `\n\n<!-- MEMORY_FIELDS\n{\n  "version": 1\n}\n-->\n`; the read-back returns everything *before*
  it. So a correct write of a record whose disk file is 5167 chars reads back as 5123 — a 44-char
  delta, constant across records. `disk.startswith(got)` is True but `got == disk.rstrip("\n")` is
  **False**, i.e. the plain newline assertion above reports a false FAIL on a healthy record. The
  reader-side assertion must be `got == disk[:disk.rfind("\n\n<!-- MEMORY_FIELDS")]` (and assert the
  stripped tail ends in `-->`). Project-5's records behave identically — the block really is
  removed, not merely truncated by the client. Fix the assert, never the record.
* **Sibling handoff is a card comment.** `hermes kanban --board company comment <task_id> "<text>"`
  is the mechanism the room card uses to tell its twins their exact delta (t_d8a41fbe commented on
  t_12ec6e42 / t_88d29f7b / t_7a42a004 with the nodes that already exist, the one path each still
  owns, and the ledger rows). Do it **before** `complete`; the scratch workspace and any script only
  you hold are gone afterwards.

## Company-home ATTENTION state — `attention/` subtree + `events/` firing
Verified on card t_ef488b5b (attention item 1, category `decisions_waiting`, resolved
2026-09-18T16:59:50Z). Attention-state events (`decision_waiting_resolved`, `blocker_resolved`,
`mention_resolved`, `ai_confirm_resolved`, `knowledge_proposal_resolved`,
`material_change_resolved`, `outcome_review_resolved`) arrive as **company-scope** state changes:
no room, no message body, no `@profile` target. Nothing to forward with `hermes chat -p` and no
room reply (`add_message` not used).
```
company/ai-lab/attention/context.md                                  index + conventions owner
company/ai-lab/attention/categories/<category>/context.md            category node (title/badge/default action + item table)
company/ai-lab/attention/categories/<category>/items/<item_id>.md    one record per AttentionItem id (STATE)
company/1/attention/context.md                                       numeric pointer (capture_type: attention_id_alias_pointer)
company/ai-lab/events/<date>_<event-name>_<HHMMSS>Z.md               the firing (one per firing)
```
* **Read the queue live first** with the w-bridge tool named after the category
  (`decisions_waiting`, `mentions`, `blockers`, ...) and record the real `status`, `resolved_at`,
  `resolved_by_id`. In a record "empty" must mean *checked-and-empty*; categories you did not query
  are **not yet inventoried**, never "empty".
* **Category segment is the canonical PLURAL** (`AttentionItem::CATEGORIES` in
  `app/models/attention_item.rb`); the inbound event name is **singular**
  (`decision_waiting_resolved`). Normalize before lookup/path build — the event name never sets the
  path segment (`RESOLVED_EVENT_TYPES` is keyed plural with a singular value).
* **`resolved_at` is not a status.** `resolve!` *and* `dismiss!` both write
  `resolved_at` + `resolved_by`; only `status` (`pending` 0 / `resolved` 1 / `dismissed` 2)
  distinguishes them. Never record "resolved" from the timestamp alone.
* **Update, don't stack.** One file per `AttentionItem.id`; a later transition is a targeted
  `replace()` of the same `items/<id>.md` + the category table row.
* **State vs firing split** as in §"Company-scope events": item record = state now; the firing
  goes once to `events/<date>_<event-name>_<HHMMSS>Z.md` (filename uses the **event** name with
  dashes). RMW the events index (`events/context.md`) with a Records bullet and bump
  `last_updated_by`.
* **Never claim the underlying action happened.** Resolving a `decisions_waiting` item means the
  human decided, not that the job ran (t_ef488b5b's item was "restart hermes-gateway +
  hermes-dashboard"); say so explicitly in both records.
* No `add_knowledge_activity_log`: project-scoped tool, and an attention item has no `project_id`
  (HTTP 404 on `/api/projects/None/...`). The subtree + event log are the trail.
* Retrieval shape: with the index/category/`items` directories created by `fs/mkdir`, their
  `.abstract.md` summary nodes outrank records for generic subdomain queries; the item record
  still ranks **1** for its own wording inside the `items` scope and 4/8 unscoped. Report the
  rank, don't chase it.

## Project-scope room-creation cards (verified on card t_0d85473a, room 35, 2026-09-18)
`room_created` with a `project_id` (room 35: `Rooms::Open`, project 5, parent 29) uses the
project-room template, not the company-scope one:
```
company/ai-lab/projects/5/rooms/<room_id>[/messages|/approval_requests|/decisions|/members]
company/ai-lab/projects/5/rooms/<parent_id>/threads/<room_id>
company/1/projects/5/rooms/<room_id>/context.md      numeric pointer (room_id_alias_pointer)
company/ai-lab/projects/5/rooms/context.md           project room registry row (RMW)
```
* **The room card also creates the `members/` registry resource** (roster row for the creation
  transaction's member left **pending**, naming the sibling membership card as owner) — the
  room-creation transaction emits a `room_member_added` firing in the same `group_id`, so the edge
  needs a home. Rooms 32/33 predate this (their membership card created `members/`); pick the
  registry-here shape and *say* which precedent you followed. The membership card's own body
  usually lists `members/context.md` in its required paths, so creating it is not doing its work
  — it only writes `members/<user_id>.md` and flips the row.
* Sibling-facet split for one room moment: `room_created` card = room node + structural children +
  registry row + `members/` resource; `room_member_added` card = exactly one `members/<id>.md`.
  Leave a handoff comment on the membership card (the room card did this for t_530993aa) naming
  the nodes that already exist, the resolved edge facts, and the one path that is their delta.
* The room's live W-space state may already exceed its OV records (room 35 had message 487 at
  17:00:55Z, ledger rows 64/65, with no owning card yet). Do not write it, do not call the room
  empty — state the ledger evidence and that its capture belongs to another card.
* **Probe the parent-room thread link with the `threads/` segment.** The node is
  `rooms/<parent>/threads/<child>`, so a matcher looking for `rooms/<child_id>` reports a false
  miss; match `threads/<child_id>`. Measured ranks on card t_0d85473a: room node 1 (own scope),
  thread link 1 (parent scope), activity record 2 (index `.abstract`/`_index.md` first),
  numeric pointer 1 (scoped to `company/1`), registry 2.

## Project-creation BUNDLE: project + project room + Open children in ONE second (verified on card t_181cdcad, project 6 "Selfin", rooms 38/39/40, 2026-09-25)
Newer W-space create-flow emits the project room AND its standard Open children inside the
`project_created` transaction, so `room_created` arrives with `content: null` and **no room id**
for three rooms whose payloads differ only by `parent_id` (39 and 40 are indistinguishable).
Measured shape (group `e3790570-652c-488d-ac9c-2a8b94b11b81`, Rails `output_events` 93-98 == bridge
`space_events` 76-81): `project_created`, `project_member_added`, `project_first_joined`, then
`room_created` x3 with `event_id` 38/39/40. `GET /api/projects/6/rooms` gives the three rows.
* **There is NO `room_member_added` in this group** — unlike the hand-made room flow (§ company-scope
  rooms, room 35/34/36/37), the project room does not emit a creator self-add. So the `members/`
  registries the room card creates for all three rooms stay **event-empty**: write the roster as an
  *event-coverage* table stating zero firings, plus the live app read
  (`Room.find(<id>).users` / `.memberships`) — measured 8 rows per room, all `involvement`
  `"mentions"` (1 `User` + 7 `Agent` including the unattributable `participant_id` 9), which is the
  room-33/35 divergence again with a different ratio. Verify the absence in **both** ledgers before
  writing "no membership fired", and say which rows prove it.
* **The `project_created` sibling usually gets there first and pre-writes the rooms registry** with
  one `pending — owned by card <room_card>` row per room, a `## Known gaps` section and an explicit
  conventions paragraph. Flip those rows in place (the identical suffix makes one `replace_all`
  edit of 3 rows), restate the ownership paragraph, mark the pre-create divergence applied, back
  the "empty" gap with ledger row numbers, and append a status-update section — plus
  `projects/<pid>/context.md`'s room-layer sentence and `last_updated_by`. Zero unintended dropped
  lines is achievable; the only "dropped" lines are the three rewritten table rows.
* **Numeric side: check what the project-level pointer declares.** If it says "no second content
  tree under `/company/<n>/`", file the three room pointers as **notes only** and record the
  departure from the room-35 precedent (which mirrored room subdirectories under the numeric path) —
  a silent difference reads as an inconsistency later.
* Recall shape: activity entry rank 1 in its `activities` scope; numeric pointer rank 1 scoped to
  `company/1/projects/<pid>/rooms/<rid>`; room nodes rank 2-6 in their own room scope behind the
  pre-created children's `.abstract.md` summaries; members registries 1/3/5 in the `rooms` scope.
* **Re-confirmed on card t_9e25ea1d (project 7 "Ledgerly", rooms 41 `ledgerly` / 42 `specifications` /
  43 `releases`, 2026-09-25) — the third instance of the same shape.** Delta exactly as project 6:
  18 `mkdir`ed directories (3 rooms × `messages`/`approval_requests`/`decisions`/`members` +
  `rooms/41/threads/{42,43}`), 10 records (3 room nodes, 3 members registries, 3 numeric pointers,
  1 activity entry), 3 RMWs (rooms registry, project context, `activities/_index.md`), one w-bridge
  `add_knowledge_activity_log` (`project_id` 7). New measurements worth reusing:
  - **Pre-create is the right call for these bundle cards.** The sibling-written registry said
    "subdirs appear on first record … this registry keeps the rule"; the card body listed the paths as
    required. Resolve it the way project 6 did: pre-create them, then flip the registry's convention
    bullet to **Applied divergence** naming both cards. Consistent across projects 5/6/7 now.
  - **`members/` registries with zero firings still carry the live read.** Each of rooms 41/42/43:
    `Room#users` = `[1]`, `Room#memberships` = 8 rows all `involvement "mentions"` (one `User` row for
    participant 1, seven `Agent` rows for participants 1,2,3,4,5,6,9). Cite the membership row ids
    (`387/388/389` for the `User` rows, `390-396`/`397-403`/`404-410` for the `Agent` blocks) — the
    ids are stable evidence and cost nothing extra once the runner is open.
  - **Read-back `normalisation` is rstrip, not "one newline".** A body ending `\n\n` comes back two
    chars shorter. Assert `got.rstrip("\n") == staged.rstrip("\n")` **and**
    `set(staged[len(got):]) <= {"\n"}` — the second clause is what proves no content was lost.
  - **`ov.py batch` rejects any op outside `root_uri`**:
    `400 INVALID_ARGUMENT "batch-write target is outside root_uri: …"`. A room family spans the slug
    tree **and** the `/company/<numeric>/…` pointer notes, so pass `root_uri` =
    `viking://user/hermes/memories/company` (the common parent), not the project directory.
  - **Make the RMW script idempotent before the first run.** The first pass wrote the registry and
    *then* failed its read-back assertion; the second run had to skip already-applied edits. Guard each
    edit with `if new in body: skip elif old in body: replace else: abort`, and gate the appended
    section on `if heading in body`.
  - **Do not quote a stale phrase in your own correction prose.** An appended sentence that wrote
    `the index's own "appended by them" note was replaced` left the stale marker string in the file and
    failed the de-stale grep. Describe the removed wording, never quote it.
  - Recall on this card: `threads/42` and `threads/43` rank **1** in the parent room scope; activity
    entry **1** in `activities`; members registry **2** in `members`; numeric pointer **2** scoped to
    `company/1/projects/7/rooms/41`; registry **1** for registry-own wording but **18** for generic
    room wording (18 pre-created children now lead that scope); room nodes 3/6/7 in their own scopes;
    `projects/7/context.md` **8** in-scope with its own title wording (limit 25) vs 13 with generic
    wording — report the in-scope rank, do not chase the `.abstract.md` pool.

## Project-room MEMBERSHIP facet (`room_member_added` on a project room) — verified on card t_530993aa (User 1 → room 35, 2026-09-18)
The membership card's delta is small and precise; the room card owns everything else:
1. **create** `rooms/<room_id>/members/<user_id>.md` (shape: `capture_type: room_member_record`,
   `membership_origin: room_creator_membership` for a self-add, `source_event_group_id`, `source_card`),
2. **RMW** `rooms/<room_id>/members/context.md` — flip the roster row the room card left
   *pending* to *filed* + bump `last_updated_by` + append a live-state section,
3. **RMW** the project room registry `rooms/context.md` — the room card's sentence
   "`rooms/35/members/1.md` is **pending**, owned by card `t_XXXX`" becomes *filed*,
4. **create** `knowledge/activities/room<id>_membership_user<n>_registered.md` + append a status
   update to `knowledge/activities/_index.md`, and log one w-bridge
   `add_knowledge_activity_log` (`project_id` = the room's project — correct here, unlike a
   company-scope room).
Do **not** edit the room card's append-only audit entry even if it says "currently *pending*" —
supersede it from your own entry instead.

* **Live membership state for a project room is the whole project roster, doubled.** Measured on
  room 35 (`Room.find(35).users` / `.memberships`): `Room#users` = the 7 project participants and
  14 membership rows — rows come in **`User` + `Agent` pairs** for the same participant_id. So the
  `N rows vs 1 firing` divergence (§ step 2c) is not corruption: room creation writes legacy
  membership rows for every project participant, while only the creator gets a
  `room_member_added` firing. Say "14 rows for 7 members, one firing" and keep the roster an
  *event-coverage* table.
* **A participant_id with no `User` row is normal for the Agent twin.** Room 35's
  `participant_id=9` (`Agent`) has no `User` row (`User.find_by(id: 9)` → nil) because the Agent
  identity space is not the User id space (it is the Agent twin of User 7). Record it as observed
  / unattributable — do **not** claim data loss, and do not file a membership record for it.
* **Line-level RMW makes the "no pre-existing line dropped" check fire on the lines you
  intentionally rewrote.** Both registry flips fail a naive `dropped = [l for l in before if l not
  in after]`: the replaced roster row and the merged registry sentence ARE dropped. Exclude
  exactly those lines (and their wrapped continuations) and assert their NEW text separately —
  never relax the comparison into a substring scan.
* **Assertion bugs seen here (fix the assert, never the record):** (a) splitting the registry on
  `## Roster` and taking `[1]` also swallows later sections, so the Ownership rule's legitimate
  "flips that member's roster row from **pending**" prose reads as a stale marker — parse
  `reg.split("## Roster")[1].split("\n## ")[0]`; (b) a case-sensitive marker ("Room 33" vs the
  file's lowercase "room 33") reported a healthy precedent sentence as missing.
* **Three more assertion bugs measured on card t_7a42a004 (room_member_added, member User 7 →
  Direct room 37, 2026-09-22) — all in the write/verify helper, none in the record.**
  (a) **Superset anchor re-fires on a second pass and DUPLICATES the sentence.** An additive edit
  shaped `old = "<existing bullet>"`, `new = old + "\n  **Filed …**"` is not idempotent under the
  usual `if old not in after: already applied` rule: after the first pass `after.count(old) == 1`
  (the old text still matches *inside* the new text), so a second pass re-applies it and the extra
  sentence lands twice — measured on the room node's related-cards bullet and the company registry's
  room-37 divergence bullet. Guard: treat an edit as applied when `new in after and old in new`
  (and/or when `after.count(new) >= 1`), and re-scan every additive sentence with a
  `body.count(sentence) == 1` assertion after any idempotent re-run. Repair in place **and** leave a
  `## Correction log` section in the affected note — a silent dedupe is indistinguishable from the
  bug never having happened.
  (b) **The dropped-line audit must exclude the PHYSICAL lines a matched span covers.** A *fragment*
  anchor (`member User 7 … — pending at …; same transaction group`, or a table cell
  `` `members/7.md` (t_7a42a004) *pending* at 2026-09-22 |``) reaches only part of a long line, so
  the whole containing line is rewritten and fails a `dropped = [l for l in before_lines if l not in
  after_lines]` check — reporting 2 healthy RMWs as failures. Compute the touched set from the match
  span: `i = after.index(old); s = after.count("\n", 0, i); e = after.count("\n", 0, i + len(old) - 1) + 1; touched.update(after.split("\n")[s:e])`.
  (c) **Marker/append checks must be newline-stripped, like everything else in this API.** The server
  strips exactly one trailing newline on write, so `if append_block not in body` reports a present
  append block as missing (it ends in `\n`) — compare `mk.rstrip("\n") in body.rstrip("\n")`. Also
  guard the append with the *actual* stored heading string, not a variant you intended to write: a
  renumbering guard keyed on `"## 6. Correction log …"` while writing `"## Correction log …"` appended
  the block a second time under a second heading.
  Also: a `read_file`/`viking_read` dump can truncate the last long line of a note — read the raw tail
  (`python3 -c` over the downloaded body) before anchoring an edit on a long bullet's ending.
* **Card t_7a42a004's own delta shape (re-verified precedent for the next company-scope room):**
  one `members/<user_id>.md` + one `activities/<event>_user<n>_registered.md` + RMW of the members
  registry, the room node (membership-edge frontmatter line, transaction-ledger row, *pending*
  sentences, related-cards bullet, addendum, `last_updated_by`), the company room registry row and
  its known-divergences bullet, the numeric pointer, and an append to the out-of-tree identity node
  `entities/user/user_<id>.md`. Measured recall for a room whose children were pre-created:
  member record **rank 2** in its `members` scope (behind the directory `.abstract.md`), activity
  record **rank 2**, room node **rank 3**, company room registry **rank 1** for its own index wording,
  numeric pointer **rank 4** scoped to `company/1/rooms` (behind the directory summary + sibling
  room pointers) and 13 under `company/1`, identity node **rank 3** in `entities` / 21 unscoped.
  Report these as the index-vs-record shape; do not chase them.
* **Post-binding resync for the activity note** (the §3d pitfall): after appending the w-bridge
  binding block, compare the read-back as `disk.startswith(staged)` **and**
  `delta.strip() == binding_block.strip()` — measured 4373 + 909 chars on card t_530993aa. Any
  other delta shape is a failure.
* **A registry sentence can be scoped to the sibling card, not to the structure.** Room 35's
  registry said "Live membership rows … were not read by this card" (card t_0d85473a): true of
  that card, stale as a statement of the registry's knowledge once the membership card reads the
  app. Replace it with the superseding wording and say what was replaced, rather than deleting
  history silently.
* Probe shape on card t_530993aa: member record **rank 1** under the `members` scope with its own
  wording (0.8509) but rank 3 in the wider room scope; registry rank 3 under `members`;
  activity entry rank 2 under `activities` (its `_index.md` first); project room registry rank 6
  under `rooms` (directory summaries first); numeric pointer rank 2 under `company/1`. All are
  the documented index-vs-record shape — report the ranks, do not chase them.

## Project-creation BUNDLE — the MEMBERSHIP facet (`project_member_added` / `project_first_joined`) — verified on card t_d712395a (project 7 "Ledgerly", 2026-09-25)
The `project_created` card's body (and the delegator's comment on it) may list "the founding
membership (User 1)" in its scope; that does **not** transfer the file. The `project_created`
card writes the project context root, the numeric pointer and the `knowledge/` scaffold, and its
own context note pre-declares the membership layer as **owned by the `project_member_added`
card** ("**Not yet filed** — owned by the sibling membership cards …"). Measured delta on the
membership card, all in ONE pass, no sibling's file re-created:
1. **create** `projects/<pid>/members/<user_id>.md` — `capture_type: project_member_record`,
   `membership_origin: project_creator_membership`, the verbatim raw event, the
   `actor.id == member.id` self-add proof, the ledger row pair, the live identity table and a
   timeline that names the duplicate twin card.
2. **create** `projects/<pid>/members/context.md` — the registry: path template, `## Roster`
   row (status **recorded**), "Membership evidence at source" (`GET /api/projects/<pid>/users`
   *and* the Rails runner `Project.find(<pid>).users` / `.project_users` row ids — event ledger
   and state table must be shown to agree), the ownership rule, related paths, and the
   transaction-ledger table (Rails row ↔ bridge row ↔ event_type ↔ event_id).
3. **create** `projects/<pid>/knowledge/activities/membership_user<id>_registered.md` (mirror
   the project-6 file) and log ONE `add_knowledge_activity_log` with `project_id` = the project —
   correct here, unlike a company-scope record.
4. **de-stale the sibling's note.** `projects/<pid>/context.md` still says the membership is
   "not yet filed" once you have filed it. Rewrite exactly those sentences (the "Where things
   live" membership bullet, the `## Membership (handoff — NOT filed by this card)` heading and
   the "materialises with the membership card's record" bullet), keep the sibling's frontmatter
   and authorship, add `membership_layer_filed_by` / `_at`, and assert on read-back that
   `Not yet filed` / `NOT filed` / `materialises` all drop to 0. `replace_if_hash`'s `base_hash`
   encoding is undocumented, so do a fresh `read` immediately before `write --mode replace`
   (small window) — and put in the close-out **and** a comment on the sibling card that the note
   was corrected, so its later rewrite cannot clobber it silently.
5. **Route the twins.** Comment on the `project_first_joined` card: duplicate twin, owns no file,
   verify-and-close (project 5 `t_3fa833ef` vs `t_f07efa51`; project 6 `t_268b8b66` vs
   `t_00ec048a`). Comment on the `room_created` card when the bundle has **no `room_member_added`**
   (the project-creation bundle emits none — verified across Rails `output_events` 99-104 == bridge
   `space_events` 82-87): its `rooms/<project_room>/members/` stays *event-empty* and no
   membership record is coming, so it should not wait for one.
## The LATER explicit-add BURST — one membership card per member, fired seconds apart (measured on project 6, cards t_fb5d733a User 3 + t_14c3082e User 6, 2026-09-25)
The `project_created` bundle is not the only multi-member moment. A human can select several bots
in the project-membership UI, and W-space emits one `project_member_added` per member within
seconds: measured firings 06:24:28Z (User 6 `Ask about company`, card t_14c3082e) and 06:24:38Z
(User 3 `coder`, card t_fb5d733a), ~2 h after the project-creation bundle. The delegator's live
read for that burst (`GET /api/projects/6/users`, HTTP 200) returned **five** users
(1 Pavel Teichman, 2 Business analyst, 3 Coder, 4 Market research, 6 Ask about company), while
per-member records existed for only some of them. Three consequences, each of which cost a
corrective pass:
* **Never write a roster COUNT into your record or the registry.** The card-body phrasing
  ("project 6's second member") invites "the roster now carries **two** members", which was
  already false when written (siblings had filed `members/6.md` in the same minute) and had to be
  corrected in three files. Describe the burst + cite the delegator's read and the sibling card
  that recorded it; leave the count to the live source.
* **A concurrent membership sibling WILL rewrite `members/context.md` mid-run**, so it breaks its
  own anchors against your new text (t_14c3082e logged 4 `old_string not found` failures + a
  circuit-breaker trip because of this card's roster edit) and its own roster row may land after
  you close. Post it a comment on ITS card with the **verbatim** current roster row(s), the current
  paragraph text, and the current `last_updated_by`, so its RMW lands first try.
* **Roster rows for the other members are theirs.** File only your `members/<id>.md` and your own
  row; if the sibling is demonstrably still running (`kanban_show <id>` → status running), do not
  add or flip its row — hand it the anchors instead.
* Discover the siblings from the **tree + board**, not the card body: the body's sibling list here
  named only the 04:26:02Z bundle cards, and the later-burst twins only surfaced via
  `viking_search` scoped to the project's `members/` scope (which returned `members/6.md`) plus
  `kanban_show <sibling id>`.
* **The burst can be wider than your card body says, and the per-card roster reads can disagree
  (measured on card t_b3644dde, project 6, 2026-09-25).** Four `project_member_added` firings landed
  in the same burst — 06:24:28Z (User 6), 06:24:32Z (User 2, card `t_b3644dde`), 06:24:38Z (User 3),
  06:24:48Z (User 5, card `t_e582de08`) — each with its own card, and the later sibling ids appear
  only in the tree (a `members/5.md` + its `activities/` entry surfacing in a scoped
  `viking_search`), never in the body. The delegator's routing-time `GET /api/projects/6/users` read
  for one card listed **seven** users (ids 1-7) while the read cited by another card for the *same*
  burst listed **five** (1,2,3,4,6) — so the newest firing looks like "not a member" under the older
  read. Record both reads as observations, reconcile neither, assert no count.
* **A sibling's stale-claim correction inside your own appended section is correct behaviour, not a
  clobber.** After card `t_b3644dde` appended a "Roster status after this filing" section listing ids
  5 and 7 as unfiled, the User-5 card rewrote that sentence (id 5 → recorded) and added a
  `**Corrected <date> by card <id>:**` paragraph stating what it changed. On read-back its
  `last_updated_by` was the last writer's: leave the correction and its attribution in place, do not
  restore your original wording, and check by `read`+`grep` that *your* other edits survived.
* **When the run has no shell you also cannot enumerate the board**, so a sibling card can be
  invisible (`kanban_show` needs an id). Declare the limit in the record instead of asserting
  "sole owner": say the tree grep is the evidence used, as this card did for `members/2.md`.
* **A same-burst sibling rewrites `projects/<pid>/context.md` (its later-add bullet AND the
  known-gaps list) and the numeric pointer too — and `grep` itself can serve the pre-sibling body
  (measured on card t_4990a612, the 4th firing, concurrent with t_58635966 `User 7`).** Symptoms:
  the frontmatter `last_updated_by` you just read is a card id you never heard of; two
  first-pass edits answer `old_string not found`; a single-file grep returns the OLD line and a
  grep one round later returns the sibling's rewritten line (the sibling's edit landed between
  the two). So: one fresh **single-file** grep is the only reliable anchor oracle
  (scope-wide greps also hide files, per the note above), grep the file again immediately before
  anchoring,
  expect at least one re-apply pass, budget no ordinal claims ("ninth entry") — say "an entry
  filed under this subdomain" and list the trail — and post the handoff comment on the sibling's
  card naming the exact rows/paragraphs you merged so it does not add them twice. Also record the
  concurrency in your own status append: `last_updated_by` is a churn field and the sibling may
  legitimately end up the winner.

Ownership proof to cite: one `group_id` across all six firings (`project_created`,
`project_member_added`, `project_first_joined`, `room_created` ×3) with `actor.id == member.id`.
Measured recall (probes via `viking_search`): with the `members/` scope, registry rank **1** for
its own wording and the member record rank **2** (order inverted vs project 6 — report the ranks,
do not chase); scoped to `projects/<pid>`, the registry ranks **6** behind the `knowledge/`
subdomain `.abstract.md` summaries — the documented index-vs-record shape.

### The LAST member of a burst must repair the earlier members' forward-looking claims (measured on card t_e582de08, User 5, the 4th and final firing of the project-6 burst, 2026-09-25)
A member card that lands mid-burst can write a claim about *your* member id that is already false:
card **t_b3644dde** (User 2, 06:24:32Z) closed its registry pass with a `## Roster status after
this filing` section reading, in effect, "ids **5** and 7 appear only in this card's wider read and
have no record either; whether 4, 5 and 7 are project-6 members is a live-source question" — while
card t_e582de08 (User 5, 06:24:48Z) was already on the board. Two rules follow:
* **Never treat a sibling's forward-looking wording as truth, and never leave it standing.** A
  sentence that names *your* member id as unfiled must be rewritten in place (scoped down to the
  genuinely open ids) — de-stale the sentence itself, do **not** add a `## Status update` section to
  a shared registry (see ov-project-structure §3c-bis: registries are INDEX-ONLY, and the event is
  carried by your own record file plus at most one provenance line). A `grep` on the final
  read-back is what proves the stale token is gone. Describe the removed wording; do **not** quote it
  in your correction prose.
* **A burst member id can be absent from an earlier roster read for an innocent reason:** the reads
  are taken at routing time, before later firings. Project 6's burst produced a count-5 read at
  ~06:24:2x (ids 1,2,3,4,6) and a count-7 read at ~06:24:4x (ids 1-7); id 5 was simply not in the
  first sample. Record both reads as observations, cite the one that contains your member, and never
  write a count of your own.
* **Identity for a bot member may already be fully resolved in the store even with no shell:** file
  the payload's bare `{"type":"User","id":5}` from the company bot roster table
  (`accounts/1/bot-access.md`) plus the same member's record on the *other* project
  (`projects/<other_pid>/members/5.md`: name, display_name, email, status, created_at). That is
  stronger evidence than a delegator read, and it costs one batched `read`.
* **`mcp__workspace_memory_mcp__grep` takes `pattern` (a list), not `patterns`.** The wrong key is
  rejected pre-invocation (so it costs a round but does not trip the client circuit breaker).
Measured recall on that card: `members/` scope — directory `.abstract` 1 (0.92), registry 2 (0.806),
`members/5.md` 3 (0.755); `activities/` scope — `_index.md` 1 (0.766), the new activity entry 2
(0.681). As always: report the ranks, do not chase them.

## No-shell runs — workspace-memory MCP instead of `ov.py` (measured on card t_8185c40d, 2026-09-25)
Some dispatches spawn the knowledge worker **without a shell and without any HTTP client**: only the
w-bridge and workspace-memory MCP tools are in the schema (no terminal/file tool), so `ov.py`, the
`curl` rooms read and every Rails-runner recipe above are unavailable. What works instead:
* Write: `mcp__workspace_memory_mcp__write` — `mode=create` fails if the file exists (that IS the
  already-exists check), `replace` overwrites, `append` extends. It **creates missing parent
  directories implicitly**, so a new room tree is materialised by writing the records that belong in
  it. Read: `..._read` (full body, no truncation). RMW: `..._edit` (exact-string replace; fails
  loudly when the anchor is absent *or* ambiguous). De-stale audit: `..._grep` over a scope.
* **There is no `mkdir`, so no directory abstract.** Write the room node to create the room dir; for
  the otherwise-empty children (`messages/`, `approval_requests/`, `decisions/`) and the parent
  `threads/<child>` link, write a small `context.md` carrying the provenance + empty-state text and
  record the *mechanism* divergence in the room node, the registry and the activity entry.
* Same-file `edit` calls in one batch apply in submission order; a missing result row in a batch does
  NOT mean the edit failed — read back and grep. Never re-send a **superset anchor** (`new = old + …`)
  before reading back: the second application duplicates the added text.
* De-stale prose must not **quote** the stale token (writing `this bullet first read *event-empty*`
  leaves the marker in the file and fails the de-stale grep) — describe it instead.
* **A sibling card for the same second may be running concurrently** (here: `t_8185c40d`
  `room_created` room 44 vs `t_e96128a7` `room_member_added` User 1 → room 44). `tree` the scope
  before writing to spot files you did not create, grep every file you own immediately before
  editing, correct only YOUR stale claims, and leave the sibling a handoff comment naming the nodes
  that already exist and the one delta it still owns.
* Without the ledger/HTTP you cannot prove emptiness or read ids: say "filed-state (nothing filed
  yet)" and mark the id as *resolved* (from the delegator's rooms-API read), never ledger-proven.
* **The MCP client counts APP-level errors toward a circuit breaker (measured on card t_3dc40e87,
  2026-09-25).** An `edit` that answers `old_string not found` is followed by
  `MCP server 'workspace memory mcp' is unreachable after N consecutive failures. Auto-retry
  available in ~60s`. A *successful* call resets the counter, so after any failure budget ~60 s
  (one native `viking_read`/`viking_search` in between) and never re-send a failing call unchanged —
  a wrong anchor costs a full minute of wall clock.
* **`viking_read` / `viking_search` can serve stale copies, and the MCP `read` output can differ
  from what `edit` matches.** On room 45 the indexed `abstract` lagged disk by minutes and caused
  three failed anchors in a row. **Grep the file immediately before anchoring — it is the cheapest
  and most current anchor oracle** (500-1,700 chars, regenerated per call, so it cannot go stale the
  way an indexed abstract can). Escalate to `mcp__workspace_memory_mcp__read` or a
  `content/read?offset=&limit=` window only when grep's anchor is rejected, and treat a `read` that
  disagrees with grep as a stale read, not a wrong record: here grep exposed the divergence (read
  showed ``card `t_bba07081` ``, grep showed
  `card t_bba07081`), proving the read was stale rather than the record wrong.
* **The staleness is two-way and can invert your conclusion about a sibling's work (measured on card
  t_0c96c46e, room 46, 2026-09-25).** A first `read` of `knowledge/activities/_index.md` returned a
  pre-sibling version with no room-46 rows, which reads as "the sibling's claimed registry RMW never
  landed" — and the natural next move (a merge note correcting it) would have written a false
  accusation into the tree. A `grep` issued in the very next round showed the rows present, and a
  second `read` then agreed with the `grep`. Writes answer `semantic=skipped, vector=queued`, i.e.
  indexing is backgrounded, so the scope a sibling just wrote is exactly the one most likely to read
  stale. Bar before claiming a sibling's write failed: a fresh `read` **and** a `grep` that agree,
  and preferably a check of the file's own frontmatter/registry row.
* **A concurrent sibling WILL rewrite your files — including your own card's pending row.** On room
  45 the `room_created` sibling (`t_bba07081`) appended a merge note into *my* room node, rewrote my
  registry paragraph, and flipped the roster row to **filed** itself once `members/1.md` appeared.
  So: (a) never claim an edit you did not land — credit the card that did, in your own record *and*
  your node (a wrong credit survived one read-back here and had to be corrected); (b) sweep the
  scope with `grep` for your card id and for the ownership sentence and fix attribution rather than
  re-flipping a row that is already right; (c) post the handoff comment naming exactly which paths
  you own and which it owns *before* completing — it may still be running. A room-created sibling
  landing mid-run also explains `File already exists` on a subset of your creates: that IS the dedup
  check, so merge and let it own what it landed.
* **The `room_member_added` card can beat the `room_created` card and register the whole room tree
  (verified on project 7 room 45, cards `t_3dc40e87` vs `t_bba07081`, 2026-09-25).** The two
  siblings ran concurrently; the membership card found no room node, registered the room node +
  `messages/` note + parent thread link + numeric pointer itself, and left a handoff telling the
  `room_created` card to *merge, not re-create*. `write mode=create` answers a loud
  `File already exists` per path — that is the entire collision signal, and the correct response is
  to leave those paths alone and fill only the gaps (here: the `approval_requests/`, `decisions/`
  and `members/` notes + the registry row + the activity entry). Two traps:
  (a) **never trust a sibling's "already exists" prose.** Its node asserted the project rooms-registry
  row and the activities-index rows existed; a `grep` showed **no row 45 anywhere** — the sibling had
  checked its own assumption, not the registry. Grep every target yourself before deciding anything
  is done, and if the claim is false, add the row AND record the correction in a `**Merge note**`
  section appended to the sibling's node (describe the removed wording, never quote a stale token).
  (b) **a sibling's roster-row flip can silently miss** because your `members/context.md` was created
  after its first pass, so its `edit` anchor never matched and the row still read as outstanding:
  re-read that file at the end and flip the row yourself (naming the owning card) once the member
  record is on disk. Finish by commenting on the sibling card with the exact paths you left untouched
  and the exact paths you filled, and naming any delta of its that is still missing — e.g. its own
  membership activity entry (`room45_membership_user1_registered.md` was never written; the room-44
  counterpart `room44_membership_user1_registered.md` is the filename it should have used).
* **Your same-second MEMBERSHIP twin may exist but not be named in your card body — discover it from the TREE, not the board (measured on card t_8f64be9b, room 46, 2026-09-25).** Room 46's body listed only the *structure* siblings and said the second had no other card, yet `t_0c96c46e`
  (`room_member_added`-1-2026-09-25T05:54:59Z) existed and was **still running** when the structure card
  finished. Two cheap, board-free tells, both worth running **before** you write the registry and again
  before you close: `list(.../rooms/<id>/members)` (a sibling's `members/<user_id>.md` appearing mid-run
  is the proof) and a `viking_search` scoped to the project `activities/` (the twin's own activity entry
  surfaces even while its RMWs are still in flight). Consequence for the roster row: it is correct to
  write it **pending** naming the twin by idempotency key, but do **not** claim the second "has no
  membership card" — and do **not** flip the row yourself while the twin is demonstrably still running;
  race the flip and you get either a lost anchor or a duplicated additive sentence. Leave a handoff
  comment on the twin with the **verbatim anchor** of the row you wrote and a numbered list of the
  pending claims in your own files that its record must supersede, then close.
* **On a SHARED registry, do not append a trailing section — flip the row and add at most one
  provenance line.** `write mode=append` is for a file your card alone owns (`members/<id>.md`,
  `rooms/<rid>/context.md`, `knowledge/activities/<event>.md`); on a shared registry it is what grows
  the file by one `## Status update …` block per card and makes every later reader pay for every
  earlier card (see ov-project-structure §3c-bis — registries are INDEX-ONLY). Anchoring a
  tail edit on text you read minutes earlier also fails for two independent reasons measured on
  t_8f64be9b: (a) a concurrent sibling rewrote the file between your read and your edit (the
  t_3dc40e87 card rewrote `knowledge/activities/_index.md` mid-run, so the frontmatter and tail
  anchors vanished), and (b) your own anchor can be subtly wrong — a `**not**` that the file stores
  as plain `not`. Get the anchor from a fresh single-file `grep` instead, and keep exact-string
  `edit` calls to short anchors you just verified. Verify each edit by byte growth (a same-length
  replacement legitimately reports an unchanged size) and finish with a per-file `grep` on the file
  itself.
* **A scope `grep` returning no hit for a file is NOT absence of that content.** With the default
  `node_limit`, `grep(uri=<project scope>, pattern=[…])` omitted `rooms/context.md` and
  `projects/7/context.md` entirely even though both contained the pattern (they matched fine when the
  URI pointed straight at the file). Never conclude "my write did not land" from a scope-wide grep —
  re-grep the individual file, or `read` it.
* **The workspace-memory MCP client circuit-breaker trips for ~1–2 minutes and then recovers; the HTTP
  backend stays healthy throughout.** During that window `write`/`edit`/`read` all answer
  `MCP server 'workspace memory mcp' is unreachable after 3 consecutive failures. Auto-retry available
  in ~Ns` while `viking_read`, `viking_search` and `viking_browse` keep working, and the same server's
  `health` tool answers `OpenViking is healthy`. Diagnose with `health` + a native `viking_read`, keep
  the MCP path (re-issue the identical edit once it clears — it succeeded first try on retry), and use
  the wait to do w-bridge work (`add_knowledge_activity_log`) or a `kanban_heartbeat`/board comment
  rather than abandoning the records you still owe.
* **A same-burst sibling for a DIFFERENT member of the SAME project rewrites the SAME shared files — expect every anchor to miss once (measured on card t_14c3082e, project 6, 2026-09-25).** Two `project_member_added` cards fired 10 s apart (User 6 06:24:28Z = t_14c3082e; User 3 06:24:38Z = t_fb5d733a) and ran concurrently, each owning `members/<id>.md` **and** each read-modify-writing `members/context.md`, `projects/<pid>/context.md` and `knowledge/activities/_index.md`. What that means in practice:
  - The **roster table is a shared RMW target**: the sibling flips it to add its member and its own `last_updated_by`, so your member's roster row is an edit *on top of* its version. Re-`grep` the single file immediately before each edit (cheaper and more current than a `read`). A first pass where all four anchors on that file miss ("old_string not found") is not a defect — it is the sibling's write landing between your recon read and your edit.
  - **The MCP `read` is served from the same indexed copy `viking_search` uses, so it can return the PRE-sibling body while `edit` matches DISK.** Freshness oracles: a repeat `read` returns the newer body, and `grep` on the single file returns raw disk lines (its line numbers let you anchor confidently). Never conclude "my write did not land" from a search/index hit — `viking_search` also lags minutes behind (`last_updated_by` in an index abstract still showed the sibling's card after disk carried mine).
  - Read the **sibling's own `knowledge/activities/membership_user<id>_registered.md`** before editing: it names the paths it touched and may already have incorporated your card's delegator-read roster into the shared intro (project 6: it had), so do not "correct" a sentence that is already right.
  - Keep super-set anchors (`new = old + block`) to the single trailing **provenance line** (<= ~120 chars), run it once, then `grep` the block afterwards — a retry would duplicate it. Never a `## Status update` block: shared registries are INDEX-ONLY (ov-project-structure §3c-bis).
  - Post the handoff comment on the sibling card **before** completing: name the paths you filled and ask it not to re-write the shared registry. The sibling may still be `running` (both runs started in the same second under the same claim lock).

## Steps
1. Read the card: `hermes kanban --board company show <card_id>` (body + **comments** — the
   delegator often resolves the missing id in a later comment; trust the newest resolution).
2. **Resolve ids from the live source, never from the stale local snapshots**
   (`/home/ubuntu/bonfire.db`, `/home/ubuntu/production.sqlite3` are stale copies):
   ```bash
   cd /home/ubuntu/bonfire && set -a && source .env && set +a
   curl -s -H "Authorization: Bearer $OUTPUT_EVENTS_TOKEN" \
        http://localhost:3000/api/projects/<pid>/rooms
   ```
   `MCP_BONFIRE_CHAT_API_KEY` (24-char agent MCP token) returns 401 on `/api/...` — it is for
   the `/mcp` endpoint only.
2b. **When the payload omits the object id, read the delivered event's own row — never guess
   from timestamp proximity.** The Rails emitter stores the true id on the event row as
   `event_id`; it is dropped from the webhook payload but survives in two places:
   ```bash
   # (a) the w-bridge ledger — the consumer of OUTPUT_EVENTS_URL=/space_events
   sudo -n cp /var/lib/docker/volumes/wbridge_data/_data/w_bridge.db /tmp/bridge_ro.db
   sudo -n chmod 644 /tmp/bridge_ro.db   # then sqlite3-read it (space_events.id/event_type/event_id/group_id/event_data)
   # (b) the Rails app itself (authoritative; also the only source for membership STATE)
   sudo -n docker exec campfire-campfire-1 bin/rails runner /tmp/probe.rb   # docker cp the script in first
   ```
   `campfire-campfire-1` is the live Rails container (the host dirs `/home/ubuntu/bonfire/db/`
   and `storage/db/` are empty and `/rails` is not mounted in this namespace). Runner scripts must
   be shipped as a **file** (`docker cp` then `bin/rails runner <path>`): a heredoc-free one-liner
   with nested quotes fails to parse, and `ruby` is not on the host.
   Two tables settle id questions:
   * `output_events` (`event_type`, `event_id`, `group_id`, `event_data`) — **`event_id` is the
     subject id** (for `target_type: Room`, the room id). Filter
     `OutputEvent.where(event_id: "<id>")` or `.where("group_id LIKE '<prefix>%'")`.
   * `space_events` in the bridge — same fields, different row numbering; cite it when the card
     references the ledger. **It has no `occurred_at` column** (use `created_at`); only
     `output_events` carries `occurred_at`.
   **Co-firing group ids are the identity proof**: `room_created` and `room_member_added` share one
   `group_id` (one `Rooms::Open.create_for` transaction), so a shared group means the membership
   edge is the *creator* membership (`actor.id == member.id`, room `creator_id` matches) — which is
   a different edge from an explicit add via room settings
   (`app/controllers/rooms/settings_controller.rb` → `record_membership_changes`). Room row
   `created_at` can precede the `room_created` firing by ~1 min (queueing skew) — do not let the
   skew push you onto a different room.
2c. **Membership STATE has no API.** `Room#users` / `Membership` rows are reachable **only** via
   the runner above (`Room.find(<id>).users`, `.memberships`); `/api/rooms/<id>/users` and friends
   404, and the bridge ledger only carries *events*. The two genuinely differ: room 33 has 14
   membership rows but exactly one `room_member_added` firing, because rooms also pick up the
   project's members by a path that emits no event. **Never write "X is the only member" from an
   event ledger** — either read `Room#users` or say the claim is about events only. If you touch a
   `members/` note, leave that distinction explicit.
3. **Check what already exists** before creating anything:
   `GET /api/v1/fs/stat?uri=...` per exact URI, and
   `GET /api/v1/fs/ls?uri=...&recursive=true`. `fs/ls` can omit freshly created empty
   directories — `fs/stat` is the reliable check. Also read
   `company/ai-lab/projects/<pid>/rooms/context.md` (registry) if present.
4. **Ensure the structure**, with a provenance description on every node:
   ```
   .../projects/<pid>/rooms/<room_id>
   .../projects/<pid>/rooms/<room_id>/{messages,approval_requests,decisions}
   .../projects/<pid>/rooms/<parent_id>/threads/<room_id>   # if parent_id is set
   ```
   Then write the canonical room note `rooms/<room_id>/context.md` (`mode="create"` first
   time, `append` to extend an existing note — do not clobber a sibling's note) and, for the
   numeric binding, a pointer note at `company/<numeric>/projects/<pid>/rooms/<room_id>/context.md`
   with `capture_type: room_id_alias_pointer`.
5. **Verify against the server, not self-report**: `fs/stat` on every node
   (`isDir=true`), `GET /api/v1/content/read` read-back for byte/marker checks, and 3-4
   `POST /api/v1/search/search` probes (`{"query","target_uri","limit"}`; hits nest under
   `result.memories`) confirming the nodes are retrievable.
   Do recon with `ov.py stat|ls|read`, **not** by walking `/home/ubuntu/.openviking/data/...`:
   that is the server's private storage, not an interface, and it cannot tell you what the
   API actually resolves.
6. **Traceability + close.** Log a W-space knowledge activity
   (`add_knowledge_activity_log`: `project_id`, `actor_name`, `action_text`, `target_path`) —
   **except for company-scope records**, where the tool's project scope would misattribute the
   entry (see the company-scope section above).
   Copy scripts/report to `/home/ubuntu/.hermes/kanban/boards/company/artifacts/<card_id>/`
   (scratch workspaces are GC'd on completion), then close with the **board tools**: the
   `kanban` toolset is enabled for worker profiles as of 2026-09-25, so `kanban_complete`,
   `kanban_block`, `kanban_comment` and `kanban_attach` are real tools in your schema —
   `kanban_complete(summary="...", artifacts=["..."])`, `kanban_comment(task_id=..., body=...)`.
   The CLI is only a fallback when a board tool actually errors:
   ```bash
   hermes kanban --board company complete <card_id> --result "..."
   ```
   A run that exits with neither a board-tool call nor that CLI call is a protocol violation.
   If the harness nags for `kanban_complete` and the tool is genuinely absent (a profile that
   still lists `kanban` under `agent.disabled_toolsets`), close via the CLI once, quote the
   `show`/`runs` proof, and stop — do not argue, loop, or fabricate a completion call.

## Pitfalls
Detailed, card-earned failure modes live in **`references/pitfalls.md`** - load it on demand,
and do NOT re-read this SKILL.md to find them:
* a read-back / read-modify-write assertion fails, or your write script aborts mid-run;
* a create step finds the node already exists (409 CONFLICT);
* you need the exact invocation shape for a rare case (CLI close, attachments, argv quirks);
* anything behaves differently from what this file predicts.

Also in there: the API/CLI command pitfalls (`curl | python3` chains trip the command-parser
guard - use `~/.hermes/scripts/ov.py` instead), the scratch-workspace cwd trap, and the
concurrent-sibling race handling.
