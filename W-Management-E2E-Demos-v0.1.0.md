# W — General E2E Use Cases for Management and Venture Building

> Version: 0.3.0  
> Date: 2026-09-29  
> Status: Draft demo scenarios

## How to use these demos

These are not demo stories for a single company. They are repeatable end-to-end use cases for management teams, investment groups, venture studios, and individual startups. In every case, W connects the same chain:

```text
Question or goal → shared context → decision → work by people and AI →
verifiable output → measured outcome → learning and next step
```

LongRiver can be the investor and strategic owner; LongRiver LAB can be the venture-building and execution team. The same scenarios also work for any portfolio, startup, or internal product team.

For a management demo, select three scenarios for a 20–25 minute session. External communication, production deployments, and metrics must use a sandbox or clearly labelled simulated demo data.

## Use-case overview

| # | Use case | Question it answers | Primary user |
|---:|---|---|---|
| 1 | Portfolio and priority decision | Where does leadership need to intervene now? | CEO, board, investor |
| 2 | Blocker to executed action | How does a decision safely turn into a concrete action? | Venture lead, COO |
| 3 | Product-market fit validation | Does a startup have evidence that it solves a valuable, repeatable problem? | Founder, product lead, investor |
| 4 | From hypothesis to code and deployment | How do we deliver a product change and verify its impact? | CPO, CTO, venture team |
| 5 | Positioning and go-to-market | Does communication create relevant demand, or just reach? | CEO, marketing, business development |
| 6 | Project takeover and knowledge | How does a new owner understand the real state without status meetings? | COO, new lead |

## 1. Portfolio and priority decision

**Promise:** leadership sees a live view of the portfolio or company and makes decisions using evidence rather than manually assembled reports.

### Starting situation

Leadership is preparing for a portfolio review. Across projects there are delivered outputs, plans, dependencies, and blockers. They do not all have the same credibility or require a board-level intervention.

### E2E flow

1. Open the company or portfolio view. It shows priority outcomes, material changes, risks, dependencies, and items needing a decision.
2. Ask: **“What has changed since the last review, and what requires a leadership decision?”**
3. W answers in impact order and shows sources, last-refresh time, and confidence for each claim.
4. Open one blocker. The view separates verified facts, plans, missing external input, and decision options.
5. Leadership selects an option and confirms an owner, deadline, and authority boundary.
6. W records the decision as a shared object, assigns follow-on work, and refreshes the state without asking the team to prepare another status report.

### Evidence to show

- the decision has a rationale, sources, owner, and due date;
- the portfolio view can expose uncertainty, not just a traffic-light status;
- the team was not given a new task to “prepare the report.”

### LongRiver / LAB example

LongRiver decides whether and how to escalate an external dependency at a portfolio company; LongRiver LAB receives unambiguous ownership of the next action.

## 2. From a blocker to a verifiable executed action

**Promise:** an AI teammate performs bounded work, while human judgment, permissions, and accountability remain explicit.

### Starting situation

A project cannot progress without a partner response, document approval, system update, or other concrete action. The team needs to know exactly who may act and what has actually been done.

### E2E flow

1. Open the project from the decision. W shows the goal, blocker, owner, deadline, and smallest useful next step.
2. The lead assigns an AI teammate a clear task: prepare the materials and proposed action; an external send or system change requires human approval.
3. Show the assignment card: goal, relevant context, allowed tools, boundaries, expected output, and completion evidence.
4. The agent prepares the materials. Its state is **waiting for approval**, not “done.”
5. The accountable person reviews the result and approves execution in a sandbox or authorised system.
6. The agent performs the action. W records the requester, agent, approval, changed system or artefact, evidence, and any failure.
7. A response or system change is linked to the intended outcome; W distinguishes an early signal from a verified result.

### Evidence to show

- draft, approval, and execution are distinct states;
- the action is auditable and recoverable after a partial failure;
- the agent cannot expand its own permissions.

### LongRiver / LAB example

LAB prepares materials for a technical or regulatory dependency of a portfolio company; the venture lead approves them and the agent demonstrably sends them to a demo contact.

## 3. Startup product-market fit validation

**Promise:** PMF is neither a feeling after a few positive conversations nor a count of completed features. It is repeatable evidence that a clearly chosen segment wants to solve a specific problem in a way the startup can sustainably deliver.

### Starting situation

A startup has a product idea and a few customer signals, but does not know whether to invest in broader development, change the segment, or test another hypothesis. The founder, venture team, and investor need the same version of reality.

### E2E flow

1. The founder creates a PMF project and records the hypothesis: target segment, painful problem, proposed solution, current alternative, and expected behaviour change.
2. W requests the minimum evidence and metrics: a qualified sample, customer interviews, activation, repeat use, willingness to pay, conversion, or another signal that fits the business model.
3. The Researcher analyses interviews, competitors, and available market evidence. Quotes, interpretation, and hypotheses remain visibly separate.
4. The team uses the evidence to decide **which segment and problem to test first**. W links the decision to the experiment and outcome owner.
5. The Builder creates the smallest suitable experiment: a prototype, landing page, concierge service, limited MVP, or integration pilot. It is not automatically a full application.
6. After approval, the agent performs permitted work — for example, prepares research invitations, configures a demo funnel, creates a prototype, or records consented results in a CRM. A human always approves sensitive external communication.
7. W connects the experiment to measurement. It shows qualified participants, activation, repeat use, conversion, feedback, and evidence quality — not page views alone.
8. At the review point, the team explicitly chooses one of three paths: **continue and expand**, **change the hypothesis**, or **stop**. W preserves a negative result as learning and creates the next small step.

### Evidence to show

| Layer | Example evidence | Not PMF evidence |
|---|---|---|
| Problem | a repeated, concrete problem in the selected segment | generic praise for the idea |
| Behaviour | activation, return use, paid pilot, workflow change | a site visit or “like” |
| Economics | willingness to pay, budget owner, ROI, or pricing signal | stated interest without commitment |
| Repeatability | a similar signal across multiple qualified customers | one enthusiastic early adopter |

### What to say

> “The goal is not to prove that our idea is right. The goal is to learn what is true as cheaply as possible, then change the next step accordingly.”

### LongRiver / LAB example

LongRiver LAB validates a new fintech or digital-asset venture: it selects a regulated segment, tests a specific workflow, and only then decides whether a larger product, licensing, or capital investment is justified.

## 4. From product hypothesis to code, deployment, and outcome

**Promise:** development does not start with a vague ticket or end with a merge request. It remains connected to a decision, a safe deployment, and measured change for users or operations.

### Starting situation

A PMF experiment or customer pilot reveals a problem worth implementing. The team must deliver a limited product change safely, without unclear handoffs between business, product, and engineering.

### E2E flow

1. Evidence from the PMF project becomes a decision: which specific hypothesis the product change will test, for whom, and how success will be measured.
2. The product owner uses W to create a short implementation brief: user problem, scope, non-goals, acceptance criteria, risks, outcome owner, and post-release measurement plan.
3. The Builder and Reviewer prepare a technical design: components, integrations, data protection, migrations, test strategy, rollback, and permission boundaries. A person approves scope and any production risk.
4. In an authorised repository, the agent creates an isolated branch, implements the small change, runs tests, and attaches the code, test results, and unresolved questions to one work item.
5. A person or Reviewer performs code review. W clearly shows **ready for review**, **changes requested**, and **approved for staging**. A merge must never be presented as a deployment.
6. After approval, the agent deploys to staging, runs smoke and integration tests, and stores build, version, test evidence, and the deployment link.
7. Production deployment requires an explicit policy-based approval. The agent performs a gradual rollout, or prepares an approved release. W records the approver, version, time, rollout scope, and rollback plan.
8. After deployment, W tracks the agreed signals: activation, workflow success, error rate, support tickets, conversion, or a regulatory control point. If the signal deteriorates, it creates an incident or rollback decision; if it improves, it plans an expansion.
9. The team records the outcome as confirmed, unconfirmed, or inconclusive. The documented learning determines the next product step.

### Control points to make visible in the demo

| Phase | What “done” means | Required evidence |
|---|---|---|
| Specification | agreement on a small scope and measurement | approved brief and acceptance criteria |
| Implementation | the code change exists | commit/PR, tests, review state |
| Staging | the change works outside production | version, deployment, test evidence |
| Production | the change is deployed within the authorised scope | approval, release record, monitoring |
| Outcome | the user or operational change is known | metric, source, and confidence |

### What to say

> “An agent can code and deploy within controlled boundaries. Accountability does not disappear: every step has an owner, approval, evidence, and a safe route back.”

### LongRiver / LAB example

LAB delivers a limited change to a portfolio product or internal tool. LongRiver sees not simply that “development is happening,” but which hypothesis is being tested, what was deployed, and what commercial or operational impact followed.

## 5. Positioning and go-to-market with measurable learning

**Promise:** content, outreach, and offers are means to validate market demand, not ends in themselves.

### E2E flow

1. The team records the target audience, value hypothesis, and intended outcome — for example, qualified conversations, pilot requests, or partner leads.
2. The Researcher creates sourced inputs; the Builder creates a post, offer, landing page, or outreach draft.
3. The Reviewer checks factual accuracy plus regulatory and brand boundaries. Sensitive claims and external delivery wait for human approval.
4. After execution, W attaches delivery or publication evidence and relevant responses from authorised systems.
5. At review, W connects the output to signal quality: qualified contacts, replies, meetings, pilots, or conversion. The team decides from the evidence whether to repeat, change, or stop the hypothesis.

### LongRiver / LAB example

LongRiver tests whether its thesis on regulated digital financial infrastructure creates relevant B2B and investor conversations; LAB tests demand for a specific venture or service.

## 6. Project takeover and approved knowledge

**Promise:** a new owner receives the current state in minutes, rather than a link to a long chat history and a folder of files.

### E2E flow

1. The new lead opens the project catch-up view: goal, current state, decisions, evidence, blocker, next step, and open uncertainties.
2. They ask: **“Why did we choose this direction, and what must be true for us to continue?”**
3. W returns a concise, sourced answer that clearly distinguishes fact, decision, and hypothesis.
4. The Knowledge Curator proposes a reusable lesson as a knowledge candidate. The accountable person approves, edits, or rejects it.
5. If a later result contradicts it, the knowledge is superseded by a newer version; history and the reason for change remain traceable.

## Recommended demo combinations

| Audience | Main flow | What the audience sees |
|---|---|---|
| Board / investor | 1 → 3 → 4 | capital priority, PMF evidence, controlled deployment |
| Venture studio / LAB | 1 → 2 → 3 → 4 | decision, execution, market validation, product delivery |
| Product and engineering | 3 → 4 → 6 | hypothesis, code and release, shared learning |
| Sales and go-to-market | 3 → 5 → 1 | segment, demand validation, management decision |

## Demo principles

- Start with the decision-maker’s question, not product navigation.
- Show a source, confidence level, human approval, and execution evidence at least once.
- Explicitly distinguish **plan**, **draft**, **approved**, **executed**, and **verified outcome**.
- A negative or inconclusive experiment is a valid result; W must not pretend it succeeded.
- Use a sandbox, test repository, and fictional or anonymised data. Do not use real customers, production credentials, or non-public investment information in a live demo.
