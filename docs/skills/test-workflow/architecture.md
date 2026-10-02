# 通用测试工作流架构

> Type: Architecture
> Status: Active
> Scope: Structure of the test-workflow specialist: verification levels and gradient, risk branches, Test Quality Gate, failure handling, and the browser/E2E branch

## 目标

`test-workflow` 面向后端、前端、API、库和 CLI 等仓库变更，从需求、Slice 功能
清单、验收标准和现有契约中提炼最小高价值测试集，并按成本从低到高逐层
验证。浏览器验证只在行为对用户可见或验收明确要求端到端流程时启用。

![test-workflow 风险驱动验证与 Test Quality Gate](diagrams/test-workflow-flow.svg)

Source: [`diagrams/test-workflow-flow.puml`](diagrams/test-workflow-flow.puml)

## 核心数据流

1. 从需求、Slice 验收标准和本次实际改动中确定行为契约。
2. 建立 Acceptance-to-Test Matrix，把每条验收标准映射到实际执行证据。
3. 根据风险选择 mandatory dimensions：happy path、boundary、negative、state/invariant、integration/contract、regression，以及按需的 property/fuzz、mutation、browser/E2E、isolation/flaky。
4. 从静态检查和 focused tests 开始，按成本逐级执行适用维度。
5. 每个验收点和 mandatory dimension 都必须有 PASS 证据，或明确的 N/A 理由；未执行不能冒充通过。
6. Test Quality Gate 汇总结果并按 `pass`、`partial`、`fail` 或 `blocked` 分类。

## 验证级别

| Level | 主要用途 |
|---|---|
| `minimal` | 微小或非行为变更。 |
| `focused` | 默认；覆盖当前 Slice 验收标准的最小检查。 |
| `regression` | 缺陷修复、跨模块变更或已有回归风险。 |
| `full` | 高风险、发布门禁或明确要求完整套件。 |

Level 只限制 suite 的广度。Stop condition 是 mandatory risk dimensions 已满足，
而不是某一级测试已经 GREEN；验收标准、失败证据、受影响边界、发布要求或
风险画像都可以触发扩大范围。

## 验证梯度

| 层级 | 主要用途 | 典型证据 |
|---|---|---|
| 静态检查 | 尽早发现编译、类型、Lint、Schema 或配置问题 | 命令输出、错误位置和修复后的重新检查 |
| Focused tests | 验证本次变更直接影响的单元、组件、API 或包契约 | 测试结果、断言和失败堆栈 |
| Boundary / negative | 验证边界值、无效输入、失败路径和状态转换 | 明确输入、预期错误/状态和断言 |
| Property / fuzz | 对复杂输入空间或强 invariant 做生成式验证 | property、seed、最小失败样例 |
| Integration / contract | 覆盖数据库、文件系统、队列、网络、Schema、进程或多模块边界 | 集成/契约测试 |
| Mutation / test-strength | 验证测试能否杀死高风险逻辑中的有意义错误 | surviving/killed mutation 与处置 |
| Regression | 覆盖受影响模块和已知缺陷复发风险 | affected suite 或 targeted regression |
| Browser / E2E | 仅验证真实用户可见关键流程 | 页面状态、URL、截图、控制台/请求或 trace |
| Isolation / flaky | 验证时间、并发、共享状态或随机性不会产生不可解释不稳定 | deterministic rerun/seed/state evidence |

优先使用能可靠证明行为的最低成本层，不把全量回归或浏览器 E2E 当作所有变更的默认反馈循环。

## 风险分支

- 微小变更：运行最接近的现有检查；只有行为容易复发时才补回归测试。
- 普通行为变更：先定义契约和 focused tests，再运行受影响的回归检查。
- 复杂或高风险行为：实际可行时采用 RED -> GREEN，先确认测试能捕获缺失行为，再实施最小修复。
- 浏览器可见行为：低层检查通过后，再使用最小真实用户流程补充浏览器验证。

## Test Quality Gate

最终 PASS 同时要求：所有 acceptance criteria 有执行证据；所有 mandatory
dimensions 已通过或有具体 N/A 理由；不存在通过 retry 被掩盖的 unexplained
flaky；没有为了 GREEN 而弱化断言；coverage 只作诊断，不作为质量证明。

Property/fuzz 先定义 invariant/oracle，再生成输入；发现失败后应固化最小 seed
为 deterministic regression。Mutation testing 优先针对 changed/high-risk module，
surviving meaningful mutation 需要补强 assertion/case 或说明等价 mutation，
不追求仓库统一 mutation score。

## 失败处理

失败先分类，再决定是否修改：实现缺陷修产品代码，测试缺陷修测试，回归问题修复或停止，环境/数据不可用则标记阻塞，需求或设计冲突则重新规划；同一提交和状态出现无法解释的 FAIL -> PASS 时标记 flaky，不能因重跑成功改成 PASS。修复应保持范围最小，并重新运行原失败点和受影响检查；不得通过放宽断言、删除测试、盲目重试或固定等待制造通过。

## Browser / E2E 分支

Browser / E2E 是条件式验证分支，只在低层检查无法充分证明用户可见行为，
或验收标准明确要求真实端到端流程时启用。优先复用目标项目已有的
Playwright、Selenium 或 Cypress 配置；没有现成 harness 时，才考虑使用真实
Chromium。浏览器检查必须从已知 URL、会话和安全测试数据开始，使用稳定的
role、label、accessible name 或 test ID，并记录实际页面状态和必要证据。

浏览器验证不替代单元、组件、API、集成或回归检查；不可用的浏览器、服务、
账号或测试数据应标记为 `blocked`，不能用源码、静态 HTML 或截图冒充通过。

## 维护边界

测试报告只记录实际执行的操作和证据。页面地址、账号、Cookie、Token、个人信息和真实业务数据使用占位符；公开图源和文档不应包含凭据或内部业务信息。
