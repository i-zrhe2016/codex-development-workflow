# 权威资料速查

Reddit 用来发现真实踩坑；下列资料用于定义术语、风险和工具行为。若它们与社区经验冲突，以组织政策、合同和适用法律为准。

| 资料 | 使用时机 | 要点 |
|---|---|---|
| [NIST SP 800-188](https://www.nist.gov/publications/de-identifying-government-datasets-techniques-and-governance) | 公开数据、研究数据、合成数据或准标识符风险评估 | 先明确用途、发布模型和重识别风险；删除标识符、变换准标识符、合成数据和受控查询都是不同方案；“遮住字段”本身不是充分证明 |
| [ICO Anonymisation guidance](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/data-sharing/anonymisation/) | 需要区分匿名化与伪名化时 | 评估可识别性、外部辅助信息和攻击者能力；有映射/密钥的伪名化仍需按个人数据治理 |
| [Adobe: Sanitize PDFs](https://helpx.adobe.com/acrobat/desktop/protect-documents/redact-pdfs/sanitize.html) | PDF 对外发布 | PDF 可能含元数据、批注、隐藏层等；真正的可见内容删除与隐藏信息清理是两件事 |
| [Microsoft Presidio](https://microsoft.github.io/presidio/) | 文本/日志/结构化字段批量检测 | 用 analyzer + anonymizer 做规则或 NER 基线；仍需补充领域词典、低置信度人工复核和格式/关系校验 |
| [PyMuPDF redaction API](https://pymupdf.readthedocs.io/en/latest/recipes-annotations.html) | 本地自动化 PDF | 使用 redaction annotation 后执行 apply；普通绘图/批注不能替代应用删除和后续复核 |

这些链接描述的是方法和工具行为，不构成合规认证，也不保证对所有语言、格式或攻击者都安全。
