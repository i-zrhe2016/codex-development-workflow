# RTK 操作规则

RTK 是本 Skill 的必用 shell 执行入口，不是可选优化，也不替代任务本身的授权、测试和发布门禁。使用显式命令，不依赖自动改写 hook。

## 选择输出形式

| 目的 | 执行方式 |
|---|---|
| Git 状态、历史、差异概览 | `rtk git status`、`rtk git log -n 5`、`rtk git diff` |
| 定位文件、精确搜索结果 | `rtk proxy rg --files`、`rtk proxy rg -n PATTERN PATH` |
| 完整读取 Skill、指令或指定文件 | `rtk proxy cat PATH`；不得使用会省略内容的 smart/read 摘要 |
| 机器消费 JSON、porcelain、精确计数 | `rtk proxy` 包装原始命令，保持输出契约 |
| 测试、构建、脱敏、review | `rtk proxy` 包装现有命令；保留完整日志和真实退出码 |
| Commit / Push / PR / Merge | `rtk proxy` 包装既有守卫脚本或已获授权的命令，先满足发布 Skill |
| 其他命令或压缩结果不充分 | `rtk proxy <original-command> ...` |

- 先查已安装版本的子命令帮助，不把任意 shell 命令机械替换成不存在的 RTK 子命令。
- RTK 摘要只用于导航；完整差异、安全判断、验收和用户要求的逐字输出必须查原始证据。
- 已执行的有副作用命令不得因摘要不足而重复执行；先读取已保存日志、查询状态。
- shell 管道或条件组合需要时用 `rtk proxy bash -o pipefail -c '...'` 包装整体，保持正确引用及原始失败状态；不要把摘要输出交给依赖原格式的解析器。
- 不把 `codex review` 再包进通用摘要器；使用 `rtk proxy python3 <github-push-when-ready-dir>/scripts/run_review.py --base <actual-base>`，由发布 Skill 的既有 runner 保存审查证据。
- 压缩不是脱敏。RTK 的命令统计和恢复记录可能包含敏感参数或输出；不得把 token、凭据放进命令参数，也不把本地 RTK 数据或日志提交到仓库。
- 不自行运行 `rtk init -g`、改写全局 hooks 或关闭测试；只有任务明确需要这些配置时才处理。

## 依赖与验证

缺少 RTK 时可用裸命令完成引导检查、可信安装和修复；之后必须回到 RTK。使用 rtk-ai/rtk 官方发布资产并核对同版本校验和，避免安装同名的其他项目。安装不可行时报告缺失项并停止依赖 shell 的工作，不静默绕过。

验证至少覆盖：版本/帮助可用、一个只读摘要命令、proxy 原样 stdout/stderr、失败退出码保留。测试在临时目录中进行，不为统计节省量重跑构建或有副作用操作。

`rtk gain` 仅在评估效果时读取，不必每轮调用。其统计是命令输出压缩估算，不代表总上下文或账单等比例降低。

来源：[RTK 官方仓库及命令说明](https://github.com/rtk-ai/rtk)。本次集成在 Linux 上验证版本 0.48.0；其他版本以本机帮助与验证结果为准。
