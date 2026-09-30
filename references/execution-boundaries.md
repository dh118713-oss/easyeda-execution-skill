# Execution Boundaries

## Identity before mutation

Every plan must resolve and record:

- EasyEDA window id (when a bridge is used)
- project UUID and human-readable name
- schematic UUID/page UUID and/or PCB UUID
- document type and file path
- source revision tuple: design-intent/schematic revision, immutable board
  snapshot revision, and constraints revision (including the compatibility
  alias `pcb_constraints_revision`)

The executor must compare those values with the approved plan immediately
before the first write. A mismatch stops the run with `revision_mismatch`.

## API discipline

The installed `easyeda-api` skill is the source for bridge setup, API classes,
method signatures, enums, coordinate units, and readback methods. Before each
operation, consult the relevant documentation. Do not invent methods or enum
numbers, and do not treat a generated code snippet as proof that the method
exists. Promise-returning calls must be awaited and null/false responses must be
recorded as failures.

The executor must verify the active document type before invoking schematic or
PCB APIs. If the bridge has no connected window, the operation is `needs_input`;
it is not silently simulated.

## Operation boundaries

Allowed operations are limited to the plan: inspect identity, open/select the
approved project/document, apply approved schematic or PCB changes, synchronize
schematic to PCB, placement, routing, copper, run ERC/DRC, save, close/reopen,
and read back. No order, fabrication submission, unrelated project edit, global
setting change, or automatic library replacement is allowed.

Creating a board outline or copper pour object is not evidence that the board
is routed or poured. Read back actual primitives and check results. DRC errors,
unconnected nets, missing footprints, unresolved symbols, or stale revisions
remain visible even if the API call returned `true`.

## Evidence and statuses

Each operation records start/end time, request summary, target identity, API
method (when applicable), result summary, raw result or error, and evidence
references. `completed` means the requested operation and its readback passed.
The overall readback may use `completed` only after ERC, DRC, save, close/reopen,
and their four evidence records are present. `partial` means the API action
occurred but verification is incomplete.

The final design review status is independent from API status:

- `not_assessed`: no complete checks yet
- `issues_found`: ERC/DRC or semantic issues remain
- `human_review_required`: the scope is complex or evidence is incomplete
- `ready_for_beginner_review`: simple scope with complete evidence, still not a
  manufacturing or safety certification

## Complexity downgrade

The executor must stop before broad mutation when the source artifacts mark the
board `advanced_manual_review` or
`unsupported_without_specialist_input`. For `intermediate`, only explicitly
listed operations may run and the readback must contain a human-review item.
