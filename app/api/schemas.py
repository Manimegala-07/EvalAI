from pydantic import BaseModel
from typing import List


class GradeRequest(BaseModel):
    references: List[str]
    students: List[str]


class GradeResponse(BaseModel):
    score: float
    similarity: float
    feedback: str
