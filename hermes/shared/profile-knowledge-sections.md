# Profile-ready Knowledge Sections for Bonfire Page Use Cases and Functionalities

This document converts page-level behavior into reusable profile sections that can be appended into SOUL profile files.

## Required Section Schema

Every reusable section below includes:
- Intent
- Trigger
- Expected Behavior
- Key Entities
- Boundaries
- Example Task Framing
- Related Profiles

## Reusable Sections

### SECTION-CH-01: Company Home Attention Triage

#### Intent
Keep user attention queues actionable and prioritized.

#### Trigger
Use when a task asks what needs attention, approval, or immediate follow-up at company level.

#### Expected Behavior
1. Review open attention items grouped by canonical category.
2. Prioritize blockers, overdue items, and decision-waiting items.
3. Route each item to the most relevant project, status, knowledge, or room context.
4. Resolve or dismiss items only with clear rationale.

#### Key Entities
- AttentionItem
- User
- Project
- Room

#### Boundaries
- Do not treat this as a company archival dashboard.
- Do not replace period status reporting with attention triage.

#### Example Task Framing
"Review Company Home attention items, prioritize blockers and approvals, and produce an action queue for today."
#### W-bridge MCP Tools to Use
- Read and triage attention queues: `mentions`, `blockers`, `decisions_waiting`, `ai_confirm`, `material_changes`, `outcomes_review`, `knowledge_proposals`.
- Create new attention signals: `add_mentions`, `add_blockers`, `add_decisions_waiting`, `add_ai_confirm`, `add_material_changes`, `add_outcomes_review`, `add_knowledge_proposals`.
- Update or resolve existing items: `edit_mentions`, `edit_blockers`, `edit_decisions_waiting`, `edit_ai_confirm`, `edit_material_changes`, `edit_outcomes_review`, `edit_knowledge_proposals`.
- When triage needs an explicit room decision flow: `add_approve_request_with_message`, `approval_requests`, `add_decision_message`.

#### Related Profiles
- Main: delegator, company, not_known_task
- Bot: project manager, business analyst, ask from w

### SECTION-CS-01: Company Status Period Review

#### Intent
Maintain a period-based company narrative for priorities, risk, dependencies, and decisions.

#### Trigger
Use when users request monthly/periodic company health, executive summary, or cross-project alignment.

#### Expected Behavior
1. Select the correct status period before analysis.
2. Summarize priorities, progress, risks, dependencies, changes, decisions, and learnings.
3. Highlight impact and ownership for each major status signal.
4. Route execution follow-ups to project-level owners and trackers.

#### Key Entities
- CompanyStatusPeriod
- CompanyStatusItem

#### Boundaries
- Do not collapse detailed execution tracking into this page.
- Do not publish status without period context.

#### Example Task Framing
"Prepare a company status summary for the current period with top risks, decisions, and dependency actions."
#### W-bridge MCP Tools to Use
- Select and manage the status period envelope: `company_status_period`, `add_company_status_period`, `edit_company_status_period`.
- Work category streams inside the chosen period: `priorities`, `progress`, `risks`, `dependencies`, `changes`, `decisions`, `learnings`.
- Use the category tools in this order for predictable reporting: list current state, add missing items, then edit status, health, and ownership details.

#### Related Profiles
- Main: company, company_project, cron_profile, knowledge
- Bot: project manager, business analyst, market research, ask from w

### SECTION-PO-01: Project Overview Context Launch

#### Intent
Provide a fast project orientation point before deep execution pages.

#### Trigger
Use when users need project scope context, team visibility, milestones, or navigation to project subviews.

#### Expected Behavior
1. Confirm core project metadata, objective, and ownership context.
2. Surface contributors, AI teammates, milestones, and channels.
3. Identify open attention volume and major context gaps.
4. Route to Project Status, All-Hands, or Knowledge based on user intent.

#### Key Entities
- Project
- ProjectUser
- User
- Room
- ProjectMilestone
- AttentionItem

#### Boundaries
- Do not use this page as the source of detailed blocker/todo state.
- Do not skip validation of project membership context.

#### Example Task Framing
"Use Project Overview to validate team alignment and then route to the correct execution view."
#### W-bridge MCP Tools to Use
- Build the execution-side project snapshot: `project_milestones`, `project_todos`, `project_bottlenecks`.
- Pull collaboration and decision context: `project_all_hands_takeaway`, `project_all_hands_action_item`, `project_all_hands_decision`.
- Pull knowledge context before routing: `project_knowledge_items`, `project_decision_records`.
- Use company-home signals to detect cross-cutting urgency: `mentions`, `blockers`, `decisions_waiting`.
- Note: there is no single aggregate "project overview" tool, so compose overview context from these tool groups.

#### Related Profiles
- Main: delegator, company_project, normal message, not_known_task
- Bot: project manager, business analyst, market research, ask from w

### SECTION-PS-01: Project Status Execution Control

#### Intent
Track delivery health and drive near-term execution progress.

#### Trigger
Use when users ask for progress, blockers, next steps, or operational project state.

#### Expected Behavior
1. Review project phase and percent completion.
2. Surface bottlenecks and rank them by delivery risk.
3. Review pending todos and convert to clear next actions.
4. Use knowledge items as execution context for immediate decisions.

#### Key Entities
- Project
- ProjectBottleneck
- ProjectTodo
- ProjectKnowledgeItem

#### Boundaries
- Do not treat this page as long-term documentation storage.
- Do not defer blocker escalation when delivery risk is rising.

#### Example Task Framing
"Assess Project Status, identify top 3 blockers, and produce an ordered next-step plan."
#### W-bridge MCP Tools to Use
- Core project status reads and writes: `project_bottlenecks`, `add_project_bottleneck`, `edit_project_bottleneck`, `delete_project_bottleneck`.
- Todo pipeline control: `project_todos`, `add_project_todo`, `edit_project_todo`, `delete_project_todo`.
- Milestone alignment for timeline health: `project_milestones`, `add_project_milestone`, `edit_project_milestone`, `delete_project_milestone`.
- Context support for status decisions: `project_knowledge_items`, `project_decision_records`.

#### Related Profiles
- Main: action, company_project, cron_profile, not_known_task
- Bot: project manager, coder, ask from w

### SECTION-PA-01: Project All-Hands Decision and Action Ledger

#### Intent
Capture team sync outcomes as accountable actions and decisions.

#### Trigger
Use when users request meeting recap, action item follow-up, or decision rationale review.

#### Expected Behavior
1. Read active summary and key takeaways.
2. Review pending action items and ownership.
3. Validate recorded decisions with rationale and impact.
4. Update completion state and route unresolved items to execution owners.

#### Key Entities
- ProjectAllHandsTakeaway
- ProjectAllHandsActionItem
- ProjectAllHandsDecision
- Project

#### Boundaries
- Do not let action items remain ownerless.
- Do not store long-form knowledge here when it belongs in Project Knowledge.

#### Example Task Framing
"Review All-Hands outputs, close completed items, and assign unresolved decisions to owners."
#### W-bridge MCP Tools to Use
- Manage meeting takeaways: `project_all_hands_takeaway`, `add_project_all_hands_takeaway`, `edit_project_all_hands_takeaway`, `delete_project_all_hands_takeaway`.
- Manage decision records from all-hands: `project_all_hands_decision`, `add_project_all_hands_decision`, `edit_project_all_hands_decision`, `delete_project_all_hands_decision`.
- Manage follow-up actions: `project_all_hands_action_item`, `add_project_all_hands_action_item`, `edit_project_all_hands_action_item`, `delete_project_all_hands_action_item`.
- Escalate unresolved actions into delivery tracking when needed: `add_project_todo`, `edit_project_todo`.

#### Related Profiles
- Main: action, company_project, cron_profile, knowledge
- Bot: project manager, business analyst, coder

### SECTION-PK-01: Project Knowledge and ADR Navigation

#### Intent
Maintain discoverable project memory across notes, assets, ADRs, directory items, and activity.

#### Trigger
Use when users need documentation lookup, ADR review, knowledge traceability, or file-based reference context.

#### Expected Behavior
1. Locate the right knowledge source (Obsidian note, external asset, ADR, directory file, or activity).
2. Provide concise context summary and relevant links/paths.
3. Preserve safe file access and path validation.
4. Route implementation follow-ups to execution profiles when needed.

#### Key Entities
- ProjectObsidianNote
- ProjectExternalAsset
- ProjectAdr
- ProjectDirectoryItem
- ProjectKnowledgeActivity

#### Boundaries
- Do not bypass safe path constraints for file preview.
- Do not substitute status tracking for documentation management.

#### Example Task Framing
"Use Project Knowledge to retrieve the latest ADR and supporting playbooks before implementation planning."
#### W-bridge MCP Tools to Use
- Primary knowledge records: `project_knowledge_items`, `add_project_knowledge_item`, `edit_project_knowledge_item`, `delete_project_knowledge_item`.
- ADR lifecycle: `project_decision_records`, `add_project_decision_record`, `edit_project_decision_record`, `delete_project_decision_record`.
- External references and sources: `external_knowledge_assets`, `add_external_knowledge_asset`, `edit_external_knowledge_asset`, `delete_external_knowledge_asset`.
- Knowledge traceability and summaries: `knowledge_activity_log`, `add_knowledge_activity_log`, `edit_knowledge_activity_log`, `delete_knowledge_activity_log`, `knowledge_summary_items`, `add_knowledge_summary_item`, `edit_knowledge_summary_item`, `delete_knowledge_summary_item`.
- Obsidian and directory context: `project_obsidian_note`, `add_project_obsidian_note`, `edit_project_obsidian_note`, `delete_project_obsidian_note`, `tree_based_project_directory_data`, `add_tree_based_project_directory_item`, `edit_tree_based_project_directory_item`, `delete_tree_based_project_directory_item`.

#### Related Profiles
- Main: knowledge, company_project, normal message
- Bot: business analyst, market research, coder

## Section-to-Profile Index

| Section ID | Topic | Related Profiles |
| --- | --- | --- |
| SECTION-CH-01 | Company Home Attention Triage | delegator, company, not_known_task, project manager, business analyst, ask from w |
| SECTION-CS-01 | Company Status Period Review | company, company_project, cron_profile, knowledge, project manager, business analyst, market research, ask from w |
| SECTION-PO-01 | Project Overview Context Launch | delegator, company_project, normal message, not_known_task, project manager, business analyst, market research, ask from w |
| SECTION-PS-01 | Project Status Execution Control | action, company_project, cron_profile, not_known_task, project manager, coder, ask from w |
| SECTION-PA-01 | Project All-Hands Decision and Action Ledger | action, company_project, cron_profile, knowledge, project manager, business analyst, coder |
| SECTION-PK-01 | Project Knowledge and ADR Navigation | knowledge, company_project, normal message, business analyst, market research, coder |
