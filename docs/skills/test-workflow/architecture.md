# 通用测试工作流架构

> Type: Architecture
> Status: Active
> Scope: Structure of the test-workflow specialist: verification levels and gradient, risk branches, Test Quality Gate, failure handling, and the browser/E2E branch

## 目标

`test-workflow` 面向后端、前端、API、库和 CLI 等仓库变更，从需求、Slice 功能
清单、验收标准和现有契约中提炼最小高价值测试集，并按成本从低到高逐层
验证。浏览器验证只在行为对用户可见或验收明确要求端到端流程时启用。
公共边界（API、CLI、UI、文件/Schema、进程、服务或公开库接口）上的成功、
失败和异常路径共享同一调用方可消费契约；失败证据必须覆盖错误/状态/异常的
格式、结构、语义和可操作性，而不只是证明失败发生。
涉及身份、session、权限、租户或受保护操作时，AuthN/AuthZ 是显式 mandatory
dimension：authentication 证明调用方是谁以及 session lifecycle、cookie/token
是否正确；authorization 证明该身份能做什么，覆盖权限、tenant/object ownership、
fail-closed，并断言 denied operation 没有 protected side effect。
Assertion strength 也是门禁的一部分：测试必须能因其声称防护的缺陷而失败；
mock-called、value-exists、no-exception 或 status-only 断言只有在它们本身就是完整契约时才足够。
当行为依赖传输或部署边界时，真实入口也是契约的一部分：协议、域名、端口、
路径前缀、反代、TLS、redirect、cache、header、cookie、token、CORS 和
浏览器安全策略都可能改变调用方实际结果。

![test-workflow 风险驱动验证与 Test Quality Gate](diagrams/test-workflow-flow.svg)

Source: [`diagrams/test-workflow-flow.puml`](diagrams/test-workflow-flow.puml)

独立验收由每个 Ticket（含文档、配置、测试）的全新 verifier 执行全部
scenario；实现阶段的 RED/GREEN 与本地反馈仍由该 Ticket 的实现 worker 执行。verifier 只读仓库
（允许缓存与临时证据），失败交还实现职责修复，再由新 verifier 重验受影响
功能并保留先前失败。主代理拥有最终门禁；详见
[调度政策](../../../AGENTS.md#multi-agent-delegation)。

## 核心数据流

1. 从需求、Slice 验收标准和本次实际改动中确定行为契约，包含成功、失败和异常路径。
2. 建立 Acceptance-to-Test Matrix，把每条验收标准映射到实际执行证据。
3. 根据风险选择 mandatory dimensions：happy path、boundary、negative、AuthN/AuthZ、state/invariant、integration/contract、real entrypoint/config、regression，以及按需的 property/fuzz、mutation、browser/E2E、isolation/flaky。
4. 从静态检查和 focused tests 开始，按成本逐级执行适用维度。
5. 每个验收点和 mandatory dimension 都必须有 PASS 证据，或明确的 N/A 理由；未执行不能冒充通过，失败路径也不能只以状态/异常出现作为通过。
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
| Boundary / negative | 验证边界值、无效输入、失败路径和状态转换 | 明确输入、预期错误/状态/异常的格式、结构、语义和调用方可操作性断言 |
| AuthN / AuthZ | 分开验证身份/session/token 与权限/ownership/tenant 边界 | 身份、session lifecycle、cookie/token、permission、tenant/object ownership、fail-closed、protected side-effect absence |
| Property / fuzz | 对复杂输入空间或强 invariant 做生成式验证 | property、seed、最小失败样例 |
| Integration / contract | 覆盖数据库、文件系统、队列、网络、Schema、进程或多模块边界 | 成功与失败/异常契约的集成/契约测试 |
| Real entrypoint / config | 覆盖生产同类入口、传输边界和关键配置组合 | URL、协议、反代、TLS、路径前缀、header/cookie/token、缓存和配置矩阵证据 |
| Mutation / test-strength | 验证测试能否杀死高风险逻辑中的有意义错误 | surviving/killed mutation 与处置 |
| Regression | 覆盖受影响模块和已知缺陷复发风险 | affected suite 或 targeted regression |
| Browser / E2E | 验证真实用户可见关键流程和浏览器强制策略 | 页面状态、URL、cookie/CORS/mixed-content/cache 结果、控制台/请求或 trace |
| Isolation / flaky | 验证时间、并发、共享状态或随机性不会产生不可解释不稳定 | deterministic rerun/seed/state evidence |

优先使用能可靠证明行为的最低成本层，不把全量回归或浏览器 E2E 当作所有变更的默认反馈循环。

## 风险分支

- 微小变更：运行最接近的现有检查；只有行为容易复发时才补回归测试。
- 普通行为变更：先定义契约和 focused tests，再运行受影响的回归检查。
- 复杂或高风险行为：实际可行时采用 RED -> GREEN，先确认测试能捕获缺失行为，再实施最小修复。
- 真实入口或配置敏感行为：用生产同类配置组合和真实入口执行最小 smoke/matrix checks。
- 浏览器可见或浏览器策略敏感行为：低层检查通过后，再使用最小真实用户流程补充浏览器验证。

## Test Quality Gate

最终 PASS 同时要求：所有 acceptance criteria 有执行证据；所有 mandatory
dimensions 已通过或有具体 N/A 理由；公共边界的成功、失败和异常路径均按
调用方可消费契约验证；authentication 与 authorization 已分开证明或说明 N/A；
测试可因防护缺陷而失败；不存在通过 retry 被掩盖的 unexplained flaky；没有为了
GREEN 而弱化断言；coverage 只作诊断，不作为质量证明。发生失败但未按契约
表达给调用方时，Test Quality Gate 必须保持 fail/partial/blocked，不能 PASS。

Property/fuzz 先定义 invariant/oracle，再生成输入；发现失败后应固化最小 seed
为 deterministic regression。Mutation testing 优先针对 changed/high-risk module，
surviving meaningful mutation 需要补强 assertion/case 或说明等价 mutation，
不追求仓库统一 mutation score。

## 失败处理

失败先分类，由实现职责处理修改，独立 verifier 不代修代码或测试：实现缺陷修产品代码，测试缺陷修测试，回归问题修复或停止，环境/数据不可用则标记阻塞，需求或设计冲突则重新规划；同一提交和状态出现无法解释的 FAIL -> PASS 时标记 flaky，不能因重跑成功改成 PASS。修复应保持范围最小，并重新运行原失败点和受影响检查；不得通过放宽断言、删除测试、盲目重试或固定等待制造通过。

## Browser / E2E 分支

Browser / E2E 是条件式验证分支，只在低层检查无法充分证明用户可见行为、
浏览器强制策略或验收标准明确要求真实端到端流程时启用。优先复用目标项目
已有的 Playwright、Selenium 或 Cypress 配置；没有现成 harness 时，才考虑
使用真实 Chromium。浏览器检查必须从真实入口或生产同类 URL、会话和安全
测试数据开始，使用稳定的 role、label、accessible name 或 test ID，并记录
实际页面状态和必要证据。

涉及 cookie、CSRF、CORS、mixed content、redirect 或缓存时，验证最短闭环：
加载页面、保留 cookie、提取运行时 token、提交请求、断言最终页面或网络结果。
只证明组件点击、服务端接口可调用、token 生成或 cookie 存在，不足以证明真实
浏览器路径可用。

浏览器验证不替代单元、组件、API、集成或回归检查；不可用的浏览器、服务、
账号或测试数据应标记为 `blocked`，不能用源码、静态 HTML 或截图冒充通过。

## 维护边界

测试报告只记录实际执行的操作和证据。页面地址、账号、Cookie、Token、个人信息和真实业务数据使用占位符；公开图源和文档不应包含凭据或内部业务信息。
