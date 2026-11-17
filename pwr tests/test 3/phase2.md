# Test 3 Phase 2 — Direct MCP Task Creation (workspace profile calls create_ai_task via action-mcp)

Driver: action-mcp endpoint (MCP_AUTH_TOKEN) to invoke create_ai_task directly from workspace context.
Goal: Prove that inter-profile task creation CAN happen without a chat trigger — i.e., an agent can programmatically delegate to another profile.

### Setup

First, establish an initialized MCP session with workspace profile:
```bash
curl -X POST http://localhost:3000/workspace-mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer <MCP_AUTH_TOKEN>" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test3-harness","version":"1.0"}}}'
```
Capture Mcp-Session-Id from the SSE headers line.

### Steps

| # | Action | Endpoint | Payload |
|---|--------|----------|---------|
| 1 | Initialize workspace MCP session | POST /workspace-mcp | standard initialize JSON-RPC 2.0 |
| 2 | List available tools | POST /action-mcp (with sessionId header) | method=tools/list |
| 3 | Call create_ai_task | POST /action-mcp (with sessionId header) | name=create_ai_task, args={project_id:8, assignee_profile:"coder", description:"Test3 direct MCP delegation", level:1, parent_task_id:null, importance:1, room_id:6} |
| 4 | Verify task in DB | sqlite3 SELECT | task exists with correct assignee and project |
| 5 | Poll for execution result | sqlite3 JOIN messages + tool_cal_logs | coder profile posts verification back to room 6 |

### Key assertion

Unlike Phase 1 where delegation happened implicitly via message analyzer noticing mentions, this proves explicit programmatic delegation works. If the same Net::ReadTimeout failure occurs, the gap is in the delivery mechanism (Rails→profile communication), not in task creation logic.
