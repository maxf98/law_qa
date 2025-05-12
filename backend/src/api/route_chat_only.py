import secrets

from fastapi import APIRouter, HTTPException, BackgroundTasks, status, Response

from src.api.background_tasks import chat_only_answer_question
from src.api.background_tasks import translateViaGPTSide
from src.api.in_out_models import *
from src.api.session_data import ChatOnlySessionData
from src.data.lawbook import LawBook
from src.law_lookup.referenced import ReferencedLookUp
from src.model.llmFactory import LLMFactory

chat_only_sessions: dict[str, ChatOnlySessionData] = {}

factory = LLMFactory()
model = factory.createModel(model_name="Gpt")
law_books = LawBook.get_all_books_from_cache()
referenced_lookup = ReferencedLookUp(law_books)

chat_router = APIRouter()


@chat_router.post(
    "/sessions",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {
            "model": OutSessionId,
            "description": "New session created",
        }
    },
    name="Create a new session",
)
async def create_session():
    session_id = secrets.token_urlsafe(16)
    chat_only_sessions[session_id] = ChatOnlySessionData()
    return {"session_id": session_id}


@chat_router.get(
    "/sessions/{session_id}",
    responses={
        status.HTTP_200_OK: {
            "model": OutChatOnlySessionStatus,
            "description": "Session status returned",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": OutErrorResponse,
            "description": "Session not found",
        },
    },
    name="Get session status",
)
async def check_session(session_id):
    session = chat_only_sessions.get(session_id)
    if not session:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Session not found")
    return {
        "session_id": session_id,
        "qa_length": len(session.q_and_a),
        "last_question_answered": None
        if len(session.q_and_a) == 0
        else (session.q_and_a[-1][1] is not None),
    }


@chat_router.get(
    "/sessions/{session_id}/qa",
    responses={
        status.HTTP_200_OK: {"model": OutQA, "description": "Q&A list is returned"},
        status.HTTP_202_ACCEPTED: {
            "model": OutQA,
            "description": "Q&A list is returned, "
                           "but the last answer is not yet generated",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": OutErrorResponse,
            "description": "Session not found",
        },
    },
    name="Get list of questions and answers",
)
async def get_questions(session_id, response: Response):
    session = chat_only_sessions.get(session_id)
    if not session:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Session not found")

    if len(session.q_and_a) >= 1 and not session.q_and_a[-1][1]:
        response.status_code = status.HTTP_202_ACCEPTED

    return {"q_and_a": session.q_and_a}


@chat_router.post(
    "/sessions/{session_id}/qa",
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        status.HTTP_202_ACCEPTED: {
            "model": None,
            "description": "Started processing new question",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": OutErrorResponse,
            "description": "Previous question not yet answered",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": OutErrorResponse,
            "description": "Session not found",
        },
    },
    name="Post a new question",
    operation_id="post_new_question_with_reference",
)
async def post_new_question_with_reference(
        session_id, in_body: InQuestion, background_tasks: BackgroundTasks
):
    session = chat_only_sessions.get(session_id)
    if not session:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Session not found")

    if len(session.q_and_a) > 0 and not session.q_and_a[-1][1]:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, detail="Previous question not yet answered"
        )

    background_tasks.add_task(
        chat_only_answer_question,
        session,
        model,
        referenced_lookup,
        in_body.new_question,
    )


@chat_router.get(
    "/sessions/{session_id}/references",
    responses={
        status.HTTP_200_OK: {
            "model": OutReferences,
            "description": "References returned as list of list",
        },
        status.HTTP_202_ACCEPTED: {
            "model": OutReferences,
            "description": "references list is returned, "
                           "but the last answer is not yet generated",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": OutErrorResponse,
            "description": "Session not found",
        },
    },
    name="Get list of list of references, both vector and regex",
)
async def get_references(session_id, response: Response):
    session = chat_only_sessions.get(session_id)
    if not session:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Session not found")

    if len(session.q_and_a) >= 1 and not session.q_and_a[-1][1]:
        response.status_code = status.HTTP_202_ACCEPTED

    return {
        "regex_references": session.references_regex,
        "vector_references": session.references_vector,
    }


@chat_router.post(
    "/translate",
    responses={
        status.HTTP_200_OK: {
            "model": InOutText,
            "description": "Translated content",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": OutErrorResponse,
            "description": "Invalid request",
        },
    },
    name="Translate via GPT",
)
async def translate_via_gpt(request: InOutText):
    try:
        translated_content = translateViaGPTSide(model, request.text)
        return {
            "text": translated_content
        }
    except Exception as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e))


@chat_router.post(
    "/reference_lookup",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": OutReferencesRegexList,
            "description": "Found references in text are returned",
        }
    },
    name="Find regex references in text",
)
async def create_session(request: InRegexLookup):
    references = referenced_lookup.find_references(request.text, request.book)
    return {"regex_references": references}
