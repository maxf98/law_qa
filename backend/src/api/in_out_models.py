from typing import Tuple, List

from pydantic import BaseModel, Field


class OutChatOnlySessionStatus(BaseModel):
    session_id: str = Field(..., min_length=16, max_length=16)
    qa_length: int
    last_question_answered: bool | None


class OutSessionId(BaseModel):
    session_id: str = Field(..., min_length=16, max_length=16)


class OutErrorResponse(BaseModel):
    detail: str


class InQuestion(BaseModel):
    new_question: str


class OutQA(BaseModel):
    q_and_a: List[Tuple[str, str]]


class OutReferenceRegex(BaseModel):
    begin: List[int]
    end: List[int]
    book: str
    paragraph: str
    subparagraph: str
    name: str
    text: str


class OutReferencesVector(BaseModel):
    book: str
    paragraph: str
    text: str


class OutReferences(BaseModel):
    regex_references: List[List[OutReferenceRegex]]
    vector_references: List[List[OutReferencesVector]]


class OutReferencesRegexList(BaseModel):
    regex_references: List[OutReferenceRegex]


class InOutText(BaseModel):
    text: str


class InRegexLookup(BaseModel):
    text: str
    book: str | None
