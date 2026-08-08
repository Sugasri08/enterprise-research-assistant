"""
Module 6 — Structured Output.
Every generated report is forced through this schema so downstream
export (TXT/PDF/email) can rely on a fixed shape regardless of topic.
"""
from pydantic import BaseModel, Field


class Report(BaseModel):
    title: str = Field(description="Concise report title")
    executive_summary: str = Field(description="2-4 sentence high-level summary")
    key_findings: list[str] = Field(description="Bullet list of the most important findings")
    strengths: list[str] = Field(description="Bullet list of strengths identified")
    weaknesses: list[str] = Field(description="Bullet list of weaknesses or risks identified")
    future_opportunities: list[str] = Field(description="Bullet list of forward-looking opportunities")
    conclusion: str = Field(description="Closing synthesis, 2-4 sentences")
    references: list[str] = Field(description="Sources used: URLs, Wikipedia pages, or uploaded file names")

    def to_markdown(self) -> str:
        def bullets(items: list[str]) -> str:
            return "\n".join(f"- {i}" for i in items) if items else "- None noted"

        return f"""# {self.title}

## Executive Summary
{self.executive_summary}

## Key Findings
{bullets(self.key_findings)}

## Strengths
{bullets(self.strengths)}

## Weaknesses
{bullets(self.weaknesses)}

## Future Opportunities
{bullets(self.future_opportunities)}

## Conclusion
{self.conclusion}

## References
{bullets(self.references)}
"""
