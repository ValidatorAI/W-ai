# Bonfire W-space Chat Testing Scenarios

Date: 2026-09-15
Scope: Manual and integration-style scenario testing for company setup, project setup, user assignment, and chat/profile routing behavior.

## Purpose

This document provides 3 end-to-end scenarios for testing W project interactions in W-space (Bonfire), starting with the simplest path and then adding routing complexity.

Every step includes expected state in:

1. Bonfire application state (Account, Project, Room, Membership, Message)
2. W-ai profile processing state and handoff order
3. OV expected capture state
4. Obsidian expected state
5. Event processing order expectations

## Shared Preconditions

1. Bonfire is running and users can sign in.
2. W-bridge is reachable and configured with a valid output events token.
3. W-ai main profiles are available: delegator, action, knowledge, normal message, company, company_project, not_known_task, cron_profile.
4. At least one admin user exists.
5. At least two regular users exist for assignment tests.

## Scenario 1 (Simplest): Company Setup -> Project Create -> Assign One User -> Normal Chat

### Objective

Validate the smallest complete path from workspace configuration to one chat message routed as normal conversational capture.

### Step 1: Open Company Settings and define company-level configuration

User interaction:
1. Admin opens Company Settings.
2. Admin updates company/workspace info fields as needed.
3. Admin optionally chooses allowed bot users.
4. Admin saves settings.

Expected state afterward:
1. Bonfire state:
   - Current workspace context resolves through Account.
   - Account settings are persisted, including allowed bot IDs if selected.
   - Company home/dashboard context remains user-attention based, not a separate Company table.
2. W-ai profile state:
   - No profile routing yet unless save emits an event consumed by bridge.
   - Baseline expectation: future routing occurs under this company/account scope.
3. OV state:
   - No required OV artifact yet for settings-only changes.
4. Obsidian state:
   - No required note yet.
5. Event order:
   - If emitted, account/company update event is created before downstream bridge enqueue.

### Step 2: Create a new project (space)

User interaction:
1. Admin opens New Space/New Project form.
2. Admin enters project name and optional description/path inputs.
3. Admin submits creation.

Expected state afterward:
1. Bonfire state:
   - Project row exists with unique slug and path.
   - Creator is added to project_users.
   - Primary project room (Rooms::Project) is created if missing.
   - Membership exists for creator in the project room.
   - Default child channels/rooms (for example specifications/releases) are created as configured.
2. W-ai profile state:
   - Lifecycle intent should be classifiable as project-create flow.
   - If routed, delegator owns first decision point.
   - Lifecycle path requires linked knowledge delegation for OV structure consistency.
3. OV state:
   - Minimum expectation: project lifecycle is represented in OV structure if lifecycle routing runs.
4. Obsidian state:
   - No mandatory project note content yet, but project-level knowledge container is now available.
5. Event order:
   - Project creation event emitted.
   - Membership-first-join and/or member-added events emitted for creator path.
   - Room-created events emitted for main/default rooms.

### Step 3: Assign one additional user to project

User interaction:
1. Admin opens project user settings.
2. Admin adds one user to the project.

Expected state afterward:
1. Bonfire state:
   - User appears in project_users for that project.
   - Membership rows are granted for all active rooms in that project.
   - User can see project rooms in UI/sidebar after broadcast refresh.
2. W-ai profile state:
   - If membership/lifecycle events are routed, delegator classifies context as project membership change.
   - Knowledge sidecar may be used to preserve OV structure consistency for lifecycle-impacting changes.
3. OV state:
   - Membership change can appear as context update in OV if routed as lifecycle note.
4. Obsidian state:
   - Optional linkage update only; no required standalone note unless policy enforces one.
5. Event order:
   - project_member_added event emitted after project_user association writes.
   - Room/membership broadcast update follows membership grant.

### Step 4: Send one normal conversational message in project room

User interaction:
1. Assigned user opens project room chat.
2. User sends a normal non-action message, for example: "hello team, kickoff discussion started".

Expected state afterward:
1. Bonfire state:
   - Message row exists with creator, room_id, and body/plain text.
   - Room receive callback runs, setting unread state for other participants as applicable.
   - Push job/payload is prepared for relevant members.
2. W-ai profile state (expected order):
   - delegator checks company kanban existence.
   - delegator performs mention detection.
   - no bot mention and no direct main-profile command path.
   - delegator classifies as conversational content.
   - card is assigned to normal message.
   - normal message captures content into OV and does not send direct room reply.
3. OV state:
   - New conversational capture entry appears with room/project/company scope context.
4. Obsidian state:
   - Usually unchanged for a plain conversation unless knowledge extraction is explicitly triggered.
5. Event order:
   - message-created/room event emitted.
   - bridge persists event first, then queues processing.
   - queue worker dispatches to Hermes profile pipeline (completion order can vary under load).

## Scenario 2: Clear Actionable Request with Multi-user Collaboration

### Objective

Validate routing and handoff when a clear execution-oriented request is posted in an already configured project.

### Preconditions

1. Scenario 1 is complete.
2. Project has at least 3 members (admin + 2 assigned users).

### Step 1: User posts clear actionable message

User interaction:
1. User posts a clear task request, for example: "prepare release checklist by tomorrow with owners and blockers".

Expected state afterward:
1. Bonfire state:
   - New message persists in project room.
2. W-ai profile state (expected order):
   - delegator checks board existence and mention rules.
   - delegator classifies intent as execution/delivery coordination.
   - company kanban card is created and assigned to action or company_project (depending on project-planning emphasis).
3. OV state:
   - Conversational intent summary captured (either via normal message capture context or downstream summary flow).
4. Obsidian state:
   - Not required at this exact step.
5. Event order:
   - message event persisted, then queued for profile pipeline.

### Step 2: Profile handoff to project planning/execution owner

User interaction:
1. Team members continue discussion with details (owners, milestones, blockers).

Expected state afterward:
1. Bonfire state:
   - Follow-up messages persist in same room/thread context.
2. W-ai profile state:
   - If planning-heavy: card sits with company_project first.
   - If delivery-heavy: card sits with action first.
   - Handoff is represented by card reassignment, not direct profile invocation.
3. OV state:
   - Intent updates append to same scoped context (room/project/company/thread).
4. Obsidian state:
   - Optional only unless explicit knowledge artifact request appears.
5. Event order:
   - sequential chat events enter queue; processing is FIFO enqueue but completion can diverge when async fire-and-forget is enabled.

### Step 3: Introduce knowledge/document requirement in same flow

User interaction:
1. User adds: "also document final checklist rationale for onboarding".

Expected state afterward:
1. Bonfire state:
   - Message persisted.
2. W-ai profile state:
   - knowledge becomes valid owner or sidecar collaborator.
   - card may reassign from action/company_project to knowledge for documentation tasks, then back.
3. OV state:
   - Knowledge-relevant summary should appear linked to initiative context.
4. Obsidian state:
   - If Obsidian MCP is available, note/link update is expected.
   - If not available, equivalent knowledge state remains in internal knowledge records.
5. Event order:
   - documentation-intent event follows prior execution-intent messages, but resulting profile completions may interleave.

## Scenario 3: Ambiguous Request + Mention Rules + Lifecycle Knowledge Consistency

### Objective

Validate edge routing: unclear task triage, bot mention passthrough, main-profile mention rejection as direct command, and lifecycle-linked knowledge delegation.

### Preconditions

1. Existing active project and room.
2. At least one bot profile is configured for mention passthrough tests.

### Step 1: Post ambiguous request

User interaction:
1. User posts ambiguous text, for example: "do the needed thing for next week".

Expected state afterward:
1. Bonfire state:
   - Message persists normally.
2. W-ai profile state (expected order):
   - delegator board check and mention check run.
   - intent lacks required specificity.
   - card assigned to not_known_task.
   - not_known_task triages and reassigns to best-fit owner when enough context is found.
3. OV state:
   - Ambiguity and missing details are recorded in contextual summary.
4. Obsidian state:
   - No mandatory update at initial ambiguity point.
5. Event order:
   - ambiguous message event enters queue; triage processing may require follow-up prompts or reassignment events.

### Step 2: Test explicit bot mention passthrough

User interaction:
1. User sends explicit bot mention, for example: "@project manager summarize blockers".

Expected state afterward:
1. Bonfire state:
   - Message persists.
2. W-ai profile state:
   - delegator detects explicit bot profile mention.
   - original message is forwarded unchanged to the mentioned bot profile.
3. OV state:
   - OV capture may include the mention instruction and context.
4. Obsidian state:
   - Not mandatory unless bot triggers knowledge write.
5. Event order:
   - mention detection precedes normal intent classification branch.

### Step 3: Test explicit main-profile mention behavior

User interaction:
1. User sends explicit main profile mention, for example: "@knowledge do this now".

Expected state afterward:
1. Bonfire state:
   - Message persists.
2. W-ai profile state:
   - delegator detects mention as main profile.
   - main-profile direct command is ignored.
   - request continues through normal classification path and card assignment rules.
3. OV state:
   - Classification decision context is preserved.
4. Obsidian state:
   - Only if resulting classified intent requires knowledge artifacts.
5. Event order:
   - mention handling branch executes before final profile assignment.

### Step 4: Trigger project/room lifecycle request

User interaction:
1. User requests a lifecycle operation, for example: "create a dedicated release room" or "archive this room".

Expected state afterward:
1. Bonfire state:
   - Requested room/project lifecycle change is applied (new room created or status changed per permissions).
   - Membership visibility updates are broadcast.
2. W-ai profile state:
   - delegator assigns primary owner by intent (often company_project/action path).
   - linked knowledge delegation is additionally required for OV structure consistency.
3. OV state:
   - OV structure reflects lifecycle change and scope links remain consistent.
4. Obsidian state:
   - If enabled, project note linkage for the new/changed room context is updated.
5. Event order:
   - lifecycle event emitted after operation write.
   - bridge persists then enqueues.
   - profile processing applies primary owner flow plus knowledge sidecar.

## Consolidated Profile Processing Order (Used in all scenarios)

1. Ensure company kanban exists (create if missing).
2. Check for explicit mention.
3. If bot mention: passthrough unchanged.
4. If main-profile mention: ignore as direct command.
5. Determine if request is unclear.
6. If unclear: assign to not_known_task.
7. If clear: classify and assign to one of action, knowledge, normal message, company, company_project, cron_profile.
8. For room/project lifecycle tasks: add linked knowledge delegation for OV structure consistency.
9. Use kanban reassignment for handoff between main profiles.

## QA Validation Checklist

For each scenario step, capture evidence for all 5 dimensions below.

1. UI evidence:
   - Relevant page/room/project screenshot.
2. Data evidence:
   - Entity IDs/rows affected (Account setting, Project, Room, Membership, Message).
3. Routing evidence:
   - Profile owner/handoff result (delegator decision plus assigned owner).
4. Memory evidence:
   - OV entry created/updated as expected.
   - Obsidian note/link behavior validated when MCP is available.
5. Event evidence:
   - Event created, persisted, queued, and processed in expected sequence.

Pass criteria:
1. All expected state checks pass for every step.
2. Mention behavior matches policy (bot passthrough, main-profile non-direct).
3. Lifecycle tasks include linked knowledge delegation.
4. No room/project context leakage across unrelated scopes.
