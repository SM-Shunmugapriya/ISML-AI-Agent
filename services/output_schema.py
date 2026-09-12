from typing import List

from pydantic import BaseModel, Field, HttpUrl


class RecommendedResource(BaseModel):
    title: str = Field(min_length=1)
    type: str = Field(min_length=1)
    qualityScore: float = Field(ge=0.0, le=100.0)
    difficulty: str = Field(min_length=1)
    category: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    url: HttpUrl


class FinalOutput(BaseModel):
    topic: str = Field(min_length=1)
    recommendedResources: List[RecommendedResource]
    learningSequence: List[RecommendedResource]
