# Profile Descriptions

This document introduces each profile and summarizes its role, boundaries, and collaboration flow.

Related document:
- `profile-workflows-and-interactions.md` for workflow and interaction Mermaid charts.

## Main Profiles

### delegator
Purpose:
- Central router and coordinator for incoming requests.

Core role:
- Classify intent.
- Ensure company kanban exists.
- Assign cards to the correct main profile.
- Forward explicit @mentions only when they target bot profiles.

Boundaries:
- Does not use room interaction tools for direct output.
- Main-profile mentions are not direct commands; delegator still decides routing.

### action
Purpose:
- Execution and delivery owner for operational work.

Core role:
- Drive delivery tasks and status updates.
- Maintain milestones, todos, bottlenecks, and all-hands execution records.
- Keep implementation progress current on kanban cards.

Boundaries:
- Uses company-kanban-assigned cards as source of truth.
- Hands off structure/knowledge-system changes to knowledge when needed.

### knowledge
Purpose:
- Knowledge and documentation owner.

Core role:
- Maintain project/company knowledge, summaries, decision context, and external assets.
- Keep structured knowledge artifacts aligned across room, project, and company context.
- Maintain OV knowledge consistency for lifecycle events.

Obsidian integration:
- If Obsidian MCP is available, use it for capture, linking, and updates.
- If unavailable, continue with standard knowledge tools and preserve the same structure.

### normal message
Purpose:
- Conversational content capture for OV.

Core role:
- Capture conversational context and intent into OV.
- Mark signals that may require follow-up.

Boundaries:
- No direct user reply output from this profile.
- add_message is not used by this profile.

### company
Purpose:
- Company-level coordination and cross-project alignment.

Core role:
- Maintain company-wide priorities, risks, dependencies, blockers, and strategic status context.
- Reassign company-scoped cards to other main profiles when execution or research is needed.

Boundaries:
- Delegates through company kanban card reassignment.
- Avoids holding implementation cards that clearly belong elsewhere.

### company_project
Purpose:
- Project-level coordination and sequencing.

Core role:
- Own project planning flow, execution slicing, and card readiness.
- Reassign project work to action, knowledge, or not_known_task as needed.
- Tag schedule-based items as cron and route through cron governance flow.

Boundaries:
- Main-profile interaction is through company kanban card reassignment.

### not_known_task
Purpose:
- Unclear-task triage owner.

Core role:
- Receive ambiguous cards.
- Determine best-fit owner profile.
- Reassign the card with clear rationale.

Boundaries:
- Must not keep cards after triage is complete.
- Does not directly invoke profiles outside kanban reassignment flow.

### cron_profile
Purpose:
- Cron governance and recurring-task orchestration.

Core role:
- Define what qualifies as a cron card.
- Validate recurrence intent.
- Reassign cron cards to non-cron owners.
- Create follow-up cards for repetitive schedules.

Boundaries:
- No direct profile invocation for execution.
- Uses company kanban reassignment as the handoff mechanism.

## Bot Profiles

### project manager
Purpose:
- Delivery planning and stakeholder alignment.

Core role:
- Define scope, WBS, milestones, and execution plans.
- Track blockers, dependencies, and decisions.
- Delegate implementation/research through kanban-assigned flows.

### business analyst
Purpose:
- Requirements and decision support.

Core role:
- Clarify scope, assumptions, constraints, and acceptance criteria.
- Produce decision-ready analyses.
- Coordinate execution-heavy follow-up with action and structure-heavy follow-up with knowledge.

### market research
Purpose:
- Evidence-driven market and competitor insights.

Core role:
- Run market scans, trend analysis, and opportunity framing.
- Produce research artifacts and structured findings.
- Route non-research execution items to action.

### coder
Purpose:
- Technical implementation and troubleshooting.

Core role:
- Implement, debug, and validate software changes.
- Maintain technical progress updates on related kanban cards.
- Coordinate long-term knowledge capture with knowledge when required.

### ask from w
Purpose:
- Lightweight request relay and conversational bridge.

Core role:
- Handle message relay and loading-message lifecycle.
- Forward requests into the correct routing workflow.

Boundaries:
- Does not own project-execution or knowledge-system domains.

## Interaction Model Summary

- Main profiles mostly interact by assigning and reassigning cards on the company kanban board.
- Cron flow always delegates by kanban reassignment, not direct invocation.
- For room/project create-delete operations, include a linked knowledge delegation to keep OV structure consistent.
