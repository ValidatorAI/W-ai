Verification complete. I found the actual root cause of the biggest waste, and I need to correct two things I told you earlier.

CORRECTIONS FIRST (both were wrong)

1. I said the 155 w-bridge tools cost ~32k tokens of schema on every round. Wrong.
   The log shows tool_search deferring them:
     tool_search activated (tier 1): 15 core/visible tools kept,
     155 deferred (~33328 tokens), listing full (budget ~4000 tokens)
   The 33,328 tokens are NOT sent. Only a ~4,000-token listing is. Trimming
   w-bridge saves ~2-3k tokens/round, not 32k. Much smaller than I claimed.

2. I said the OV MCP exposes write/edit and the profile just ignored it. Half wrong.
   The memory MCP does register 19 tools including mcp__memory__write and
   mcp__memory__edit (log, 2026-09-18 07:45 and 09-22 10:15). But the agent's
   tool surface only ever exposed the 155 w-bridge tools as deferred — its own
   tool_search reported "0/155 matches". So mcp__memory__write was not reachable
   in practice, and REST was the only working write path. The skill's REST rule
   was a workaround, not a whim.

AND THE ACTUAL ROOT CAUSE OF THE NUDGE LOOP (verified in source)

  agent/kanban_stop.py:
    guard ON when HERMES_KANBAN_TASK is set (every dispatcher worker)
    _DEFAULT_MAX_ATTEMPTS = 2
    returns None if session already called kanban_complete / kanban_block
    the nudge text says: "Call kanban_complete(summary=..., artifacts=[...])"
  tools/kanban_tools.py:_check_kanban_mode() -> requires HERMES_KANBAN_TASK
    AND _is_dispatcher_owned_worker()  ...or the kanban toolset in config
  profiles/knowledge/config.yaml:
    agent.disabled_toolsets contains: kanban
    platform_toolsets.cli does NOT contain: kanban

  So every knowledge worker is spawned with the guard armed, told to call
  kanban_complete, and the tool physically cannot exist in its session.
  54 nudge events over 27 tasks = exactly 2 each = max_attempts, every time.

Here is the checklist.

======================================================================
A. STOP THE GUARD DEAD-END  (biggest win; verified root cause)
======================================================================
[ ] A1. Enable the kanban toolset for the knowledge profile.
        HERMES_HOME=~/.hermes/profiles/knowledge hermes tools enable kanban
        This writes kanban into platform_toolsets.cli AND removes it from
        agent.disabled_toolsets (tools_config.py:2588-2614 does that reconcile).
        Effect: the worker gets kanban_complete / kanban_block / kanban_show /
        kanban_comment / kanban_heartbeat / kanban_link as real tools.
        The guard becomes satisfiable; the 2 dead rounds per task disappear.
        Targets the 13.1% of model time the last session burned on this.

[ ] A2. Verify it landed.
        HERMES_HOME=~/.hermes/profiles/knowledge hermes tools list | grep kanban
        HERMES_HOME=~/.hermes/profiles/knowledge hermes config get agent.disabled_toolsets
        Expect: "kanban" absent from the disabled list.

[ ] A3. Re-run one card and confirm the guard is gone.
        grep -c "stop-loop nudge" ~/.hermes/profiles/knowledge/logs/agent.log
        Expect: no new hits. And the session should show a kanban_complete tool call.

[ ] A4. Fallback only if A1 is rejected: disable the guard for workers by
        exporting HERMES_KANBAN_STOP_NUDGE=0 in the dispatcher's environment.
        There is no config.yaml key for it — the code reads os.environ directly,
        so this breaks the secrets-in-.env convention. Prefer A1.

======================================================================
B. LET WORKERS TALK TO THE BOARD NATIVELY (kills most CLI traffic)
======================================================================
[ ] B1. Same change as A1 enables this: replace the shell round-trips with tools.
        188 hermes kanban show -> kanban_show      (no terminal round, no shell quoting)
         32 hermes kanban complete -> kanban_complete
         21 hermes kanban comment -> kanban_comment
        Each CLI call currently costs one full API round at ~110-146k input tokens.

[ ] B2. Add to the lifecycle skill: read the card ONCE with kanban_show at
        session start and read comments ONCE before close. Not 6.3 times per card.
        Evidence: t_25588382 read 30x, t_3fa833ef 25x, t_94d26890 25x; one command
        shape (show T 2>&1 | head -100) repeats identically 20 times.

[ ] B3. Ban direct SQLite reads of the board.
        Evidence: 59 commands re-derive by hand what show/runs already prints
        (tasks.status, current_run_id, task_runs lease fields, workspace_path).
        Add to the skill: "the CLI is the interface; do not open kanban.db."

======================================================================
C. FIX THE OPENVIKING WRITE ROUTE  (removes ~152 terminal commands / 16%)
======================================================================
[ ] C1. First, establish what is actually callable in a knowledge session.
        Start one card, then in-session check whether mcp__memory__write
        appears in tool_search results. Evidence says the agent's surface only
        exposed 155 w-bridge tools, so expect "no".
        Do not rewrite the skill before you know which route works.

[ ] C2. If mcp__memory__write/edit ARE reachable, patch ground rule #2 of
        ~/.hermes/profiles/knowledge/skills/note-taking/ov-wspace-lifecycle-registration/SKILL.md
        (currently line ~27) to use them instead of:
          "POST /api/v1/content/write, POST /api/v1/fs/mkdir using
           OPENVIKING_API_KEY from the profile .env in an X-API-Key header"
        Payoff: kills the collateral chain together — 71 source .env,
        68 port-1933 calls, 52 urllib imports, 31 curl = 152 commands (16.1%),
        and turns a 3-step HTTP dance into one tool call.

[ ] C3. Delete the on-disk verification route outright, in the same skill.
        Evidence: 20 commands find/grep/sed/diff inside
        /home/ubuntu/.openviking/data/viking/default/user/hermes/...
        That is the server's private storage; verifying an API write by reading
        the server's disk is a tautology. Read back with viking_read instead.

[ ] C4. If C2 is not possible, at least fold the REST calls into ONE helper
        script per session instead of 68 ad-hoc curl/urllib commands, and stop
        re-sourcing .env on every call (it did that 71 times).

======================================================================
D. FIX THE INFRASTRUCTURE THE WORKAROUND WAS COMPENSATING FOR
======================================================================
[ ] D1. The OV MCP endpoint is configured as http://0.0.0.0:1933/mcp.
        Prefer 127.0.0.1 (0.0.0.0 as a client target is undefined behaviour and
        is the likely source of the ConnError/Timeout churn).
        HERMES_HOME=~/.hermes/profiles/knowledge hermes config set mcp_servers... 
        (nested key — use hermes config edit for this one, then re-read it)

[ ] D2. Raise the MCP timeouts. Documented keys per server:
        timeout (default 120), connect_timeout (default 60).
        Evidence: 37 keepalive failures + 10 failed initial connections +
        13 ConnectErrors, all on 2026-09-18.

[ ] D3. Clear the 12 stale 0-byte discovery locks:
        find ~/.hermes -name .mcp-discovery.lock -size 0 -delete
        Evidence: 6x "MCP discovery lock still held after 240 retries --
        running discovery unguarded". Every profile has one, never cleaned.

[ ] D4. Confirm both servers are up before blaming the agent. Right now:
        OV 1933 -> /health 200 (healthy), w-bridge 8000 -> /mcp 405 (up).
        So the current state is fine; D1-D3 are about not regressing.

======================================================================
E. TRIM THE DEFERRED CATALOG  (modest — do it last)
======================================================================
[ ] E1. w-bridge exposes 155 tools for 39 calls total in 34 sessions.
        Restrict it to the knowledge/lifecycle families it actually uses:
          add/ knowledge_activity_log, edit_knowledge_activity_log
          project_knowledge_items, add_project_knowledge_item
          decisions_waiting, blockers, mentions
        Two ways:
          hermes tools disable w-bridge:hello w-bridge:add_material_changes ...
          or the interactive wizard (hermes tools) which writes an include list.
        Config shape it writes: mcp_servers.<server>.tools.exclude / .include
        Payoff is ~2-3k tokens/round, NOT 32k. Low priority.

[ ] E2. Note the real MCP cost is the 3-round tax: tool_search ->
        tool_describe -> tool_call. Evidence: 16 writes of
        add_knowledge_activity_log needed 17 tool_describe calls; 104
        indirection calls total. Trimming the catalog does not fix this —
        only making the tools non-deferred would, which there is no config for.

======================================================================
F. STOP DUPLICATE DISPATCH
======================================================================
[ ] F1. Six cards ran twice -> 34 sessions for 30 knowledge cards:
        t_3fa833ef, t_b926a02c, t_4f6d6d99, t_52eb82e6, t_cf989b41, t_3898e963.
        Audit the delegator's idempotency keys and check the board for an
        existing card before create. That is 6 wasted sessions (~40 min).

[ ] F2. Room-37-style bundles dispatch 4 sibling cards in the same second.
        They coordinate only through comments. Consider one card per event
        FAMILY with sequential steps, so the 44 multi-card coordination
        commands and the "ALREADY EXISTS — do not re-create" handoff dance
        stop being necessary.

======================================================================
G. SKILL BLOAT
======================================================================
[ ] G1. ov-wspace-lifecycle-registration/SKILL.md is 60,131 chars and was read
        8+ times per task at 34.7-56.0 KB per view. skill_view returns averaged
        15,798 chars and produced 1.28M chars = 23.6% of ALL injected context.
        Move the pitfalls appendix (lines ~400-600) into references/ and load it
        only when a pitfall fires. Update the SKILL.md to point at it.

[ ] G2. Add to the skill: "do not re-view a skill you already viewed this
        session." The top 8 skill_view returns were all the same file.

======================================================================
H. AGENT BUDGET
======================================================================
[ ] H1. agent.max_turns is 90. One session hit exactly 90/90
        (20260918_102128_708223) — it was cut off, not finished. Re-check after
        A-G; if sessions still land near 90, raise it, otherwise leave it.
        Do not raise it first — that just pays for the waste at a higher ceiling.

[ ] H2. Do NOT enable compression. deepseek-v4-flash has a 1,000,000-token
        context (models_dev_cache), so the 146k peak input is nowhere near a
        limit. Compression would break prompt caching and cost more.

======================================================================
I. BASELINE + VERIFICATION
======================================================================
Record these numbers now, then re-measure after ~5 cards:

    API rounds / task            43.9
    tool calls / task            56.4
    wall time / task             402 s
    model vs tool latency        57.7% / 42.3%
    base_in -> peak_in           22,795 -> 146,517  (+2,249 tok/round)
    terminal calls               942  (89.9% read/inspect)
    kanban CLI calls             394  (188 show, 32 complete, 59 raw sqlite)
    OV-route-bypass commands     152  (16.1%)
    nudge events                 54 over 27 tasks  <- expect 0
    skill_view calls             81, avg 15.8 KB   <- expect steep drop

Re-measure with:
  cd ~/.hermes/profiles/knowledge && python3 -c "..."  (the parsers I used above)
Or simply:
  grep -c "stop-loop nudge" logs/agent.log
  grep -oE "API call #[0-9]+" logs/agent.log | wc -l

DO IN THIS ORDER: A (one command, biggest win) -> C -> B3/F1 -> D -> E -> G.
A alone removes the guaranteed 2 dead rounds per task and hands the worker real
board tools; C removes ~16% of terminal traffic; everything else is tuning.

Want me to execute A1 (enable kanban for knowledge) and the C3/G2 skill edits
now? A1 is one reversible command; the skill edits change behaviour for every
future knowledge run, so I'd rather you approve them explicitly.
