# required MCP tools

* Tools: `ai_task_cost`, `ai_tasks`, `create_ai_task`, `delete_ai_task`, `get_ai_task`, `get_ai_task_children`, `get_ai_task_parents`, `hello`, `update_ai_task`
* use the relevant task tools to read, create, update, and cost task records; do not rely on ad hoc task creation outside the supported MCP task surface

# when you read a task and start applying it
use tool to update the record and make dispatched true

* before starting work, verify the task exists and is not already finished; if it is already completed, do not re-open or duplicate it
* if the task is blocked by missing information, dependencies, or unclear requirements, record the issue in the task notes or status before proceeding
* when starting a task, update the task record to reflect the active execution state, including `dispatched = true`, current assignee/actor if tracked, and the start timestamp if available
* while working on the task, keep the task description and status aligned with the actual progress; do not silently ignore required inputs or partial work
* when task ends update record make finished true and update token_used & usd_used
* if the task was completed without a true end state, ensure the final result is recorded and the task is marked as finished only after validation
* if the task is a child task, confirm the parent context is still valid before continuing work; if the parent is complete or invalid, record that clearly
* when adding work output or notes, keep them factual and tied to the task so later review can understand the result and the resources consumed

# on creating new task

* before creating a task, check previous tasks for the same project, room, or topic context and confirm whether a similar task already exists
* if a matching task is already created and still relevant, reuse it instead of creating a duplicate; only create a new task when no equivalent task exists or the prior task is clearly stale/finished and needs a fresh follow-up
* when creating a task, always include `project_id`; add `room_id` only when the task is related to a room; add `topic_id` only when the task is related to a topic; `project_id` is required for every task
* when creating new task, if the current task is at any level, the new task must be created at `level + 1`.
* set the new task's `parent_id` to the current task's id; if the current task is a root task, set `parent_id` to `null` and the new task should be `level = 1` or the model's root-level default.
* if the task model includes a `grandparent_id` field, set it to the current task's `parent_id` when the current task is not a root task; if the current task is a root task, set `grandparent_id` to `null`.
* put your profile name on `adder_profile`.
* create a new row in the `ai_task` table (or the related task model) with all required fields populated, including:
  * `project_id`: required for every task
  * `room_id`: include if the task is related to a room
  * `topic_id`: include if the task is related to a topic
  * `title`: short task title or summary
  * `description`: task details / instructions - mention related entities for doing the tasks
  * `level`: current task level + 1
  * `parent_id`: current task id, or `null` for root-level task
  * `grandparent_id`: current task's parent_id when the current task is a child task, otherwise `null`
  * `adder_profile`: your profile name
  * `status`: initial state such as `pending`, `new`, or `open`
  * `dispatched`: `false`
  * `finished`: `false`
  * `token_used`: `0`
  * `budget_used`: `0`
  * `created_at` / `created_on`: current timestamp
  * `created_by` / `updated_by`: current profile if those columns exist
* if the model has additional fields such as `priority`, `assignee`, `tags`, `notes`, or `metadata`, fill them only when explicitly provided; otherwise leave them empty or default.
* do not leave required fields null or empty when the schema requires them.
* when the task is later started, update the record to set `dispatched = true`; when it ends, set `finished = true` and update `token_used` and `budget_used` accordingly.

## when not to create a task

* when used budget of parent task exceeds its allocated budget
* when the task is a duplicate of an existing relevant task
* when level of current task is 3 or higher
