from src.api.session_data import ChatOnlySessionData
from src.law_lookup.referenced import ReferencedLookUp
from src.model.abstractModel import AbstractLLM


def chat_only_answer_question(
    session_data: ChatOnlySessionData,
    model: AbstractLLM,
    referenced_lookup: ReferencedLookUp,
    new_question,
):
    session_data.append_qa(new_question, None)
    session_data.references_regex.append(
        referenced_lookup.find_references(new_question)
    )
    answer = model.answer_question_chat_only(
        session_data.q_and_a[:-1], new_question, session_data.references_regex[-1]
    )
    session_data.set_last_answer(answer[0])
    references = [
        {
            "paragraph": ref.metadata["id"],
            "book": ref.metadata["book_name"],
            "text": f"{ref.metadata['title']}\n{ref.metadata['source']}",
        }
        for ref in answer[1]
    ]
    session_data.references_vector.append(references)


def translateViaGPTSide(model: AbstractLLM, reference) -> str:
    translated = model.translateViaGPT(reference)
    return translated
