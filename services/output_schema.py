from typing import Dict, List

from pydantic import BaseModel, Field, HttpUrl


class RankingFactors(BaseModel):
    relevance: float = Field(ge=0.0, le=100.0)
    educational_quality: float = Field(ge=0.0, le=100.0)
    credibility: float = Field(ge=0.0, le=100.0)
    learning_effectiveness: float = Field(ge=0.0, le=100.0)


class RecommendedResource(BaseModel):
    title: str = Field(min_length=1)
    type: str = Field(min_length=1)
    qualityScore: float = Field(ge=0.0, le=100.0)
    difficulty: str = Field(min_length=1)
    category: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    url: HttpUrl

    rankingFactors: RankingFactors | None = None
    rankingExplanation: str | None = None


class FinalOutput(BaseModel):
    topic: str = Field(min_length=1)
    recommendedResources: List[RecommendedResource]
    learningSequence: List[RecommendedResource]
