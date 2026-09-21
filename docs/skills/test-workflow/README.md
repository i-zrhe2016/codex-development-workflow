# Test Workflow

本目录迁移并维护 `test-workflow` specialist 的文档。运行时 skill 源码位于
[`skills/test-workflow/`](../../../skills/test-workflow/)；它服务于本仓库的
主 Agent / Slice workflow；它负责验证委派或主线程执行的 Slice，但不负责
决定是否拆分 Agent 或如何并行实现。

核心入口是 `test-workflow`：先建立 Acceptance-to-Test Matrix，再从变更风险
选择 mandatory test dimensions，并按 `静态检查 -> focused -> boundary/negative
-> property/fuzz -> integration/contract -> mutation -> regression -> browser/E2E
-> isolation/flaky` 的成本梯度执行。复杂或高风险行为采用 RED -> GREEN；
最终是否 PASS 由 Test Quality Gate 决定，而不是仅由某个 test level 变绿决定。

![test-workflow 通用测试验证梯度](diagrams/test-workflow-flow.svg)

图源：[test-workflow-flow.puml](diagrams/test-workflow-flow.puml)。规范产物使用
[SVG](diagrams/test-workflow-flow.svg)；已有 PNG 仅作为兼容产物保留，不作为
文档主引用。该图按 `plantuml-skill` 的 safe-subset、render validation 和
readability self-check 规则维护。

## Managed skill

| Skill | 用途 | 运行时入口 |
|---|---|---|
| `test-workflow` | 通用单元、组件、API、集成、回归和条件式浏览器验证 | [`skills/test-workflow/SKILL.md`](../../../skills/test-workflow/SKILL.md) |

## 文档索引

- [通用测试工作流架构](architecture.md)：测试梯度、职责边界、风险分支和失败处理。
- [通用测试工作流运行手册](usage.md)：模式选择、验收清单、执行顺序和报告格式。

## 验证级别

| Level | 用途 |
|---|---|
| `minimal` | 微小、文档、配置、样式、依赖、typo 或简单重构。 |
| `focused` | 默认；直接覆盖当前 Slice 验收标准的最小检查。 |
| `regression` | 缺陷修复、跨模块变更或已有回归风险。 |
| `full` | 高风险、发布门禁或明确要求完整套件。 |

Level 只控制验证广度，不直接决定 PASS。只有所有 mandatory risk dimensions
已满足，或以具体理由标记 N/A，Test Quality Gate 才能关闭；需要扩大 suite
时仍按风险和证据逐级升级。

## 推荐执行顺序

```text
Requirement / Slice
        |
        v
Acceptance + Test Cases
        |
        v
Acceptance-to-Test Matrix
        |
        v
Static / Type / Lint
        |
        v
Focused automated tests
        |
        +-- complex/high-risk --> RED -> Implement -> GREEN
        |
        v
Boundary / Negative
        |
        +-- complex inputs/invariants --> Property / Fuzz
        |
        v
Integration / Contract
        |
        +-- high-risk/weak-test suspicion --> Mutation
        |
        v
Affected Regression
        |
        +-- browser-visible critical flow --> Browser / E2E
        |
        v
Isolation / Flaky check
        |
        v
Test Quality Gate
```

原则：使用能可靠证明行为的最低成本测试层，不把浏览器 E2E 当默认反馈循环，也不为了 GREEN 放宽断言、增加盲目 retry 或固定 sleep。

## 维护约定

- 优先复用项目已有测试框架、fixture、helper 和命令。
- 每个 Slice 的内循环保持 focused；多个 Slice 完成后再运行必要的集成/回归测试。
- Coverage 只作为诊断信号，不能替代 assertion quality 或 acceptance evidence。
- Retry 只能用于诊断；同一提交出现 FAIL -> PASS 且无已验证外因时必须标记 flaky。
- Property/fuzz、mutation 和 Browser/E2E 按风险启用，不做所有变更的固定成本。
- 浏览器验证只用于真实用户交互或明确要求的 E2E 行为。
- 文档中的页面地址、账号、Cookie、Token 和测试数据使用占位符，不写入真实值。
