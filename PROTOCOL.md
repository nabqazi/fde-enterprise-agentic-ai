# Protocol — working with AI coding agents

One-page reference. How I run sessions, lock decisions, and keep an autonomous
coding agent inside the rails of an approved spec.

## Session types I run

- **Investigate** — open-ended exploration. Output is notes, not edits. Used to
  understand the problem before scoping it.
- **Design** — produce or revise a spec, ADR, or charter. Output is markdown
  under `foundation/` or `specs/`. No code changes.
- **Build** — execute against a locked spec. Output is code. Scoped to the file
  list named in the dev ticket. No silent scope expansion.
- **Review** — HITL gate. Read the diff, run the security checklist, accept or
  refine. Output is a `R-NNN-*.md` log.

A session is one type. Switching mid-session is a smell — close the current
session and open a new one with the right type.

## Decisions are locked or registered

Every real choice has one of two homes:

- **Locked** — an ADR under `foundation/`. Status, context, decision,
  consequences, alternatives. Immutable once merged; superseded by a new ADR if
  the world changes.
- **Registered** — a row in `GAPS-REGISTER.md` with an explicit revisit
  trigger. Deferring is fine; deferring without writing it down is not.

There is no third option. A choice made silently in code is drift.

## MCQ before silent pick

When a tradeoff is real — model choice, framework choice, output shape,
deferral that closes off a future option — I surface it as a multiple-choice
question to the human owner before picking. Two to four options, each with the
honest downside named. The human picks; I record the pick in the ADR or the
gap row. If I find myself about to write "I went with X because it seemed
cleaner," that is the cue to stop and write the MCQ instead.

## HITL gates

Two checkpoints are blocking, not advisory:

- **Code review gate** — before any agent-written code is considered shippable,
  a human reads the diff against the dev ticket's file list and Do-NOT list.
  Refinements go back to the agent. Logged in `reviews/R-NNN-*.md`.
- **Security gate** — a short, fixed checklist runs against every shippable
  unit: prompt injection surface, secret handling, output rendering, code
  execution, dependency surface. Each item is Pass with mitigation noted, or
  Deferred with a GAP id. No verbal "looks fine."

Gates that are sometimes-skipped become always-skipped. They are blocking.

## Anti-hallucination rails in dev tickets

A dev ticket handed to a coding agent always carries five things:

1. **Linked artifacts** — the spec, the ADRs, this protocol. The agent reads
   them before writing.
2. **Scoped file list** — exact paths, no others. New files outside the list
   are a rejection condition at the review gate.
3. **Per-file scope** — 2–4 sentences naming what goes in each file. Prevents
   the agent from inventing layers.
4. **Explicit Do-NOT list** — the failure modes I've seen this class of agent
   produce. Named so they can't be rationalized.
5. **Success criteria and signals** — runnable commands and observable
   outputs. "It works" is not a success criterion.

If a ticket is missing any of the five, it goes back to design, not to the
agent.
