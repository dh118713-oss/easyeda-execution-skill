---
name: easyeda-execution-skill
description: >-
  Execute approved schematic and PCB design intent in EasyEDA (嘉立创EDA) for
  beginner-friendly, low-risk boards. Verify project/document identity, apply
  only approved revisions, run ERC/DRC, save and reopen for readback, and report
  evidence-backed status without claiming design correctness from API success.
license: MIT
metadata:
  version: "0.1.0"
---

# EasyEDA Execution Skill

This is the execution layer for a three-part workflow:

1. The schematic skill produces a reviewed `design-intent.json` with exact
   device, package, pin assignments, net roles, and evidence.
2. The PCB routing skill produces reviewed `constraints.json` for placement,
   routing, return paths, and manufacturing checks.
3. This skill applies those artifacts in EasyEDA and returns a readback report.

It is intended for simple beginner boards: an MCU minimum system, indicators,
buttons, UART/I2C/SPI peripherals, low-speed ADC/DAC, CAN/RS485 transceivers,
USB device basics, SD cards, and similar conventional circuits.

## Required inputs

- An operation plan validated by `schemas/eda-operation-plan.schema.json`.
- An immutable schematic `design-intent` revision and, when PCB work is
  requested, a matching PCB routing constraints revision.
- The source revision tuple: `design_intent_revision`, `schematic_revision`,
  `board_revision`, `constraints_revision`, and the compatibility alias
  `pcb_constraints_revision`. The two schematic values and the two constraints
  values must match the artifacts that were actually reviewed.
- Exact EasyEDA project/document identity, or an explicit discovery step that
  resolves it before any write operation.
- An approval record naming the revision(s) and scope that may be changed.

Network names are not sufficient evidence for electrical roles. The execution
layer consumes semantic net and interface data from the upstream artifacts; it
must not infer `POWER`, `TX`, `SDA`, or similar roles from names alone.

## Execution rules

1. Check bridge health and the connected EasyEDA window before the first API
   operation. Select a window only after displaying its identity when more than
   one is connected.
2. Resolve the project UUID, document UUID, file path, and document type. A
   PCB API call requires an active PCB document; a schematic API call requires
   an active schematic page. Never assume the active tab is the requested one.
3. Read the relevant EasyEDA API class and enum documentation before writing
   an API call. Await promise-returning methods and use documented enum members;
   never guess a signature, numeric enum, coordinate unit, or object shape.
4. Verify approved source revisions immediately before mutation. If an artifact
   changed, stop with `revision_mismatch` and require a new plan.
5. Apply operations in plan order. Keep schematic edits, schematic-to-PCB
   synchronization, placement, routing, copper, and rule checks observable.
6. Run ERC/DRC using the documented API. Preserve raw results and detailed
   error nodes in readback; a boolean API success is only an execution result,
   not proof that the circuit is electrically correct, manufacturable,
   EMC-compliant, or safe.
7. Save, close/reopen the target document when supported, and read back project,
   document, primitives, nets, and check results. A save call without a
   successful readback is `partial`.
8. Never place an order, publish a manufacturing job, or change unrelated
   projects/global EasyEDA settings.

## Complexity gate

The planner must mark a request before execution as one of:

- `beginner_simple`: eligible for this workflow after review.
- `intermediate`: execution may proceed only for explicitly supported parts,
  with extra evidence and human review.
- `advanced_manual_review`: pause before irreversible or broad mutation.
- `unsupported_without_specialist_input`: do not execute.

High-speed SerDes/DDR, RF/antenna, mains or high voltage, high current,
isolated safety circuits, complex switching power, strict impedance/length
matching, and production EMC/thermal certification are not beginner-simple.

## Failure states

Use the status vocabulary in the schemas: `planned`, `running`, `completed`,
`partial`, `blocked`, `needs_input`, `revision_mismatch`, `api_error`, and
`manual_review`. On any failure, retain the operation index, API error, raw
readback, and the last known document identity. Do not report success when an
operation was skipped, only queued, or returned an unverified value.

## Output

Return a readback document validated by `schemas/eda-readback.schema.json`.
Include the plan id, source revisions, resolved project/document identity,
per-operation status, ERC/DRC raw results, save/reopen evidence, unresolved
questions, and a clear design-review status. The output should tell a beginner
what still needs a human check before ordering a board.

`completed` is reserved for a complete evidence loop. It requires completed
`run_erc`, `run_drc`, `save`, and `close_reopen` operations, ERC/DRC results that
were actually returned by the client, and evidence entries of kinds `erc`,
`drc`, `save`, and `reopen`. Otherwise use `partial`, `needs_input`,
`revision_mismatch`, `api_error`, or `manual_review` as appropriate.
