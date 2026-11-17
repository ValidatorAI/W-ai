# Test 3 — Inter-Profile Task Delegation Battery

Objective: End-to-end verification of multi-agent task delegation between Hermes profiles, measuring success/failure at each hop in the pipeline.

Background: In Test 1 & Test 2 phases, task creation via `create_ai_task` was observed only incidentally (when message_analyzer auto-routed tasks). This test drives it explicitly as a test input rather than a side-effect.

Structure: 5 phases, each targets one stage of the delegation chain.

---

Phase 1 — Chat-Triggered Delegation: workspace → business_analyst
Phase 2 — Direct MCP Delegation: workspace → coder  
Phase 3 — Execution Verification: Does coder respond?
Phase 4 — Cross-Project Delegation + Approval Gate
Phase 5 — Concurrent Delegation Race

Key variables tracked:
- Task creation: assigneee_profile, dispatched flag, dispatch_attempts
- Delivery success: dispatch_error field (currently shows Net::ReadTimeout)
- Response quality: tool_cal_logs presence, bot message content in target room
- Approval compliance: cross-project writes gated correctly

Expected primary finding: Delegations fire consistently through step 1-4 (event emission → task creation → dispatch initiation), but **step 5 (actual delivery to recipient profile)** fails intermittently with TCP timeouts. This suggests the gap is in Rails→Hermes profile WebSocket/session bridge, not in task model logic.
