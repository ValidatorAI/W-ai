# Profile Workflows and Interactions

This document defines how profiles collaborate operationally.

## Core Interaction Rules

- Main profiles interact mostly through company kanban card assignment and reassignment.
- Explicit @mention passthrough is bot-only.
- Explicit @mention of main profiles is not a direct command.
- Cron work is delegated through kanban reassignment, not direct profile invocation.
- Room/project create-delete tasks include a linked knowledge delegation for OV structure consistency.

## Workflow 1: Entry and Mention Handling

```mermaid
flowchart TD
    U[User Message] --> D[delegator]
    D --> M{Explicit @mention?}
    M -- No --> C[Intent Classification]
    M -- Yes --> T{Mention type}
    T -- Bot profile --> B[Forward original message unchanged]
    T -- Main profile --> C
```

## Workflow 2: Intent Classification and Kanban Assignment

```mermaid
flowchart TD
    C[Intent Classification] --> R{Request Type}
    R -- Execution or Delivery --> A[action]
    R -- Research or Information --> K[knowledge]
    R -- Conversational Content to OV --> N[normal message]
    R -- Company Coordination --> CO[company]
    R -- Project Coordination --> CP[company_project]
    R -- Unclear --> U[not_known_task]
    R -- Recurring or Scheduled --> CR[cron_profile]

    A --> KA[Assign card on company kanban]
    K --> KK[Assign card on company kanban]
    N --> KN[Assign card on company kanban]
    CO --> KC[Assign card on company kanban]
    CP --> KP[Assign card on company kanban]
    U --> KU[Assign card on company kanban]
    CR --> KCR[Assign card on company kanban]
```

## Workflow 3: Unclear Task Triage

```mermaid
flowchart TD
    X[Unclear Card] --> U[not_known_task]
    U --> E{Best-Fit Owner}
    E -- action --> A[Reassign company kanban card]
    E -- knowledge --> K[Reassign company kanban card]
    E -- normal message --> N[Reassign company kanban card]
    E -- company --> CO[Reassign company kanban card]
    E -- company_project --> CP[Reassign company kanban card]
    E -- cron governance --> CR[Reassign company kanban card]
    E -- Still unclear --> Q[Request missing detail and keep triage note]
```

## Workflow 4: Company and Project Coordination

```mermaid
flowchart TD
    I[New Initiative or Card] --> S{Scope}
    S -- Company-wide --> CO[company]
    S -- Project-specific --> CP[company_project]

    CO --> H1[Align priorities blockers dependencies]
    CP --> H2[Align milestones todos bottlenecks]

    H1 --> G{Next Need}
    H2 --> G

    G -- Execution --> A[action]
    G -- Knowledge or Documentation --> K[knowledge]
    G -- Conversational OV capture --> N[normal message]

    CP --> L{Create/Delete Room or Project?}
    L -- Yes --> K2[Linked knowledge delegation for OV structure]
```

## Workflow 5: Cron Card Lifecycle

```mermaid
flowchart TD
    T[Recurring Need] --> CR[cron_profile]
    CR --> Q[Define cron qualification]
    Q --> TAG[Tag or Name card as cron]
    TAG --> O{Non-cron owner}

    O -- action --> A[Reassign company kanban card]
    O -- knowledge --> K[Reassign company kanban card]
    O -- company --> CO[Reassign company kanban card]
    O -- company_project --> CP[Reassign company kanban card]

    A --> REP{Repetitive schedule?}
    K --> REP
    CO --> REP
    CP --> REP

    REP -- Yes --> F[Create follow-up cron card]
    REP -- No --> Z[Close current card]
```

## Workflow 6: Main Profile Interaction Graph

```mermaid
flowchart LR
    D[delegator] --> A[action]
    D --> K[knowledge]
    D --> N[normal message]
    D --> CO[company]
    D --> CP[company_project]
    D --> U[not_known_task]
    D --> CR[cron_profile]

    CO --> A
    CO --> K
    CO --> CP
    CO --> U

    CP --> A
    CP --> K
    CP --> U
    CP --> CR

    U --> A
    U --> K
    U --> N
    U --> CO
    U --> CP
    U --> CR

    CR --> A
    CR --> K
    CR --> CO
    CR --> CP
```

## Workflow 7: Bot Entry Points into Main Routing

```mermaid
flowchart LR
    PM[project manager] --> D[delegator]
    BA[business analyst] --> D
    MR[market research] --> D
    CD[coder] --> D
    AW[ask from w] --> D
```

## Notes

- normal message captures conversational content into OV and does not send direct user replies.
- knowledge uses Obsidian MCP for linked knowledge updates when available.
- Main-profile handoff should be represented as kanban card assignment/reassignment.
