from app.schemas.analysis import DimensionScore, ResumeAnalysis
from app.schemas.resume import ParsedResume


class ResumeScorer:
    def score(self, parsed: ParsedResume) -> ResumeAnalysis:
        scores = [
            DimensionScore(name="信息完整度", score=85, reason="具备教育和技能基础信息"),
            DimensionScore(name="内容表达清晰度", score=75, reason="表达基本清楚，但仍偏笼统"),
            DimensionScore(name="项目与经历质量", score=74, reason="有项目，但贡献描述较弱"),
            DimensionScore(name="成果量化程度", score=60, reason="缺少结果数据"),
            DimensionScore(name="整体可读性", score=80, reason="结构基础可读"),
        ]
        overall_score = sum(item.score for item in scores) // len(scores)

        if overall_score >= 85:
            summary = "可直接投递"
        elif overall_score >= 70:
            summary = "建议修改后投递"
        else:
            summary = "不建议直接投递"

        return ResumeAnalysis(
            overall_score=overall_score,
            summary=summary,
            dimension_scores=scores,
        )
