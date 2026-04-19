# 简历 Markdown 解析链路设计文档

## 1. 背景

当前简历诊断助手的 PDF 解析链路较为简单：

- 使用 `pdfplumber` 提取纯文本
- 直接基于纯文本做模块分块和后续分析

这条链路已经打通 MVP，但存在两个明显问题：

1. PDF 提取结果偏原始，格式信息损失较多，不利于后续解析。
2. 简历内容进入分块器前没有经过结构化整理，导致项目、技能等模块的识别稳定性较弱。

用户已经明确提出两个改进方向：

1. 上传 PDF 后，先将文件解析成 Markdown 文本，提取方式参考 [test.py](/Users/liheng/project/python/codex-begin-class/test.py)。
2. 在得到提取文本后，调用一个小模型将其进一步整理成更规范的 Markdown 文本。

本次设计聚焦于在现有 MVP 上新增一条更稳定的「PDF -> Markdown -> 规范化 Markdown -> 分析」链路。

## 2. 目标

本次改动的目标是：

1. 用 `MarkItDown` 替换当前 `pdfplumber` 纯文本提取方案。
2. 复用 [test.py](/Users/liheng/project/python/codex-begin-class/test.py) 中的清洗逻辑，生成质量更高的原始 Markdown。
3. 接入 ModelScope 小模型，对原始 Markdown 做二次整理。
4. 当未配置 `MODELSCOPE_API_KEY` 或模型调用失败时，自动降级为原始 Markdown，保证主流程不中断。
5. 将最终整理后的 Markdown 作为后续分析输入。
6. 在结果页展示 Markdown 相关结果，便于人工检查解析质量。

## 3. 非目标

本次设计明确不做以下内容：

- 不改造评分规则本身
- 不引入岗位匹配评分
- 不展示模型推理过程（thinking/reasoning）
- 不把 API Key 写死到代码库
- 不对 Markdown 做复杂 AST 级解析
- 不重构整套结果页布局

## 4. 用户已确认的关键约束

- 采用 `B` 方案，即标准两阶段解析。
- 小模型调用的密钥通过环境变量接入。
- 如果未配置 `MODELSCOPE_API_KEY`，系统自动降级，不报错中断。
- 如果模型调用失败，也自动降级，不报错中断。
- 整理后的 Markdown 既用于后续分析，也要在页面上展示。

## 5. 方案对比与结论

### 5.1 方案 A：最小接入

- 用 `MarkItDown` 替换 `pdfplumber`
- 增加一层模型整理
- 直接把结果塞回现有链路

优点：

- 改动最小
- 开发速度最快

缺点：

- 原始提取、整理结果、最终分析输入耦合在一起
- 后续调试和扩展成本较高

### 5.2 方案 B：标准两阶段解析

- 独立原始 Markdown 提取服务
- 独立 Markdown 规范化服务
- 独立解析编排层负责降级和结果整合
- 页面展示原始 Markdown、最终 Markdown 和降级状态

优点：

- 结构清楚
- 降级策略好维护
- 后续更换模型或调整提示词更容易

缺点：

- 比方案 A 多一层服务编排

### 5.3 方案 C：重型增强版

- 在 B 的基础上继续重构 Markdown 分块器
- 页面增加更多调试信息

优点：

- 一次性能力更强

缺点：

- 超出当前两项小需求的范围
- 容易把迭代做大

### 5.4 结论

本次采用 `方案 B`。

原因是它在实现成本、可维护性和后续扩展性之间平衡最好，且完全符合用户已经确认的范围。

## 6. 设计概览

新的处理链路调整为：

1. 用户上传 PDF
2. 系统使用 `MarkItDown` 将 PDF 转为原始 Markdown
3. 系统对原始 Markdown 执行清洗逻辑
4. 系统尝试调用 ModelScope 小模型，将原始 Markdown 整理成更规范的 Markdown
5. 如果模型未配置或调用失败，则直接使用原始 Markdown 作为最终 Markdown
6. 分块器基于最终 Markdown 继续做解析
7. 诊断和评分链路保持不变
8. 结果页展示：
   - 原始提取 Markdown
   - 最终整理 Markdown
   - 当前是否使用降级结果

## 7. 架构设计

### 7.1 原始 Markdown 提取服务

新增一个 PDF -> Markdown 的提取服务，职责包括：

- 调用 `MarkItDown` 处理 PDF 文件
- 复用 [test.py](/Users/liheng/project/python/codex-begin-class/test.py) 中的文本清洗逻辑
- 输出清洗后的原始 Markdown

该服务将替代现有 `pdfplumber` 纯文本提取逻辑。

### 7.2 Markdown 规范化服务

新增一个 Markdown 规范化服务，职责包括：

- 读取环境变量 `MODELSCOPE_API_KEY`
- 构造 ModelScope OpenAI 兼容客户端
- 将原始 Markdown 作为用户输入发送给模型
- 获取模型输出的整理后 Markdown

模型调用要求：

- `base_url` 使用 ModelScope OpenAI 兼容地址
- 模型 ID 使用用户给定的 `deepseek-ai/DeepSeek-V3.2`
- 默认允许开启 `enable_thinking`
- 代码中只消费最终 `content`，不在结果页展示推理内容

### 7.3 解析编排层

新增一个统一编排层，负责串联两阶段解析，并输出统一结果。

建议输出结构至少包含：

- `raw_markdown`
- `normalized_markdown`
- `used_fallback`
- `fallback_reason`

其中：

- `raw_markdown` 表示 `MarkItDown + 清洗逻辑` 的结果
- `normalized_markdown` 表示最终用于后续分析的 Markdown
- `used_fallback` 表示是否发生了降级
- `fallback_reason` 用于说明降级原因，例如：
  - `missing_api_key`
  - `llm_request_failed`
  - `llm_empty_response`

### 7.4 分块器输入调整

当前 `ResumeSectionParser` 直接消费纯文本。

本次调整后，它将消费最终 Markdown 文本。

第一版不强制将分块器重写为完整 Markdown 语义解析器，但至少要保证：

- 现有基于文本扫描的逻辑仍然可继续工作
- 后续如果 Markdown 更结构化，分块器可以逐步演进

### 7.5 页面展示调整

结果页增加一个新的 Markdown 展示区，建议包含：

- 原始提取 Markdown
- 最终整理 Markdown
- 当前是否启用降级

展示目的不是面向所有最终用户，而是当前阶段便于产品和开发人工审核解析质量。

## 8. 降级策略

### 8.1 未配置 API Key

当环境变量 `MODELSCOPE_API_KEY` 不存在时：

- 不抛错
- 不中断分析流程
- 直接使用原始 Markdown 作为最终 Markdown
- `used_fallback = true`
- `fallback_reason = "missing_api_key"`

### 8.2 模型请求失败

当模型请求超时、网络失败、返回异常或服务端报错时：

- 不抛错中断用户流程
- 直接回退到原始 Markdown
- `used_fallback = true`
- `fallback_reason = "llm_request_failed"`

### 8.3 模型返回空结果

当模型成功返回，但最终 `content` 为空或只有空白时：

- 视为无效响应
- 自动回退到原始 Markdown
- `used_fallback = true`
- `fallback_reason = "llm_empty_response"`

## 9. 提示词策略

本次设计不要求先构建复杂提示词系统，但至少应明确模型任务：

- 输入是一份从 PDF 提取得到的原始 Markdown
- 目标是将其整理为结构更清楚、更适合后续规则分析的 Markdown
- 不要补充用户原文中不存在的信息
- 不要杜撰项目或经历内容
- 优先保留原始内容，只整理结构、换行、标题和列表格式

第一版提示词以稳定输出为目标，不追求复杂行为控制。

## 10. 数据流变化

### 10.1 当前数据流

当前链路：

`PDF -> pdfplumber 纯文本 -> 分块 -> 评分/诊断 -> 页面展示`

### 10.2 改造后数据流

改造后链路：

`PDF -> MarkItDown 原始 Markdown -> LLM 规范化 Markdown -> 分块 -> 评分/诊断 -> 页面展示`

同时增加调试展示数据：

`raw_markdown` 和 `normalized_markdown`

## 11. 错误处理要求

本次设计要求保留现有「不要静默失败」原则，但对模型相关阶段采用「可降级、不阻断」策略。

处理原则如下：

- PDF 本身无法解析：仍然返回 `400`
- `MarkItDown` 失败：返回 `400`
- 小模型阶段失败：不返回 `400`，而是降级继续

换句话说：

- PDF 提取阶段是硬失败
- Markdown 规范化阶段是软失败

## 12. 对现有代码的影响

预计会影响以下模块：

- `app/services/pdf_text_extractor.py`
  - 需要替换或重构为基于 `MarkItDown` 的提取实现
- `app/routes/web.py`
  - 需要接入新的解析编排层，并把 Markdown 结果传给模板
- `app/templates/result.html`
  - 需要增加 Markdown 展示区和降级状态展示
- `app/services/resume_section_parser.py`
  - 输入改为最终 Markdown 文本
- `pyproject.toml`
  - 需要增加 `markitdown` 和模型调用相关依赖

预计会新增以下模块：

- 原始 Markdown 提取服务
- Markdown 规范化服务
- 解析编排服务

## 13. 验收标准

当以下条件全部满足时，本次改动可视为完成：

1. 上传 PDF 后，系统能够先生成原始 Markdown。
2. 当环境变量存在时，系统会尝试调用小模型整理 Markdown。
3. 当环境变量缺失时，系统自动降级但流程继续。
4. 当模型调用失败时，系统自动降级但流程继续。
5. 结果页能展示原始 Markdown、最终 Markdown 和降级状态。
6. 后续评分与诊断链路仍然可以正常工作。
7. 新增测试覆盖正常路径和降级路径。

## 14. 当前结论

本次改动采用 `方案 B`：

- 引入 `MarkItDown` 生成原始 Markdown
- 引入小模型生成规范化 Markdown
- 用统一编排层管理模型调用与自动降级
- 将最终 Markdown 同时用于分析和页面展示

该方案能够在不显著扩大范围的前提下，提升 PDF 解析质量，并为后续更稳定的简历结构识别打下基础。
