from app.schemas.analysis import ResumeAnalysis
from app.schemas.resume import ParsedResume
from app.services.rewrite_guidance import build_project_suggestion
from app.services.scoring import ResumeScorer


class DiagnosisEngine:
    def analyze(self, parsed: ParsedResume) -> ResumeAnalysis:
        analysis = ResumeScorer().score(parsed)

        if parsed.projects:
            analysis.top_issues.append("项目描述偏职责罗列，缺少结果证明")
            analysis.risk_flags.append("项目经历技术名词较多，但看不出场景复杂度")
            analysis.rewrite_suggestions.append(build_project_suggestion(parsed.projects[0]))

        if parsed.skills and len(parsed.skills.content.split()) >= 5:
            analysis.top_issues.append("技能清单偏堆砌，缺少掌握深度证明")

        analysis.strengths.append("至少具备项目和技能基础信息")
        analysis.weaknesses.append("成果量化和个人贡献表达偏弱")
        return analysis
