# 通用测试工作流运行手册

## 适用范围

适用于后端、前端、API、库、CLI 以及其他仓库级功能变更、缺陷修复、重构和
Slice 验收。目标是用最低成本的可靠检查证明验收标准，而不是追求无差别的
全量测试。

## 验收清单

在执行前先从需求和现有契约提炼简短清单：

```text
行为 / 契约
- 主要成功路径
- 直接相关的边界或失败路径
- 可能的回归风险

证据
- 静态、类型、Lint 或配置检查（如适用）
- 覆盖变更契约的 focused test
- 跨模块边界时的集成检查
- 仅在用户可见交互改变时执行 Browser / E2E
```

先建立 Acceptance-to-Test Matrix，再选择最小但完整的高价值测试集。不要把固定
case 数当成 completeness；优先覆盖契约、边界、状态转换、失败处理和实际风险。

## 验证级别

| Level | 执行边界 |
|---|---|
| `minimal` | 微小、文档、配置、样式、依赖、typo 或简单重构。 |
| `focused` | 默认；覆盖当前 Slice 验收标准的最小检查。 |
| `regression` | 缺陷修复、跨模块变更或已有回归风险。 |
| `full` | 高风险、发布门禁或明确要求完整套件。 |

Level 只控制广度。只有 Acceptance-to-Test Matrix 和所有 mandatory risk
dimensions 都满足（或有具体 N/A 理由）后才停止。

## 模式选择

| 变更类型 | 执行方式 |
|---|---|
| 微小变更 | 运行最接近的现有检查；行为回归风险明确时补测试 |
| 普通行为变更 | 定义或更新 focused tests，随后运行相关回归检查 |
| 复杂 / 高风险行为 | 实际可行时使用 RED -> GREEN，再运行集成/回归检查 |
| 浏览器可见行为 | 完成低层检查后，补充最小真实用户流程 |

## 标准执行顺序

1. 建立 Acceptance-to-Test Matrix，并根据风险选择 mandatory dimensions。
2. 运行编译、类型、Lint、Schema 或配置等静态检查。
3. 运行覆盖变更契约的最小 focused tests。
4. 补齐适用的 boundary 和 negative-path checks。
5. 复杂输入空间或强 invariant 场景运行 property/fuzz；失败 seed 固化为回归测试。
6. 触及数据库、文件系统、队列、网络、Schema、进程或多模块边界时运行 integration/contract checks。
7. 高风险逻辑或怀疑测试过弱时，对 changed/high-risk module 做 targeted mutation/test-strength check。
8. 运行受影响模块回归；只有范围/风险确实要求时才运行 full suite。
9. 浏览器可见关键流程且低层无法证明时执行 Browser / E2E。
10. 涉及并发、时间、共享状态、随机性或出现间歇失败时执行 isolation/flaky diagnosis；重跑成功不能抹掉先前失败。
11. 用 Test Quality Gate 汇总；只有所有 mandatory dimensions 满足才 PASS。

不要用固定 sleep、盲目 retry、弱化断言或删除测试来取得通过。出现第一个有用失败时先诊断根因，再决定是否扩大检查范围。

## RED -> GREEN

复杂或高风险变更按以下顺序执行：

1. 将验收标准转成 focused test。
2. 运行并确认测试因预期缺失行为而失败；若已通过，不人为制造失败。
3. 实施满足契约的最小改动。
4. 重跑原测试和直接相关检查，确认 GREEN。
5. 运行必要的集成/回归检查。

## 失败分类

| 类型 | 处理 |
|---|---|
| 实现缺陷 | 修改最小相关产品代码，并重跑失败检查 |
| 测试缺陷 | 修正断言、fixture、定位器或测试设置，不修改正确的产品行为 |
| 回归 | 修复受影响行为；若超出范围则停止并报告 |
| 环境 / 数据失败 | 标记 `blocked`，说明缺失的依赖、服务、权限或数据 |
| Flaky / isolation | 标记 flaky/blocked，定位时间、随机性、共享状态、并发或外部依赖；retry 不得变成 PASS |
| 需求 / 设计冲突 | 停止扩展补丁，重新确认预期或规划 |

## Browser / E2E 分支

浏览器验证只证明低层检查无法充分覆盖的用户可见行为。测试应从已知 URL、会话和数据状态开始，优先使用 role、label、accessible name 或稳定 test ID，等待目标状态而不是固定时间，并在失败时保留 URL、页面状态和必要的截图、控制台、请求或 trace 证据。

不对生产环境执行未授权的写入、删除、支付或消息发送操作。CLI、浏览器、服务、账号或测试数据不可用时如实标记 `blocked`，不能用源码、静态 HTML、`curl` 或截图代替真实浏览器通过。

## 报告模板

```markdown
## Test Report

- Scope: <Slice/feature>
- Mode: tiny / normal / RED-GREEN / browser
- Level: minimal / focused / regression / full
- Result: pass / partial / fail / blocked

### Acceptance-to-Test Matrix

| Acceptance criterion | Risk | Required dimension | Evidence | Result |
|---|---|---|---|---|
| ... | ... | ... | command/test/observed behavior | pass/fail/blocked |

### Test Quality Gate

| Dimension | Result | Evidence / N/A reason |
|---|---|---|
| Acceptance coverage | pass/fail | ... |
| Boundary coverage | pass/fail/N/A | ... |
| Negative-path coverage | pass/fail/N/A | ... |
| Regression protection | pass/fail/N/A | ... |
| Integration/contract | pass/fail/N/A | ... |
| Property/fuzz | pass/fail/N/A | ... |
| Mutation/test-strength | pass/fail/N/A | ... |
| Browser/E2E | pass/fail/N/A | ... |
| Flaky/isolation | pass/fail/N/A | ... |

### Failures

- <root cause, relevant evidence, and next action>
```

只报告实际执行过的检查。所有验收标准和 mandatory dimensions 都应有对应证据；
不适用必须给出 N/A 理由。Coverage 是 diagnostic signal，不是 PASS 条件；retry
不能把 unexplained flaky failure 改写为成功。
