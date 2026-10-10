# Plan-to-Ticket Architecture

> Type: Architecture
> Status: Active
> Scope: Structure and boundaries of the plan-to-ticket specialist: components, request flow, requirement/Plan/Ticket hierarchy, and Ticket output contract

## Scope

This repository packages the `plan-to-ticket` specialist inside a larger
main-agent workflow. Its job is to define one Plan per independent requirement,
one Ticket for ordinary work, and additional behavior Tickets only when
distinct boundaries justify them, then persist the Plan and Tickets to GitHub
Issues before branch work. There is no
application runtime, custom API client, or local ticket database in this
package; GitHub Issues are the workflow's external durable store.

## Logical architecture

![Plan-to-Ticket logical architecture](diagrams/plan-to-ticket-architecture.svg)

The source for this diagram is
[plan-to-ticket-architecture.puml](diagrams/plan-to-ticket-architecture.puml).
It describes the behavior exposed by the skill package rather than an
application infrastructure topology.

## Responsibilities

| Asset | Responsibility | Boundary |
| --- | --- | --- |
| [`skills/plan-to-ticket/SKILL.md`](../../../skills/plan-to-ticket/SKILL.md) | Defines requirement/Plan/Ticket planning rules, Issue persistence contract, Ticket structure, scope constraints, and verification expectations. | It plans and persists Issue records; it does not implement the planned change. |
| [`skills/plan-to-ticket/agents/openai.yaml`](../../../skills/plan-to-ticket/agents/openai.yaml) | Supplies the display name and short interface description. | It describes the skill in the interface; it does not define planning behavior. |
| GitHub Issues connector | Creates, finds, and updates one Plan Issue plus one child Issue per Ticket for every requirement. | It is the external durable authority; no local Markdown mirror is maintained. |
| This documentation package | Explains the bundle structure, behavior, output contract, and maintenance expectations. | Documentation does not add executable behavior. |

## Request flow

1. A requestor provides one independent requirement, which may ask for a feature, bug fix, refactor, documentation, configuration, dependency, test, or CI/CD change.
2. Codex uses the frontmatter description in `SKILL.md` to determine whether this skill applies.
3. The planning instructions use the available repository context to identify
   milestones, Ticket boundaries, Ticket dependencies, scope boundaries, and
   verification.
4. The skill defines each Ticket's complete execution and acceptance contract.
5. The skill resolves the repository's GitHub target, searches exact stable
   markers and Ticket ID collisions, normalizes matching Issue titles, and
   creates or updates one Plan Issue and its Ticket Issues before branch work
   for every requirement.
6. The skill assigns or resumes one branch and base branch for the Plan, records
   those values on the Plan Issue, and keeps all Tickets on that branch.
7. The successful output follows the contract in `SKILL.md`: a `Plan` section
   followed by complete Ticket sections with canonical Issue links and Plan
   branch handoff fields.
8. The main agent dispatches each Ticket to a fresh owner, who retains context
   across the Ticket and local repairs. After Development
   Complete, a separate fresh verifier checks all Ticket scenarios under the
   [scheduling policy](../../../AGENTS.md#multi-agent-delegation). A new
   Sol/high verifier can also satisfy final Plan acceptance only when the Plan
   has one Ticket and the full scope, artifact/version, configuration and
   deployment surface match exactly; otherwise final acceptance is a separate
   fresh whole-Plan check.

## Design boundaries

- The skill is a single cohesive module because its trigger, planning rules, and output format are tightly coupled.
- The interface metadata is kept separate from behavior so presentation changes do not alter planning semantics.
- The skill does not prescribe a project framework, dependency, command, or deployment platform unless repository context establishes it. It requires the available GitHub Issues connector for persistence but does not implement a custom API client.
- Ticket verification describes observable checks. It does not claim that implementation has already been completed.
- A required GitHub Issue failure blocks completion; chat
  output and local Markdown are not persistence fallbacks.
- Planning defines worker-ready Ticket contracts; the main agent
  dispatches Ticket owners and chooses safe concurrency under the canonical
  scheduling policy. Workers are leaves and never dispatch workers.
- Each Plan Issue maps to one independent requirement and one implementation
  branch and, when delivered, one PR; all child Tickets share that branch, and the PR head/base must match
  the Plan Issue metadata.
- Plan Issue titles use `[PLAN] <short plan title>`; Ticket Issue titles
  use `[T####] <short behavior/capability title>`. New `T####` identifiers are
  repository-scoped, four-digit, monotonically allocated, and never reused;
  historical duplicate IDs remain legacy records.
- Every requirement has one Plan Issue and at least one Ticket Issue; an
  ordinary requirement uses one Ticket, while complex work may use multiple
  Tickets only for distinct behavioral, dependency, or acceptance boundaries.
  If the user elects delivery, PR/merge/cleanup gates apply
  once for the Plan; local verification does not force publication.

## Requirement-to-Ticket hierarchy

Each independent requirement has one Plan Issue. Ordinary work uses one child
Ticket; complex work may use multiple behavior Tickets only where distinct
behavioral, dependency, or acceptance boundaries justify them. Supplementary
work for the same requirement updates its Ticket, adding another only for a
distinct boundary. An independent requirement always gets a new Plan, even
before another Plan merges. The runtime
[scope contract](../../../skills/plan-to-ticket/SKILL.md#scope-and-sizing) and
[publication rules](../../../skills/github-push-when-ready/SKILL.md#readiness-and-boundaries)
own scope updates and shared commit/PR gates. Real Ticket dependencies decide
execution order on the Plan branch.

## Ticket output contract

Each Ticket Issue holds its complete execution and acceptance contract:

- requirement goal, scope, exclusions, dependencies, and status;
- Function Checklist, concrete requirements, and observable acceptance;
- relevant context, test strategy and level, concrete test cases; and
- the smallest reliable validation command.

## Change guidance

When changing planning behavior:

1. Update the relevant rule or output-contract section in
   `skills/plan-to-ticket/SKILL.md`.
2. Check that the architecture boundaries and request flow in this document remain accurate.
3. Update this documentation index or repository layout if files or responsibilities change.
4. Verify the Markdown structure, frontmatter, and any rendered diagram before committing.
