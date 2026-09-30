# EasyEDA Execution Skill

作者：**李继洲** · 许可证：[MIT](LICENSE)

这是“硬件学习蛊skill”的嘉立创EDA（EasyEDA）执行模块。它接收已经审查过的原理图意图和 PCB 约束，在明确版本的工程上执行有限操作，并通过 ERC、DRC、保存、重开和回读留下证据，帮助初学者看清板子还需要哪些人工检查。

这是三段式入门电路板工作流中的执行层，面向嘉立创EDA（EasyEDA）。它接收已经审查过的原理图设计意图和 PCB 约束，在明确的工程和文档上执行有限操作，再通过 ERC/DRC、保存、重开和回读产生可审查证据。

## 适用范围

适合 MCU 最小系统、LED/按键、UART、I2C、SPI、低速 ADC/DAC、CAN/RS485 收发器、基础 USB、SD 卡等常规简单板。高速 SerDes/DDR、射频、天线、市电/高压、大电流、复杂开关电源、隔离安规和量产 EMC 等场景会降级为人工审查或要求专家输入。

## 输入与输出

- 输入：`design-intent.json`、`constraints.json`、精确工程/文档身份、批准的 revision、`eda-operation-plan.json`。
- 输出：`eda-readback.json`，包含每个操作的状态、原始 ERC/DRC、保存与重开证据、未解决问题和人工检查项。

计划和回读都绑定同一组来源版本：`design_intent_revision` 与
`schematic_revision` 表示原理图意图，`board_revision` 表示不可变的 PCB
快照，`constraints_revision` 与兼容字段 `pcb_constraints_revision` 表示 PCB
约束。调用方必须让两组兼容字段保持相同值，并在执行前再次确认版本没有变化。

字段契约见：

- [`schemas/eda-operation-plan.schema.json`](schemas/eda-operation-plan.schema.json)
- [`schemas/eda-readback.schema.json`](schemas/eda-readback.schema.json)
- [`references/execution-boundaries.md`](references/execution-boundaries.md)

示例计划和回读见 [`examples/`](examples/)。它们是合成 fixture，不是通过 EasyEDA 执行得到的结果。JSON Schema 测试位于 [`tests/`](tests/)。

## 重要边界

API 返回成功只证明调用被 EasyEDA 接受，不证明原理图逻辑、封装、布局布线、EMC、热、安规或量产合格。本 Skill 不下单，不自动绕过 revision、ERC/DRC 或人工审查，也不凭网络名称猜测电气角色。

只有在 `status` 为 `completed` 时，回读才可以称为闭环完成：必须有已完成的
`run_erc`、`run_drc`、`save`、`close_reopen` 操作，ERC/DRC 原始结果，以及
`erc`、`drc`、`save`、`reopen` 四类证据。缺任何一项都应使用 `partial`、
`needs_input` 或相应失败状态。

本目录提供契约和执行边界，不包含操作 EasyEDA 的实现，也不声称具备 API 自动化绘图能力。实际执行必须有运行中的 EasyEDA 客户端、桥接扩展，并按本地 EasyEDA API 技能先查阅官方 API 文档。
