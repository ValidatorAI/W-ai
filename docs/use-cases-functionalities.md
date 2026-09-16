# Bonfire W-space Pages: Meanings, Functionalities, Entities, and Use Cases

This document captures the functional meaning of six core Bonfire pages and summarizes how they are used in company and project operations.

## 1. Company Home

### Meaning
Company Home is a user-centric attention inbox. It is not a company master record page. It aggregates open attention items that require review, approval, or action.

### Functionalities
- Shows open attention count and category distribution.
- Highlights overdue and urgent items.
- Groups items by canonical categories.
- Supports resolve and dismiss actions for attention items.
- Provides quick navigation to related company/project contexts.

### Entities
- AttentionItem
- User
- Project
- Room

### Use Cases
- A user checks what needs action now.
- A user triages blockers and approvals before daily execution.
- A user opens linked project status or room context from an attention card.
- A user closes resolved items to keep attention queues clean.

### Notes and Assumptions
- Canonical category keys must stay normalized and consistent.
- The page is operational and queue-like, not archival.

## 2. Company Status

### Meaning
Company Status is a period-based company health and alignment page. It is used for monthly or periodic leadership review and cross-project narrative updates.

### Functionalities
- Selects a status period.
- Renders category-based status cards.
- Shows priorities, progress, risks, dependencies, changes, decisions, and learnings.
- Opens status item details for context and impact.
- Supports JSON payload rendering for status consumption.

### Entities
- CompanyStatusPeriod
- CompanyStatusItem

### Use Cases
- Leadership reviews current period priorities and risk posture.
- Teams align on dependencies and major changes.
- Stakeholders prepare executive or weekly summary updates.
- Teams record and review major decisions and lessons learned.

### Notes and Assumptions
- Intended as a periodic snapshot surface.
- Execution tasks should be routed to project-level operational pages after status review.

## 3. Project Overview

### Meaning
Project Overview is the project landing page and summary launchpad. It gives a high-level identity, participant, and context snapshot before deep execution views.

### Functionalities
- Displays project metadata and objectives.
- Shows contributors and AI teammates.
- Lists milestones and key alignment context.
- Displays linked rooms/channels and communication context.
- Provides quick links to Project Status, Project All-Hands, and Project Knowledge.

### Entities
- Project
- ProjectUser
- User
- Room
- ProjectMilestone
- AttentionItem

### Use Cases
- A project owner validates scope and participant alignment.
- A teammate opens the right operational page from a single entry point.
- A manager checks whether communication and contributors are aligned.
- A user audits project context before assigning work.

### Notes and Assumptions
- This is a high-level summary page, not the execution board itself.
- Should remain fast to scan and navigation-centric.

## 4. Project Status

### Meaning
Project Status is the operational control panel for current delivery health. It tracks progress, bottlenecks, immediate tasks, and practical context.

### Functionalities
- Shows phase and progress indicators.
- Surfaces active bottlenecks.
- Lists pending todos and next steps.
- Shows contextual knowledge items relevant to delivery.
- Presents a concise at-a-glance execution dashboard.

### Entities
- Project
- ProjectBottleneck
- ProjectTodo
- ProjectKnowledgeItem

### Use Cases
- Delivery owners assess if the project is on track.
- Teams prioritize blocker removal.
- Operators review next actionable items.
- Team members align daily execution with current project reality.

### Notes and Assumptions
- Focus is near-term execution and unblock flow.
- Deep documentation work belongs to Project Knowledge.

## 5. Project All-Hands

### Meaning
Project All-Hands is the team sync recap and decision-action ledger. It centralizes takeaways, decisions, and follow-up actions from all-hands coordination.

### Functionalities
- Shows active summary and key takeaways.
- Tracks action items and completion state.
- Records decisions with rationale and impact.
- Uses live update patterns for collaborative visibility.
- Provides empty-state handling when no recap data exists.

### Entities
- ProjectAllHandsTakeaway
- ProjectAllHandsActionItem
- ProjectAllHandsDecision
- Project

### Use Cases
- Teams review what was agreed in the latest all-hands sync.
- Owners track which follow-up actions are still pending.
- Stakeholders verify decision rationale and downstream impact.
- Coordinators keep decision/action records visible between meetings.

### Notes and Assumptions
- Functions as a meeting outcome surface.
- Long-form artifacts should be referenced from Project Knowledge when needed.

## 6. Project Knowledge

### Meaning
Project Knowledge is the project memory and documentation hub. It combines notes, external assets, ADRs, directory items, and knowledge activity.

### Functionalities
- Shows project Obsidian notes integration when configured.
- Lists external assets and reference links.
- Presents ADR records and decision artifacts.
- Displays directory tree and document structures.
- Shows recent knowledge activity entries.
- Supports markdown preview with safe file-path handling.

### Entities
- ProjectObsidianNote
- ProjectExternalAsset
- ProjectAdr
- ProjectDirectoryItem
- ProjectKnowledgeActivity
- Project

### Use Cases
- Teams browse current playbooks and reference docs.
- Engineers review ADRs before implementation.
- Stakeholders track recent knowledge changes.
- Users open markdown documentation from project storage safely.

### Notes and Assumptions
- This page is archive-plus-knowledge workflow, not a status board.
- Knowledge ownership should stay explicit across company/project/room context.

## 7. Cross-Page Functional Summary Matrix

| Page | Primary Meaning | Dominant Functional Goal | Primary Entity Groups |
| --- | --- | --- | --- |
| Company Home | Attention inbox | Triage and action routing | AttentionItem, Project, Room, User |
| Company Status | Periodic company snapshot | Leadership alignment and risk narrative | CompanyStatusPeriod, CompanyStatusItem |
| Project Overview | Project launchpad | Project context orientation and navigation | Project, ProjectUser, Room, ProjectMilestone |
| Project Status | Execution control panel | Delivery tracking and unblocking | Project, ProjectBottleneck, ProjectTodo, ProjectKnowledgeItem |
| Project All-Hands | Sync outcome ledger | Decisions and follow-up accountability | ProjectAllHandsTakeaway, ProjectAllHandsActionItem, ProjectAllHandsDecision |
| Project Knowledge | Knowledge archive hub | Documentation, ADR, and knowledge discovery | ProjectObsidianNote, ProjectExternalAsset, ProjectAdr, ProjectDirectoryItem, ProjectKnowledgeActivity |
