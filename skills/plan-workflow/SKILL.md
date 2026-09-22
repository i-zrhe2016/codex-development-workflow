---
name: plan-workflow
description: "Decide WHEN to plan. Turn a requirement into an executable work definition: understand the affected repository area, settle architecture and scope, and decompose the work into Tickets and Slices. Use when the request is to plan, design, investigate, or decompose before any code changes. It does not edit code, run the delivery verification, or publish anything."
---

# Plan Workflow

Stage workflow for the **requirement -> executable work definition**
transition. It decides *when* planning happens and *how much* planning the
requirement warrants; the decomposition and persistence procedure itself
belongs to the `plan-to-ticket` capability.

## Responsibility

- Read `docs/Repo_Current_State.md` and the affected code before proposing
  anything; verify the claims the request depends on.
- Normalize the original request into a compact Requirement Contract before
  decomposing work. Preserve the user's wording where it defines observable
  behavior or constraints, assign stable Requirement IDs, and never silently
  turn an uncertain assumption into a requirement.
- Establish the affected boundary, the interfaces it touches, and the
  constraints that already exist, including `AGENTS.md` rules in scope.
- Choose the simplest design that satisfies the requirement. Record a rejected
  alternative only when it explains a real decision.
- Split the requirement into behavior Tickets and dependency-ordered Slices.
- Name the acceptance criteria and the verification breadth each Slice will
  need, without executing it.
- Decide whether the work needs a persisted Plan Issue.

## Requirement Contract

Before decomposing the work, normalize the request into a compact contract:

- **Desired Outcome** — what must be true from the user's perspective when the
  work is finished.
- **Requirements** — stable IDs such as `R1`, `R2`, and `R3` for observable
  outcomes or explicit constraints.
- **Must Not** — explicit behaviors or changes that must not happen.
- **Non-goals** — related work intentionally excluded from this Plan.
- **Constraints** — verified architecture, compatibility, interface, security,
  performance, or repository constraints that materially affect the solution.
- **Assumptions** — implementation-relevant assumptions that are not yet facts.
- **Open Questions** — unresolved ambiguity that could materially change
  user-visible behavior, architecture, interfaces, persisted data,
  compatibility, security, or destructive behavior.

Do not resolve material ambiguity silently. Resolve it from authoritative
repository evidence when possible; otherwise preserve it as an explicit
assumption or open question.

## Requirement Fidelity Gate

Before creating Tickets or Slices, compare the Requirement Contract with the
original request and relevant repository evidence.

Planning may continue only when:

- every explicit requirement is represented;
- no planned behavior contradicts the request;
- no material behavior was invented without a Requirement ID or verified
  repository constraint;
- material ambiguity is resolved or explicitly recorded; and
- the planned scope still matches the Desired Outcome, Must Not, and Non-goals.

If material ambiguity would produce substantially different behavior or
architecture, return `BLOCKED` instead of choosing silently.

## Persistence decision

Persist a Plan and its child Tickets as GitHub Issues when any of these hold:

- the work is complex, crosses modules, or has internal dependencies;
- the work must survive a session boundary or be resumed by another agent;
- the user explicitly asks for a persisted plan.

Small, single-session work keeps its plan inline and moves straight to
`develop-workflow`. Use `plan-to-ticket` for the decomposition and, when a
trigger above applies, for its persistence contract. Title format, markers,
Ticket ID allocation, and branch naming stay exactly as `plan-to-ticket`
defines them.

## Not responsible for

- editing product, test, configuration, or documentation files;
- running the acceptance verification — that is `verify-workflow`;
- committing, pushing, opening a pull request, or merging — those are
  `publish-workflow` and `integrate-workflow`;
- closing Issues, or refreshing `docs/Repo_Current_State.md`, which happens
  after integration;
- the post-delivery process evaluation.

## Completion

Planning is complete when the Requirement Fidelity Gate passes, every
Requirement ID is traceable into the executable work definition, every Slice a
later stage will execute carries a scope, an out-of-scope boundary,
dependencies, acceptance criteria, a test strategy and level, and a validation
command, and the persistence decision above has been recorded. Return the plan
and stop; do not start implementing.
