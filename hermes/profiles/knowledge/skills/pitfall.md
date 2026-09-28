---
name: ov-wspace-lifecycle-registration-pitfalls
description: Failure modes for W-space/OV registration cards - load on demand.
---

# Pitfalls (load on demand)

Extracted from SKILL.md on 2026-09-25 to cut the per-view cost (the parent skill was
being read 8+ times per card at ~35-56 KB per view). The parent skill
(`ov-wspace-lifecycle-registration`) is still the entry point; load this file only when
one of its failure modes actually fires. These were paid for by real cards.

* **The RMW read-back assertion must tolerate the missing trailing newline (cost a false abort on
  card t_88d29f7b).** `content/write(mode="replace")` sends the buffer you read back from the
  server — which already lacks the final `\n` the server strips. So on an RMW,
  `got == after[:-1]` is **False** for a perfectly healthy write (`got == after` is the true shape;
  measured 12983 → 12983). It aborted the run *after* the room-node write had landed, leaving the
  registry/pointer/conventions steps un-run. Use
  `ok = (got == after) or (got == after[:-1])` **plus** `got.rstrip("\n") == after.rstrip("\n")`,
  and keep the create-mode check as `staged.startswith(got) and got == staged[:-1]`. Fix the
  assert, never the record.
* **Make the write script resumable — you will need it.** Two mechanisms, both cheap:
  (a) a `STEPS`/`DRY` env gate; (b) an idempotent RMW helper — if the old anchor's `count != 1` but
  *every* new marker is already present, print `ALREADY APPLIED — skipping` and return instead of
  asserting; and create-steps that **verify instead of rewrite** when `fs/stat` says 200
  (`got.rstrip("\n") == staged.rstrip("\n")`). Card t_88d29f7b lost 4 steps to a false assertion and
  recovered only because the second run was a no-op-verify for the landed steps.
* **The "no pre-existing line dropped" check has a THIRD failure mode: a replacement INSIDE one long
  physical line.** Registries and room nodes often keep a whole bullet/table row on a single long
  line; replacing a substring of it changes that one line, which then shows up in `dropped` while
  the old-string's own line list does not contain it (measured on card t_88d29f7b: registry reported
  `dropped 3, allowed 4` → 1 "unexpected" = the entire room-37 divergences bullet). Fix: for each
  replacement record the physical lines of the *current* buffer that the matched span touches
  (`after.rfind("\n", 0, idx)+1` .. the newline after `idx+len(old)`) and use that as the allowed
  set — it covers the multi-line-anchor case and this one. Assert on `UNEXPECTED`, not on counts.
* **`content/read` on a file you just wrote via RMW returns the buffer byte-for-byte** (no strip,
  because the server only strips a trailing newline that the stored copy does not have). Do not
  "fix" a healthy record because a length assertion says `read == staged - 1` is off by one.
* **The handoff phrase "flip your router row" means the room node's ledger table row for your
  card** (`| 89 | 72 | room_member_added | User 1 | User 1 | t_88d29f7b (not yet run at capture
  time) |` → `… — **filed** 2026-09-22, `rooms/37/members/1.md` |`). There is no OV "router" node:
  a probe for one in `company/ai-lab` returns only directory summaries. Flip the row, the
  related-cards bullet and the frontmatter `source_event_membership_edges` line for *your* card and
  leave the sibling cards' "not yet run at capture time" wording alone — it is still true.

* **A REST helper that tests `if "error" in r` treats every healthy read as missing.** The OV
  response envelope *always* carries an `error` key — `null` on success — so `"error" in r` is
  always True and `content/read` returns `None` for records that are actually there (cost a
  debugging detour on card t_0d85473a). Use `if r.get("error"):`. Also note the success shapes:
  `content/read` returns its body as a **plain string** under `result` (not a dict), and
  `content/write` returns `result.vector_status` / `result.content_updated` (`written_bytes` is
  absent) — log from `result`, not from the top level.
* **`DELETE /api/v1/fs?uri=<uri>&recursive=true&wait=true` exists and is the repair path.** It
  returns `result.estimated_deleted_count`. Use it to remove nodes a run created at a wrong path
  (the `{NS}/company/1/...` URI-prefix trap below produced 6 stray nodes on card t_0d85473a) or a
  probe file written while shape-checking an API; then `fs/stat` the removed paths and assert
  `NOT_FOUND`. **Record the repair** in the room/record note as a correction log — a silent
  delete makes the divergence indistinguishable from never having happened. The full endpoint set
  is discoverable at `GET /openapi.json` (`fs/ls|tree|stat|attrs|mkdir|mv` + `fs`, plus
  `content/*`, `search/search`) — check it before hand-rolling a workaround.
* **Any bullet-level insert or row flip must use the FULL bullet as its anchor.** Inserting after a *first line* whose
  bullet continues on an indented next line splits the original bullet and re-parents the
  continuation text under your new bullet (seen on card t_3898e963 in `company/ai-lab/context.md`:
  "Direct rooms carry no project scope…" ended up trailing the new registry bullet). Match the whole
  bullet, or re-check by index order afterwards; the set-based "dropped lines" check cannot catch
  this re-ordering, so assert `index(anchor_bullet) < index(continuation) < index(new_bullet)`.
* **Before writing anything, check whether an earlier run of YOUR card already wrote it.** These
  cards get re-dispatched after crashes/timeouts, and a run that exhausts its iteration budget
  **keeps every node it wrote** while leaving the card open (observed: card t_cf989b41's nodes were
  written by run #87 at 10:20–10:28Z, then the run timed out at 90/90 iterations without calling
 `complete`). Read the card's `show` events for prior runs, then `fs/stat` the exact target URIs:
  if they exist, **verify and correct instead of re-writing** — re-writing risks clobbering a
  sibling's note and burns the budget that closing the card needs. Budget the close (`artifacts/`
  copy, `attach`, `comment`, `complete`) as part of the work, not as an afterthought; a full OV
  write + read-back + probes can genuinely run 60+ iterations.
* Do not assert a *state* fact from an *event* ledger (see step 2c) — membership counts, "only
  member", "never happened" all need the live record, not the absence of a firing.
* When re-writing a note with `mode="replace"`, keep the old-wording assertion honest: a correction
  line that quotes the very phrase you then assert is absent will trip your own check (seen in
  t_cf989b41's registry fix). Assert on the body, not on your replacement text.
* `content/write` with `mode="replace"` → `NOT_FOUND` when the file does not exist yet.
  Use `mode="create"` for the first write, then `replace` on later writes. Reserve `append` for a
  file your card alone owns (`members/<id>.md`, `rooms/<rid>/context.md`,
  `knowledge/activities/<event>.md`); a shared registry is flipped row-by-row with `edit`, never
  appended (ov-project-structure §3c-bis).
* Never write the server's memory-fields HTML marker string literally inside a record body —
  the server strips it wherever it appears, silently mutilating that line.
* `curl ... | python3` and inline multi-command curl chains trip the command-parser guard.
  Do not hand-roll HTTP at all: use `~/.hermes/scripts/ov.py`
  (`write --verify`, `batch`, `read`, `stat`, `ls`, `mkdir`, `rm`). It resolves
  `OPENVIKING_API_KEY` from `$HERMES_HOME/.env` itself, so the old `source .env` step is gone
  too (that step alone accounted for 28 commands across 34 recorded cards).
* Prefer one `ov.py batch` over check-then-write sequences. The server enforces the
  preconditions: `create_if_absent` answers `409 CONFLICT ... target already exists` (that IS
  the "ALREADY EXISTS — do not re-create" signal, no read-back needed first), and
  `replace_if_hash` with the current `base_hash` guards a read-modify-write flip against a
  concurrent sibling. Verified live 2026-09-25: 2 ops in one round-trip, second identical run
  → 409 with the original content untouched.
* Concurrent sibling knowledge workers race on the same structure; re-check existence right
  before writing (a fresh single-file `grep` is the cheapest way to re-check, and it is the freshest
  oracle). On a **shared registry** (`members/context.md`, `rooms/context.md`, a project
  `context.md`, any `_index.md`) flip the row in place with `edit` and add at most ONE provenance
  line - do **not** keep appending narrative. Registries are INDEX-ONLY; narrative goes to the
  record file that event owns (ov-project-structure §3c-bis). The flip stays clobber-safe because
  the anchor is one line rather than a growing block.
* `POST /api/v1/fs/mkdir` on a node that already exists returns **409 CONFLICT** (e.g. the
 canonical `rooms/<id>` node created earlier by the convention-owner card). That is success,
  not failure — treat 200 and 409 alike and let the following `fs/stat` be the real proof.
* The worker's shell session cwd IS the scratch workspace, and `complete` deletes it, so every
  later shell command in the same session dies with `getcwd: cannot access parent directories`
  (and `cd` back into it fails with exit 126). Run the post-completion `show`/`attachments`
  verification with an explicit `workdir` (e.g. `/home/ubuntu`), not `cd`.
* If an empty-directory convention ("subdirs appear on first record") conflicts with your
  card's explicit "ensure the structure exists", follow your card, create the nodes, and
  record the divergence in the room's context note instead of leaving it implicit.
* **`fs/ls` returns its nodes as `result` = a LIST of node dicts, not `{"entries": [...]}`** (verified
  on card t_51db917e): `r["result"]["entries"]` raises `AttributeError: 'list' object has no
  attribute 'get'` and aborts the verify pass mid-run. Write
  `_res = r["result"]; ents = _res if isinstance(_res, list) else (_res or {}).get("entries", [])`.
  Same family as the `content/read`-returns-a-plain-string quirk — parse `result` by hand, never
  assume the envelope's inner shape.
* **`content/read` on a missing file is HTTP 404 `NOT_FOUND`, not `result: null`** (verified on
  card t_6f068477): `{"error": {"code": "NOT_FOUND", ...}}`. An idempotent "read-back, else
  create" helper must map 404 → `None` — otherwise the first write pass aborts before writing
  anything. Also, `content/read` on a **directory** URI returns **HTTP 400 Bad Request**: only
  read file URIs; use `fs/stat` for nodes without content.
* **`fs/mkdir` takes `{"uri", "description"}`** and the description becomes that directory's
  summary/abstract (this is how the sibling room children carry their provenance line). The
  description is plain text — it may contain `<user_id>` placeholders, which are stored literally.
* **Two cards can own one room.** `room_created` and `direct_conversation_created` fire inside a
  single `Rooms::Direct` creation transaction (same `group_id`; verified t_6f068477 ↔ t_3898e963,
  group `c2c66348…`, rows 49-50) and each firing gets its own card. The second card must NOT
  re-register the room: `fs/stat` the node, then deliver only the delta (for t_6f068477: the room
  `members/` resource + the `room_created` addendum) and **flip the first card's pre-declared
  handoff wording** — the sibling wrote "The room node it would register is this record" and
  "No `members/` node is created here", both of which become false. Use the §3g RMW shape: targeted
  `replace()` of exactly those sentences, report `dropped_lines` as the pass condition, add
  `last_updated_by`/`last_updated_at` to the frontmatter and `source_event_twin:` naming the twin
  firing, then re-probe the node (`rooms/<id>/context.md` ranked **1** at 0.8089 for
  "room_created firing for Direct room 34 registered by knowledge card").
* **Company-scope room membership: the `members/` resource is *usually* the `room_created` card's,
  but it lands with whichever lifecycle card first NEEDS it (verified on card t_88d29f7b, Direct
 room 37, 2026-09-22).** Room 37's `room_created` card (t_12ec6e42) was still `ready` when the
  member-User-1 card ran, so `fs/stat` on `rooms/37/members` and its `context.md` both returned 404.
  The predecessor card (t_d8a41fbe, the room node) had left an explicit handoff instruction: *"if it
  is absent when you run, create `members/context.md` with a roster row per edge"* — so the
  membership card `mkdir`s the resource, writes `members/context.md` with
  `established_by: knowledge (card <yours>)` + an `established_because:` line naming the undispatched
  room card, and a roster row per edge (**its own row filed**, the sibling edge *pending* against
  its card), then files its own `members/<id>.md`. Supersede the room node's "`members/` is left to
  card t_<room_created>" sentence and the registry's "owns the `members/` resource" claim with a
  dated **Superseded** sentence (they are dispatch state, not rules), and add the refinement to
  `infra/ov-memory-structure-conventions.md` §2e (t_88d29f7b added the paragraph "Which card creates
  the `members/` resource"). Still true: never a second `members/` resource, never a second room
  node; the `room_created` card arriving later verifies with `fs/stat` and files only its facet —
  leave it a handoff comment saying so. Verified record shapes for this card: `members/1.md`,
  `members/context.md` and `activities/room_member_added_user1_registered.md`; mine used
  membership id 361 (live `Room.find(37).memberships`), rows 89/72, group `62b1b86a…`.
* Path for that resource: `/company/ai-lab/rooms/<id>/members/` (+ `members/context.md` registry),
  not under `projects/<pid>/`. Verify a room's live membership
  with `Room.find(<id>).users` / `.memberships` — Membership columns are
  `participant_id` / `participant_type` / `room_id` / `involvement` (there is **no** `user_id` or
  `member_type`; `m.user_id` raises `NoMethodError`). One creation transaction can emit **two**
  `room_member_added` firings (creator self-add + an explicit add — ledger rows 51 & 52 for room
  34, 85 & 86 for room 36). **CORRECTION (card t_c19347d2, room 36, 2026-09-18): do NOT assume the
  creator self-add edge is permanently uncarded.** Room 36's room card t_6b9b5929 wrote "no dedicated
  board card" and "no card writes it" for row 85 / bridge row 68, and the delegator then dispatched
  **t_c19347d2** (`room_member_added-1-2026-09-18T17:02:05Z`) for exactly that firing. So: carry a
  not-yet-carded edge as *known-but-unfiled* with its ledger evidence, but treat that as **dispatch
  state, not a rule** — and when your card owns such a self-add edge, flip the registry row, the
  room node's events table and its related-cards bullet (there are three places, grep for
  `uncarded` / `known-but-unfiled` / `no dedicated board card` before closing) and state the
  correction in your own entry rather than editing the sibling's audit record.
* **Company-scope room membership card — verified on card t_c19347d2 (member User 1 → room 36,
  2026-09-18).** Same delta shape as the project-room membership card (§ steps 1-4) minus the
  project activity log: create `rooms/<id>/members/<user_id>.md`, RMW the `members/context.md`
  roster row + addendum, RMW the room node (ledger row, membership addendum), RMW the company room
 registry and the numeric pointer, and optionally create the out-of-tree identity node
  `entities/user/user_<id>.md` **if recon shows none exists** (user_1.md did not exist; user_4.md
  existed and was only appended). Self-add facts: `actor.id == member.id` **and** the room's
  `creator_id` matches the member — say both. The delegator's comment asked for "ONE membership
  resource with both member edges": honour it by having the single `members/` registry carry a row
  per edge (`1.md` + `4.md`), not by opening a resource per event.
  - **Probe calibration for a room whose children were pre-created.** In the `members` scope the
    `.abstract.md` directory summary and the registry `context.md` outrank the leaf record, so
    `members/<id>.md` measures **rank 3** (0.68-0.77) for its own wording — assert 3, not 1. In
    `activities`, a sibling record with near-identical wording takes rank 1 and yours takes **rank
    2**. In the room scope the node measures 2 (supersede wording) to 6 (addendum wording, behind
    three child `.abstract.md`). The numeric pointer measures **rank 9** under `company/1` (sibling
    project-room numeric records lead) and the out-of-tree identity node 3 in `entities/user` / 8 in
    `entities` — and is unreachable unscoped (36 `.abstract.md` hits first). Report these ranks as
    the index shape; do not chase them.
  - **Measured ranks for the room-37 shape (card t_88d29f7b, 2026-09-22, where the card created the
    `members/` resource itself).** Member record **2** in the `members` scope (behind
    `members/.abstract.md`, 0.88) and the registry also **2**; activity record **1** in
    `activities/`; room node **3** in the room scope (behind two child directory summaries); company
    room registry **6** in `company/ai-lab/rooms` (child summaries lead — assert 1-6, not 1);
    conventions doc **1** in the `infra` scope. The numeric pointer measures **4** scoped to
    `company/1/rooms` — behind its own directory summary `37/.abstract.md` (0.8835) and the sibling
    room-34/36 pointer records — the *pre-existing* shape for that scope (probe it before and after;
    it was unchanged by this write). Assert in-scope ranks with the record's own wording and record
    the directory-summary leader honestly.
  - **Assertion bugs that bite on this exact card shape:** the room node's note says "**R**egistered
    once, by card …" (capital R — a lowercase anchor fails a healthy write), and a sibling marker
    written as `card t_51db917e (company board)` misses the file's `kanban_card: t_51db917e (company
    board)` (colon, not space). Fix the assert, never the record.
* **After `complete` the scratch workspace is deleted, so the shell cwd dies and `write_file`
  starts failing with `[Errno 2] No such file or directory` for every path** (any path, not just
  relative ones). Before the post-close steps, run one `cd` to a surviving directory via terminal
  (`cd /tmp/<card dir>`) to reset the session cwd; better, stage every script under `/tmp/`
  from the beginning.
* **Company-scope `room_created` card running LAST (verified on card t_12ec6e42, Direct room 37,
  2026-09-22).** Room 37's ordering is the room-34 one: `direct_conversation_created` (t_d8a41fbe)
 landed the node first, the two membership cards next, and the `room_created` card last — the
  mirror image of room 36. The last card's delta is exactly one **created** record plus RMW of four
  shared notes, and each RMW must be resumable (an earlier run of your own card can leave steps
  applied; the idempotency guard then reports ALREADY APPLIED and the run still verifies):
  1. CREATE `rooms/<id>/activities/<event>_event_registered.md` (`activity_type: room_creation_registration`,
     `source_event_rails_row` / `source_event_bridge_row`, `idempotency_key`);
  2. RMW the room node — frontmatter `source_event_twin` (de-stale its *not yet filed* clause), the
     transaction-ledger table row for your rails/bridge row pair, the related-cards bullet, an
     addendum section inserted **before** `## Room content`, `last_updated_by`;
  3. RMW the company registry — its room row **and** its known-divergences bullet;
  4. RMW `rooms/<id>/members/context.md` — **yes, this file too**: the registry carries the same
     four-row transaction ledger and its `room_created` row is written as `<card> (not yet run)`, so
     flip that row + a dating note + `last_updated_by` there as well (still never a second `members/`
     resource);
  5. RMW the numeric pointer (prospective -> filed sentence) and `infra/ov-memory-structure-conventions.md`
     §2e (the later-arriving-twin rule).
     No `add_knowledge_activity_log`, no second room node, no `threads/`.
  - Measured ranks for this exact delta (card t_12ec6e42): activity record **2** in the `activities`
    scope (0.834, behind the directory `.abstract`), room node **2** in the room scope (0.834),
    company room registry **1** (0.731) for index-own wording, members registry **2** (0.779),
    numeric pointer **4** scoped to `company/1/rooms` (behind that dir's `.abstract` + the sibling
    room-34/36 pointers), conventions doc **1** (0.767) in `infra`. Report these; do not chase them.
  - **Ledger evidence you can re-read first-hand (cheap, and it is the claim's proof):**
    `sudo -n cp /var/lib/docker/volumes/wbridge_data/_data/w_bridge.db /tmp/...` then read
    `space_events`. Its columns are `id, space_event_id, event_type, event_id, group_id, event_data,
    created_at, stored_date, sent_date, result, dedupe_key` — there is **no** `occurred_at` column
    (it lives inside `event_data`), `space_event_id` is the Rails `output_events` row, `id` is the
    bridge row, and `dedupe_key event:<type>:<rails_row>:<hash>` is a third independent identifier.
* **A preserved-anchor (`KEEP`) marker must be copied from the file, not from your head.** A KEEP
  entry written as `` `rooms/<id>/messages/492.md` `` aborts a *successful* RMW — the path sits inside
  a fenced code block, so the stored text carries no backticks — and because the marker check runs
  *after* the write + read-back, the abort looks like a record fault while the write has in fact
  landed. Same family: a code block writes the room path with alignment spaces, so anchor on a
  distinctive *word sequence* ("message capture, card t_b05e731b"), never on whitespace. Fix the
  assert, re-run, and let the idempotency guard turn the remaining steps into ALREADY APPLIED.
* **Your own new record must not contain the literal stale-marker strings.** The activity record for
 t_12ec6e42 quoted the wording it had replaced ("not yet filed at capture time") and the end-of-run
  stale sweep then flagged *your own new file*. Describe the replacement in prose ("a capture-time
  *not-yet-filed* / *not-yet-run* placeholder"), and keep the hyphenated form when a quoted flip is
  genuinely useful; the bare space-separated strings are what the sweep greps for.
* **A DRY-run gate must also skip the read-back verify.** With `DRY=1` nothing is written, so a
  post-write read-back comparison necessarily mismatches; return right after logging the intended
  byte delta, or the dry run can never exercise the anchors it exists to validate.

