from app.schemas.analysis import RewriteSuggestion
from app.schemas.resume import ResumeSection


def build_project_suggestion(section: ResumeSection) -> RewriteSuggestion:
    return RewriteSuggestion(
        section_title=section.title,
        original_problem="描述只有职责，没有体现结果和难点",
        rewrite_direction="补充业务背景、技术方案和量化结果",
        example="基于 Spring Boot 完成核心接口开发，优化分页查询逻辑，接口平均响应时间降至 120 ms。",
    )
