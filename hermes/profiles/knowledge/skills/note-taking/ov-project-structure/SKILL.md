---
name: ov-project-structure
description: Use when a W-space card needs OV structure built or aligned.
platforms: [linux]
---

# OpenViking structure build (knowledge profile)

Use this when a kanban card assigned to `knowledge` asks to **build or align the OpenViking
(OV) structure** for a W-space lifecycle event — e.g. `project_created`, `room_created`,
`project_member_added`, `account_settings_updated`. The deliverable is memory records at the
canonical paths, written and independently verified — not a plan describing them.

## 1. Recon before writing (never skip)

1. Read the card: `hermes kanban --board <board> show <card>`. The body carries the raw event
   and the required paths.
2. Read the current OV tree so you match convention instead of inventing:
   `viking_browse(action="tree", path="viking://user/hermes/memories/company")`.
3. Resolve entity facts that the event payload omits **from the originating cards**, not from
   guesswork. `room_created` payloads, for example, omit the room id; sibling cards resolved
   the room table from `GET /api/projects/<id>/rooms`. Reading the already-resolved facts out
   of those cards' `show` output is faster and safer than re-querying.
4. Check for sibling cards that already own part of the work. The board has hit duplicate
   dispatches before; register what is yours, and record the handoff in your comment instead
   of redoing another card's work.

## 2. Company id: numeric vs slug (the trap in this deployment)

W-space event payloads carry the **numeric** company id — `knowledge_path: /company/1/projects/5/knowledge`.
The established OV company root uses the **slug** — `/company/ai-lab` (see
`memories/company/ai-lab/context.md`). Convention for this deployment:

- `ai-lab` is canonical. **Never** build a parallel tree under `/company/1/` — a single-rooted
  namespace is required for cross-profile knowledge sharing.
- Satisfy numeric-path expectations with one small pointer note at
  `/company/1/projects/5/context.md` that maps to the canonical tree.
- Record the mapping in the project context note and in the card metadata.

## 3. Path templates

```
/company/ai-lab                                   company root (context.md)
/company/ai-lab/projects/<pid>                    project context root
/company/ai-lab/projects/<pid>/knowledge          namespace index
/company/ai-lab/projects/<pid>/knowledge/{items,external-assets,directory-items,
                                          obsidian-notes,activities,adrs}/_index.md
/company/ai-lab/projects/<pid>/rooms              room registry
/company/ai-lab/projects/<pid>/rooms/<room_id>    per-room node
/company/ai-lab/projects/<pid>/rooms/<rid>/messages|approval_requests|decisions
/company/ai-lab/projects/<pid>/rooms/<parent>/threads/<child_room_id>
/company/ai-lab/projects/<pid>/members            membership registry (context.md)
/company/ai-lab/projects/<pid>/members/<user_id>.md   per-member record
```

Company-scope **attention state** (company-home queue; no room, no project) has its own subtree —
see the attention section in `ov-wspace-lifecycle-registration` and OV convention §2f:

```
/company/ai-lab/attention/context.md                                 index + conventions
/company/ai-lab/attention/categories/<category>/context.md           category node (canonical PLURAL key)
/company/ai-lab/attention/categories/<category>/items/<item_id>.md   one record per AttentionItem id (STATE)
/company/1/attention/context.md                                      numeric pointer
```

### 3b. Membership records (`project_member_added` / `project_first_joined`)
Membership must not live only as prose in `projects/<pid>/context.md` or only as kanban
cards. Each member gets a record under `projects/<pid>/members/<user_id>.md` carrying:
`member_type`/`member_id`/username, the acting user and `actor_is_member` (self-add is real —
a creator adding themselves has no separate inviter), the source event
(`project_member_added` vs `project_first_joined`) and its `occurred_at`, plus the
originating card. A `members/context.md` registry holds the path template, the roster table
and the ownership rule.

Ownership rule: write **only** the member your card owns, and list the others in the registry
as *pending* with their owning cards. Two workers filing one membership is a defect; the
W-space event is the proof of membership, the record is only the filing.
Membership content belongs in `members/` (it is a project entity, not a knowledge item); log
the filing action once in `knowledge/activities/` and once via w-bridge
`add_knowledge_activity_log` with `target_path` = the member record path.

### 3c. Refinements verified on card t_4f6d6d99 (User 5, project 5)
- **Flip the roster row, do not only append.** A `members/context.md` whose User-N row still
  says *pending* after you filed that member is stale documentation. Budget one
  **read-modify-write** with `mode=replace`: obtain the anchor with `grep` on a bare token from the
  row (`grep(uri=<registry>, pattern="members/<N>.md")` → ~500-1,700 chars, versus 23,000+ for a
  full read of this registry), re-grep immediately before writing (siblings race),
  `replace()` the one row line, concatenate your additive section, then assert
  (a) every pre-existing non-blank line is still present **except the row you flipped**,
  (b) the new row text is present, (c) the appended marker is present,
  (d) `vector_status=complete`. Report the missing-line list in the write log — `missing ==
  [OLD_ROW]` is the pass condition and doubles as proof nothing was clobbered.
- **Name the bare ids from the live roster.** Event payloads carry `{"type":"User","id":N}`
  only. `GET /api/projects/<pid>/users` (bearer `$OUTPUT_EVENTS_TOKEN`) returns
  `id/name/display_name/email_address/status/created_at` for every project member — the same
  call names all sibling ids at once, so one fetch gives you the member's display name plus a
  "roster identity resolution" table worth adding to the registry as labelled convenience
  metadata (explicitly *not* a substitute for the sibling cards' records). In this deployment
  ids 2-7 are bot/agent users (`business analyst`, `coder`, `market research`,
  `project manager`, `Ask about company`, `Workspace`) and User 1 is the only human.
- **`memories/events/2026/09/18/` does not exist** in the store even though
  `members/1.md` and `projects/<pid>/context.md` reference it (checked with `fs/ls`; only
  `company/ai-lab/events/<date>_<event>_<HHMMSS>Z.md` company-scope records exist). Treat the
  `members/` node as the canonical membership home, note the dangling reference, and do not
  fabricate the missing path.
- Third-party add vs self-add: `actor_is_self_add` is `actor.id == member.id`. For project 5
  only the creator (User 1) self-added; every other member record must say third-party.
### 3d. Refinements verified on card t_4bc70740 (User 2, project 5)
- **Check for leftover work from crashed prior runs before writing.** This card had five
  reclaimed/crashed runs; verify `members/<id>.md` absent, the roster row still *pending*, and no
  `membership_user<id>_*` activity entry before writing, so the run is provably idempotent
  instead of a duplicate. The write script's `create` path already refuses to overwrite an
  existing record whose body does not mention its own card id — keep that guard.
- **The post-write w-bridge binding append breaks the staged-baseline comparison.** If you log
  the activity entry via w-bridge *after* the write and then `replace` the activity note to add
  the `## w-bridge binding` block (as `t_4f6d6d99` did), the staged file no longer equals the
  on-disk record and the verifier reports a false content mismatch. Either append the binding in
  the same write pass, or resync the staged baseline afterwards and assert the delta is exactly
  the binding block (`disk.startswith(staged)` + `entry id N` present), as `recheck.py` does —
  never loosen the comparison itself.
- **The numeric-alias pointer needs record-close probe wording.** `members/*` records rank 1 for
  member phrasings, but the `/company/1/...` alias note MISSES on abstract wording like
  "project 5 AI Lab numeric company id alias" (top hits come back as `.abstract.md` directory
  summaries) and ranks 1 on "/company/1/projects/5 -> canonical /company/ai-lab/projects/5
  numeric-company-id pointer" or "company id 1 equals ai-lab slug mapping for project 5 memory
  paths". Keep the missed wording in the script as a comment with its resolution — the fix was
  wording, not indexing.
- **CORRECTION (card t_9b1d6e27): the alias-note "miss" is a SCOPE error, not a wording
  error.** The pointer note lives at `company/1/projects/5/context.md` — **outside** the
  `company/ai-lab` scope. A probe with `target_uri=user/hermes/memories/company/ai-lab` therefore
  returns rank `None` for it no matter how good the wording is (observed with the exact
  "numeric-company-id pointer" string: 5 generic `.abstract.md` hits, rank None). Re-scope to
  `user/hermes/memories/company/1` (where it actually lives) or probe unscoped, and it returns
  **rank 1** (0.749/0.750) immediately. General rule: a `target_uri`-scoped probe can only ever
  return hits *under* that prefix — before declaring a "missing" record, check whether the
  record is even inside the scope you passed.

  ### 3e. Refinements verified on card t_54b6d101 (User 6, project 5)
  - **An identity node for your member may already exist and may already name your card.** Card
  t_54b6d101 found `entities/user/user_6.md` (filed 08:49, before its own run) already saying
  "project_member_added event (t_54b6d101 card created)". Do **not** rewrite or replace it:
  append the bot/human label, its evidence and the pointer to the now-filed
  `projects/<pid>/members/<id>.md`, and assert the original lines are still present (the
  entry-point wording to preserve is `**User ID:** N` plus the pre-existing `Bot status` line).
  The card's "identify whether the id is a bot or a human" requirement is satisfied in two
  places: `member_kind` + `member_kind_evidence` in the member record, and this appended block
  on the identity node.
  - **Prove idempotency when the card has a history of crashed runs.** Five reclaimed/crashed runs
  preceded this one; the recon step asserted `members/<id>.md` absent, the activity entry
  absent, `/company/1/.../members/<id>.md` absent and the roster row still *pending* before
  writing anything. Put that absence check in the write script's own log so the "this run is
  idempotent, not a duplicate" claim is evidence-backed.
  - **Bot-label evidence beats the roster alone.** `GET /api/projects/<pid>/users` gives the name,
  but the label comes from the account allow-list: an id present in *both* recorded
  `allowed_bot_user_ids` firings (`accounts/1/bot-access.md`) is an active bot, and if it is
  already in the earliest known firing plus `removed_bot_user_ids == []`, then account access was
  **not** granted on this card — say so explicitly instead of implying a new grant.
  - **`target_uri` scope bug** cost a full false-negative verify pass; see §5.4.

  ### 3f. Refinements verified on card t_9b1d6e27 (User 4, project 5)
  - **The identity node may be ABSENT — then create it, do not append.** Unlike §3e, this card
    found no `entities/user/user_4.md` at all. Same target path, opposite write mode: run
    `fs/stat` on the identity node in recon, and branch create-vs-append on the result. A
    create-path `no-clobber` guard (refuse if a body exists that does not mention your card)
    covers the case where recon raced a sibling.
  - **A verify assertion can be the thing that is wrong — fix it, never loosen it.** Two
    first-pass failures here were assertion bugs, not record faults: (a) a "does any recorded
    member still have a pending row" check that used `str.replace("| User 3 |", "")`, which does
    not remove a row whose text is `| User 3 | \`members/3.md\` (pending) | …`; (b) a roster row
    counter that also counted the *roster-identity-resolution* table further down the same
    document, so 7 rows read as 14. Parse the roster section explicitly
    (`reg.split("## Roster (as of …)")[1].split("\n## ")[0]`) and assert on the derived id sets
    (`pending_ids == ['3','7']`, `recorded_ids == ['1','2','4','5','6']`) instead of substring
    surgery. Keep the comparison itself strict.
  - **Out-of-tree identity nodes need their own probe phrasing.** `entities/user/user_4.md`
    ranks `None` for `"User 4 market research bot agent user"` and for the bare `"User 4"`, but
    **rank 3** for `"market research bot identity node outside the company tree"` (0.768) and
    **rank 1** scoped to `user/hermes/memories/entities`. Probes on out-of-tree nodes should
    carry an explicit expectation and report the ranking; see also the §5.4 scope rule.
  - **Project-context append is optional but if you do it, supersede in place.** Sibling cards
    disagreed (t_4bc70740 appended a `projects/<pid>/context.md` section, t_54b6d101 did not).
    When your card's requirement text says "update project membership context", append a section
    and explicitly mark the earlier "Users N, M remain owned by their own cards" sentence as
    superseded *for your member* — append-only, do not edit the sibling's historical sentence.
  - **Correct the w-bridge `action_text` via `edit_knowledge_activity_log` rather than leaving a
    typo.** The first `add_knowledge_activity_log` call accepted a wording slip; the fix needs
    **both** `activity_id` and `project_id` — omitting `project_id` fails with
    `404 … /api/projects/None/knowledge_activities/<id>`. Read the entry back afterwards.

  ### 3g. Refinements verified on card t_a0226985 (User 7, project 5)
  - **URI-prefix trap: the company namespace constant already contains `company`.** With
    `NS = "viking://user/hermes/memories/company"`, the numeric-alias note is
    `f"{NS}/1/projects/<pid>/context.md"` — **not** `f"{NS}/company/1/..."` (that 404s as
    `company/company/1/...`). Worse, `entities/user/user_N.md` is *outside* `NS` entirely
    (`viking://user/hermes/memories/entities/...`). Three of seven writes silently skipped
    because an early `raise SystemExit` on a missing alias note aborted the run mid-way; build
    every URI from a single literal and `stat` it in recon.
  - **The identity node may pre-declare your card as the record owner — then flip the bullet.**
    `entities/user/user_7.md` (filed by the account-event card t_d813b187, §3e shape) already
    said the membership "**record** `projects/5/members/7.md` is owned by card t_a0226985 and is
    deliberately not written here". That is a *handoff*, so this card does a targeted
    read-modify-write of exactly those two lines to point at the filed record, then appends the
    membership block; assert the preserved entry points (`- **User ID:** N`, `**Kind / status:**`)
    and report `dropped_lines == [the two old bullet lines]` as the pass condition. Grep the
    read-back for the old "deliberately not written here" wording before closing.
  - **The no-clobber guard for RMW files is `must_contain` markers, not full-text equality.**
    Read-modify-write targets (registry, `_index.md`, project context, alias note, identity node)
    have no staged baseline, so verify them with marker greps + a NEW-slash-OLD marker check
    (OLD wording gone, NEW wording present) instead of the exact staged-vs-disk comparison used
    for freshly created records.
  - **Do not reconstruct the registry row from a template — grep it.** Filed rows are not in the
    short documented form; they carry the member label, the real timestamp and the flip state, e.g.
    (project 6 members registry, read 2026-09-28):
    ``| User 7 (`Workspace`, bot) | `members/7.md` | User 1 (Pavel Teichman) | project_member_added
    2026-09-25T06:24:54Z — card **t_58635966** | **recorded** |`` — note the member label in
    parentheses and the em dash. A constructed
    ``| User N | `members/N.md` (pending) | User 1 | project_member_added — card t_XXXX | owned by
    that card (blocked) |`` greps **0 matches**, and a blind `edit` with it fails (each failure also
    costs a ~60 s MCP circuit-breaker pause). Instead `grep(uri=<registry>, pattern="members/<N>.md")`
    and copy the returned `L<n>` line verbatim as `old_string`; a hyphen-only or template-only
    variant misses and the run aborts on the missing row.
  - **Re-probe wording for the numeric alias is scoped, exactly as §3d's correction says.** The
    unscoped probe `"/company/1/projects/5 numeric company id pointer canonical ai-lab"` MISSED
    (5 `.abstract.md` hits), while the record's own title string
    `"/company/1/projects/5 -> canonical /company/ai-lab/projects/5 numeric-company-id pointer"`
    scoped to `user/hermes/memories/company/1` returned **rank 1** (0.7475). Keep the missed
    wording in the probe file as a comment with its resolution.
  - **Record-specific probes rank 2 for records filed into a directory that already has an
    index.** `members/7.md` ranked 2/7 under the `members` scope and 5/8 company-wide;
    the activity entry ranked 2/8 under the `activities` scope. Generic roundups return
    `_index.md` / sibling records first — report as "retrieved via its canonical index entry
    point", not as a miss.

  ### 3h. Refinements verified on card t_6a05378b (project 6 "Selfin", project_created)
  - **The card's "no sibling cards exist yet" premise can be stale at execution time — re-check the
    board before honouring it.** This card instructed "no member-card siblings for project 6 yet, so
    create ONE founding-membership record (User 1)". Two siblings existed for the same event second
    (`project_member_added` t_268b8b66, `project_first_joined` t_00ec048a), one already `running`, and
    it had filed `members/context.md` + `members/1.md` + its activity entry *while this card ran*.
    Correct action: file none of it, record the handoff in the project context note and in a card
    comment. Same for the room layer (`room_created` t_181cdcad owned rooms 38/39/40; a duplicate
    t_1d34da6a was `archived` by the dispatcher 15 s after creation). The `project_created` card's own
    share is the project record + the *registry index* — exactly what t_3836a7cd did for project 5
    (`projects/5/rooms/context.md` is `established_by` the project card).
  - **The payload omitting rooms does not mean the project has none.** Card text said "no rooms exist
    yet for this project; project_created carries no room ids", but `GET /api/projects/6/rooms`
    returned 38 `selfin` (Rooms::Project) + 39/40 (Rooms::Open, parent 38), all in the project's
    creation second. Register what the API says and mark per-room nodes *pending — owned by <card>*.
  - **Directory nodes created implicitly by `content/write` never get an abstract and cannot be
    given one later.** `fs/mkdir {"uri","description"}` on an existing dir returns **409 CONFLICT**;
    the "`[Directory abstract is not ready]`" placeholder is permanent for such dirs (project-5
    `projects/5`, `rooms/37` show it days later). Dirs made with `fs/mkdir` *first* keep the
    description as their abstract (rooms/35, `members/`, `1/rooms/37`). So if scope-node abstracts
    matter for ranking, `mkdir` the directory with its description **before** writing records into it.
    Doing it after is not worth a delete-and-recreate; the records themselves are indexed fine.
  - **Unscoped / company-scoped recall probes can be drowned out by unrelated `.abstract.md` nodes.**
    With project 5's room tree present, queries like "project 6 Selfin project context root" returned
    5+ project-5 directory summaries scoring ~0.85 and **none** of the fresh project-6 records, even
    with the record's own title wording. Re-probing **scope-constrained**
    (`target_uri: user/hermes/memories/company/ai-lab/projects/6`, query = the project's own naming)
    returned **all** of them: `context.md` rank 3, `items/_index.md` 2, activity entry 4,
    `external-assets` 5, `directory-items` 6, `knowledge/context.md` 10, `status` 11, `adrs` 12,
    `attention` 14, `obsidian-notes` 15, `activities/_index.md` 16, `rooms/context.md` 17 — plus the
    numeric pointer at rank 1-2 scoped to `company/1`. Report the in-scope ranking; do not call it a
    miss and do not chase the generic pool. Newly created sibling dir abstracts (`members/.abstract.md`)
    legitimately outrank your records for generic project-6 phrasings — that is the index-shape
    artifact §5.4 describes.
  - **`fs/stat` size is not `content/read` length.** Every healthy record stat'ed `size: 4` here while
    `content/read` returned thousands of chars — assert existence on `result["name"]` + `not isDir`
    (as §5.2 says) and never on size.

  ### 3i. Refinements verified on card t_bc377038 (project 7 "Ledgerly", project_created)
  - **The `project_created` context note is a shared RMW target — a concurrently-running membership
    card edits it before you finish.** Measured: card t_d712395a (`project_member_added`, same
    second, running in parallel) read-modify-wrote `projects/<pid>/context.md` to flip "membership
    not yet filed" → "filed by card t_d712395a" *while this card was still running*, and **dropped
    the opening `---` of its YAML frontmatter** (first line on disk became `capture_type: ...`).
    So: (a) never assert an exact staged-vs-disk equality on `projects/<pid>/context.md` — verify it
    with marker greps + a frontmatter-key check instead (the freshly-created subdomain records are
    still fine with the strict comparison); (b) re-read immediately before any write to that note;
    (c) assert `body.startswith("---\n")` as its own check and repair by prepending `---\n` with
    `mode=replace`, leaving the sibling's added keys and its `last_updated_by` untouched (a
    delimiter repair is not an editorial change), then record it as a `## Correction log` in
    `knowledge/activities/project_structure_registered.md`. Expect to file the project record
    *before* the membership layer exists — project 6's project card saw the same ordering.
  - **Resolve the bundle group id and both ledger row ranges in one cheap read — no rails runner per
    row.** `sudo -n cp /var/lib/docker/volumes/wbridge_data/_data/w_bridge.db /tmp/bridge_ro.db`
    then `select id,event_type,event_id,group_id,dedupe_key from space_events order by id desc limit
    14` returns the whole creation bundle, and **`dedupe_key` is
    `event:<event_type>:<rails_output_events.id>:<hash>`** — i.e. it names the Rails row for every
    event (project 7: bridge 82–87 → Rails 99 `project_created`, 100 `project_member_added`,
    101 `project_first_joined`, 102/103/104 `room_created` event_id 41/42/43). Cite both ledgers;
    one `bin/rails runner` with `OutputEvent.where(group_id: ...)` then only confirms. A six-row
    transaction also *proves the absence* of `room_member_added` — that is the evidence to write
    instead of "no membership records are pending".
  - **A URI-prefix bug fails SILENTLY into a real directory: assert the ls of the intended parent,
    not just the per-record read-back.** With `NS = ".../memories/company"`, building the numeric
    note as `f"{NS}/company/1/projects/7/context.md"` created
    `.../memories/company/company/1/projects/7` and wrote the note there — and the read-back
    verification *passed*, because the record was written, just at the wrong path (§3g's trap, whose
    symptom here is a green verification run with no record at the canonical path). Catch it by
    asserting the intended path appears in `fs/ls` of the intended parent
    (`fs/ls .../company/1/projects` must list `7`); repair with
    `DELETE /api/v1/fs?uri=<stray>&recursive=true&wait=true` (`estimated_deleted_count: 2`) and
    assert `fs/stat` → `NOT_FOUND` afterwards.
  - **Sequencing that worked.** This card ran first and created `projects/<pid>`, `knowledge/*`
    (6 subdomains + `_index.md`), `status/`, `attention/`, `rooms/context.md` (rows
    *pending — owned by <room card>*, `mkdir`ed with its provenance description **before** the
    records) and the numeric pointer; the membership card then filed `members/` + its activity
    entry; the room card keeps the room tree. Recall shape matched project 6: directory
    `.abstract.md` nodes outrank records for generic project wording (project context rank 6–7,
    knowledge index rank 8 in-scope) while the activity entry and status scope rank **1** and the
    rooms registry / attention index rank **2** — report the index-vs-record shape, don't chase it.

Membership content belongs in `members/` (it is a project entity, not a knowledge item); log
the filing action once in `knowledge/activities/` and once via w-bridge
`add_knowledge_activity_log` with `target_path` = the member record path.

**Company-scope rooms (`project_id = null`) use the same node minus the project segment**
(verified on card t_3af1f7e2, room 34 `members/6.md`):
`/company/ai-lab/rooms/<room_id>/members/context.md` + `members/<user_id>.md`, same ownership
rule (the room card creates the `members/` resource, the membership-event card writes exactly its
own member and flips that registry row). Do **not** call `add_knowledge_activity_log` there — no
project means HTTP 404 on `/api/projects/None/knowledge_activities`; the filing goes to
`rooms/<room_id>/activities/<record>.md`. Convention text:
`company/ai-lab/infra/ov-memory-structure-conventions.md` §2e.

Memory URI prefix: `viking://user/hermes/memories/...`. Subdomain -> w-bridge tool mapping
(`items`->`project_knowledge_items`, `adrs`->`project_decision_records`,
`external-assets`->`external_knowledge_assets`,
`directory-items`->`tree_based_project_directory_data`,
`obsidian-notes`->`project_obsidian_note`, `activities`->`knowledge_activity_log`) is written
into `knowledge/context.md`.

Per-room nodes carry the room identity (id, name, type, parent, created_at) and the required
subtree shape. **Do not pre-create empty `messages/`, `approval_requests/`, `decisions/`
directories** — they appear when they receive their first record. This matches the existing
verified room-4 layout and keeps the tree free of placeholder noise.

## 4. Write

Credentials: `OPENVIKING_API_KEY` is an **account user** key (account `default`, user
`hermes`) in each profile `.env`. A ROOT key is rejected on tenant-scoped data APIs with
`PERMISSION_DENIED`; `/mcp` does accept root. Resolve as:

```bash
export HERMES_PROFILE_ENV=/home/ubuntu/.hermes/profiles/knowledge/.env
```

Write each record with `POST /api/v1/content/write`
(`{"uri","content","mode":"create","wait":true,"timeout":120}`); use `mode=replace` to update.
A successful write returns `written_bytes` and `vector_status=complete`.

Ready-made scripts: `scripts/write_records.py` (staged files -> URIs, idempotent: skips URIs
whose read-back already matches) and `scripts/verify_records.py`. Both resolve the key from
the profile `.env`. Copy and edit the `RECORDS`/`PROBES` tables at the top.

The older `note-taking/ov-conversational-capture` skill (normal-message profile) has the same
REST contract and its own `ov_capture.py`; run it with `HERMES_PROFILE_ENV` pointed at your
profile's `.env` (its key resolution defaults to normal-message).

## 5. Verify (three independent ways — never report an unverified write)

1. **Content integrity**: stored file == staged body. Tolerate exactly two server
   normalisations: (a) the trailing newline is stripped, (b) the server appends a
   `MEMORY_FIELDS` HTML-comment metadata block (JSON `{"version": 1}`) at the end — this is
   the constant `+42` byte delta seen on disk, benign, and also present on older sibling
   records.
   **Never quote that literal comment marker inside document body text.** The server strips
   the marker wherever it occurs, not just at the end, so a sentence containing it comes back
   silently mutilated (observed: an inline mention was deleted, leaving empty backticks).
   Describe the marker in prose instead. Compare the body with the trailing block stripped,
   and also round-trip via `GET /api/v1/content/read`.
   Note byte-vs-char counts: em dashes and other multi-byte characters make the on-disk byte
   size larger than the string length `content/read` returns — compare decoded strings, never
   a byte count against a char count.
2. **Existence**: `GET /api/v1/fs/stat?uri=...` on every URI you wrote. In this deployment
   the response has **no `exists` key** — `result` is `{name, size, mode, modTime, isDir,
   isLocked}` and a non-null `result` **is** the existence proof. Asserting on
   `result["exists"]` reports every healthy record as a failure; assert on
   `result and result["name"] and not result["isDir"]` instead. `fs/ls` on a directory is a
   useful cross-check for a subdomain index listing its records.
3. **Tree**: `viking_browse(action="tree", ...)` shows every path you claimed exists.
4. **Semantic recall**: POST `/api/v1/search/search` with several phrasings and require the
   target URI to come back. Hits nest under **`result.memories`**, not `result.items` —
   parsing `items` silently returns `[]` and makes an indexed record look missing. `mode`
   accepts only `list|context` (anything else is `400 INVALID_ARGUMENT`); omit it. A
   "missing" target is usually just phrasing: re-probe with a query close to the record's own
   wording before declaring failure — canonical entry points should rank top-1/top-2.

   **`target_uri` must be a valid viking SCOPE path, not the plain memory path** (verified on
   card t_54b6d101): use `user/hermes/memories/company/ai-lab/...` (or a bare scope:
   `user`, `agent`, `resources`, `session`). Passing the path shape `company/ai-lab` returns
   `400 INVALID_URI: Invalid scope 'company'. Must be one of: agent, resources, session, user`,
   and a probe that only reads `result.memories` sees `[]` — i.e. a whole-card pass of false
   "record not retrievable" failures on freshly verified records. Check for `_http_error` in
   the probe helper and fail loudly on it instead of treating it as an empty result. The same
   card also confirmed the expected rankings: record rank 1 under the company scope with its own
   wording, rank 2-3 in a narrower subdir scope, and out-of-tree nodes (`entities/user/user_N.md`)
   reachable only **unscoped** (rank 3 for the member's own wording).

   **Index-vs-record ranking is by design, not a miss.** Once you append a pointer to a
   subdomain `_index.md` (which names the record file), the *index* outranks the record for
   generic subdomain queries ("activity log entry for project 5") while the record still ranks
   top-3 for record-specific phrasings. Report this honestly as "retrieved via its canonical
   index entry point" — do not chase it with more probes and do not call it an indexing gap.
   Filing each record immediately after writing it is what creates this expected shape.

   **Never probe a record from outside its scope and call the empty result a failure.** A
   `target_uri`-scoped probe can only return hits under that prefix, so a record you filed
   *elsewhere* (observed: `entities/user/user_7.md`, a bot-roster identity entry filed with a
   company-scope account event) is structurally unreachable from `target_uri=company/ai-lab`.
   Re-probe those unscoped and expect them to rank behind any pre-existing literal-match memory.
   Also expect target-specific queries ("<record name> <field>=<value>") to surface the record
   at rank 1 while generic subdomain/wording roundups return `.abstract.md` index entries first:
   give each probe an explicit expectation and report the ranking, don't treat the index hits as
   the miss.

Give write calls a generous timeout (600s terminal timeout); embedding is synchronous.

## 6. Close the card

**UPDATE (2026-09-25, card t_6a05378b): the `kanban` toolset is ENABLED for the `knowledge`
profile again — use the in-session tools.** `kanban_show`, `kanban_comment` and
`kanban_complete` all worked directly (checked via `kanban_show()` first, closed with
`kanban_complete(summary=..., metadata=..., artifacts=[...])`, `run 107 -> outcome completed`,
`status=done`, lease released). Prefer the tools; the CLI route and the "nudge cannot be
satisfied" notes below apply only if `kanban_*` is absent from your tool surface at session
start (config may have been re-disabled). Everything below is the historical/fallback path.

The `kanban` toolset was config-disabled for the `knowledge` (and `normal-message`)
profiles: `~/.hermes/profiles/<profile>/config.yaml` lists it in `agent.disabled_toolsets`
**and** `platform_toolsets.cli` is an explicit allowlist that omits it. So `kanban_complete`
does not exist in-session and `tool_search` will not find it. Consequences:

- A harness nudge demanding `kanban_complete(...)` **cannot** be satisfied in-session (the
  tool surface is frozen at session start). Report it; never fake the call. **The nudge can
  keep firing after a successful CLI close** (observed on card t_a0226985: the nudge claimed
  "still running" while the board row was already terminal). Verify with the board's own
  database before believing it, and quote the evidence back:
  ```bash
  python3 - <<'PY'
  import sqlite3
  c = sqlite3.connect("/home/ubuntu/.hermes/kanban/boards/company/kanban.db")
  c.row_factory = sqlite3.Row
  t = dict(next(iter(c.execute("select * from tasks where id='t_XXXX'"))))
  print({k: t[k] for k in ("status","current_run_id","claim_lock","completed_at")})
  for r in c.execute("select id,status,outcome,ended_at,error from task_runs where task_id='t_XXXX'"):
      print(dict(r))
  PY
  ```
  `status=done` + `current_run_id=None` + the last `task_runs` row `outcome=completed` (its
  `ended_at` equals `completed_at`, because the CLI close also closes the run) means there is
  nothing left to close. Two cheaper checks settle it in one shot before hand-reading the DB
  (verified on card t_12ec6e42, 2026-09-22):
  ```bash
  hermes kanban --board company list --status running     # -> "(no matching tasks)"
  hermes kanban --board company complete <card> --result "noop"
  # -> cannot complete <card> (unknown id or terminal state)
  ```
  plus a group-by on the board DB proving no `running` row exists at all
  (`select status, count(*) from tasks group by status` -> only `done` / `archived`), and a check
  that the run's lease fields are released (`claim_lock`, `claim_expires`, `worker_pid` all `None`).
  An open lease — not the free-text nudge — is the only genuine "still running" signal; the nudge is
  emitted whenever a turn ends without a kanban tool call, including after a successful CLI close.
  Do **not** work around it by editing the profile config's
  `disabled_toolsets` unasked — that changes the profile's tool surface for every future run.
- Close through the official CLI, which writes the same `completed` event, `result`, run
  status, and summary/metadata:

```bash
hermes kanban --board company comment <card> "<text>" --author knowledge
hermes kanban --board company attach  <card> <file> --name <name> --author knowledge
hermes kanban --board company complete <card> --result "<one line>" \
  --summary '<json>' --metadata '<json>'
```

- Pass multi-line payloads as a **single argv element from Python** (`subprocess.run([...])`)
  — giant inline shell payloads trip the hardline command-parser block, and shell command
  substitution loses newlines. See `scripts/close_card.py`.
- The scratch workspace `boards/*/workspaces/<card>/` is **deleted on completion**: stage in
  `/tmp`, but put durable artifacts in OV or as board attachments (one manifest file listing
  URI + sha256 per record is a good durable handle).

## 7. Pitfalls checklist

- Do not invent facts the event omits (room ids, phases, membership) — resolve or cite.
- **Helper bug that fakes a missing record:** the OV envelope always has an `error` key (`null` on
  success), so `if "error" in r: return None` makes every healthy `content/read` look absent.
  Use `r.get("error")`. `content/read` returns its body as a plain string under `result`;
  `content/write` reports `result.vector_status` (`written_bytes` is absent).
- **Wrong-path nodes are repairable:** `DELETE /api/v1/fs?uri=…&recursive=true&wait=true`
  (`result.estimated_deleted_count`). Use it for the `{NS}/company/1/...` URI-prefix trap (§3g)
  or a stray probe file, then `fs/stat` the paths and assert `NOT_FOUND`, and record the repair as
  a correction log in the affected note. Endpoint inventory: `GET /openapi.json`.
- For a parent-room thread link (`rooms/<parent>/threads/<child>`), match `threads/<child_id>` in
  recall probes — a `rooms/<child_id>` matcher reports a false miss (card t_0d85473a).
- `content/read` returns **HTTP 404 `NOT_FOUND`** for a missing file and **HTTP 400** for a
  directory URI (verified on card t_6f068477). A read-back helper must treat 404 as "absent" or
  the idempotent first write aborts; never `content/read` a directory. `fs/mkdir` takes
  `{"uri", "description"}` and the description becomes that directory's summary/abstract — that
  is how pre-created room children carry their provenance line.
- After `hermes kanban complete`, the scratch workspace is deleted and the shell cwd dies:
  `write_file` then fails for **every** path with `[Errno 2] No such file or directory` until you
  `cd` to a surviving directory via terminal. Stage scripts under `/tmp/` from the start.
- Additive RMW inserts: anchor on the **whole** bullet/line, not its first line — an indented
  continuation line otherwise gets re-parented under your new bullet, and a set-based "dropped
  lines" check cannot detect the re-ordering (verified on card t_3898e963; assert index order too).
- Do not create a `/company/<numeric_id>/` tree beside the slug tree — but **do** check for
  one: sibling cards whose body quotes the raw numeric paths may create it concurrently
  (observed: a room card built `/company/1/projects/5/rooms/32/{messages,approval_requests,decisions}`
  and `/company/1/.../rooms/29/threads/32` while the canonical tree was `ai-lab`). When you
  find a divergence, flag it on both cards with evidence instead of silently duplicating or
  deleting another worker's records; convergence is an operator/convention decision.
- Do not write the literal server marker (`MEMORY_FIELDS` comment) inside a record body.
- Do not pre-create empty room subdirectories.
- Do not skip the recall probe: `vector_status=complete` alone does not prove retrieval.
- Do not claim a write for a record you did not read back.
- Obsidian: if no Obsidian MCP and no vault exist (`OBSIDIAN_VAULT_PATH` unset, no `.obsidian`
  dir), store in OV (the documented fallback) and say so on the card; keep
  `knowledge/obsidian-notes/` as the registration point for later.
