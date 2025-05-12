import json
import os
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains.llm import LLMChain
from langchain.chat_models import ChatOpenAI

##############################################################################
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.schema import Document
from langchain.vectorstores import Qdrant
from qdrant_client import QdrantClient
from src.model.rerank import FlashRerank
from typing import List
from src.model.abstractModel import AbstractLLM
from langchain.retrievers import ContextualCompressionRetriever
from langchain.text_splitter import RecursiveCharacterTextSplitter
from transformers import FSMTForConditionalGeneration, FSMTTokenizer
from langchain.schema import Document


apiKey = ""
os.environ["OPENAI_API_KEY"] = apiKey
os.environ["OPENAI_API_MODEL"] = "gpt-3.5-turbo-16k"


class GptLLm(AbstractLLM):
    def __init__(self, model_name: str, vectorLookup: bool = True):
        self.model_name = model_name
        self.llm = ChatOpenAI(openai_api_key=apiKey, model_name=self.model_name)
        # check if vectorLookup is true
        if vectorLookup:
            self.vectorDB = Qdrant(
                client=QdrantClient(url="http://localhost:6333"),
                collection_name="Gesetze",
                embeddings=OpenAIEmbeddings(openai_api_key=apiKey),
            )

    def summarize(self, legal_text: str) -> str:
        # loader = WebBaseLoader("https://lilianweng.github.io/posts/2023-06-23-agent/")
        # docs = loader.load()

        prompt_template = """Write a concise summary of the following legal text. If it the text is not law related, apologize and do not write a summary. Please keep the summary short:
        "{text}"
        CONCISE SUMMARY:"""

        prompt = PromptTemplate.from_template(prompt_template)
        llm_chain = LLMChain(llm=self.llm, prompt=prompt)
        stuff_chain = StuffDocumentsChain(
            llm_chain=llm_chain, document_variable_name="text"
        )

        docs = [
            Document(
                page_content=legal_text,
            )
        ]

        return str(stuff_chain.run(docs))

    def answer_question(
        self,
        legal_text: str,
        summary: str,
        detected_laws: list[dict],
        prev_qa: [(str, str)],
        new_question: str,
    ) -> str:
        ai_Template = (
            "You are a helpful assistant that gives answers according to this legal text: {legal_text} "
            "\n\n. And also the previous chat {history}. If the text is not law or legal related do not "
            "answer and apologize and tell that you can only help in the law and legal related areas. If "
            "you do not know the current situation then give answers according to what you know and state "
            "the date. "
        )
        human_template = "{text}"
        history = "NONE"

        if prev_qa:
            joined_elements = [f"{item[0]}" + " \n " + f"{item[1]}" for item in prev_qa]
            history = " \n ".join(joined_elements)
        chat_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", ai_Template),
                ("human", human_template),
            ]
        )
        json_detected_laws = json.dumps(
            [{key: law[key] for key in ["name", "text"]} for law in detected_laws],
            ensure_ascii=False,
        )
        messages = chat_prompt.format_messages(
            legal_text=legal_text,
            history=history,
            text=new_question,
            detected_laws=json_detected_laws,
        )
        # chain = chat_prompt | self.llm
        return self.llm(messages).content

    def answer_question_chat_only(
        self, prev_qa: [(str, str)], new_question: str, detected_laws: list[dict]
    ):
        # ai_Template = """You are a helpful assistant, who gives legal advice based on you previous knowledge. If the 
        # text is not law or legal related do not answer and apologize and tell that you can only help in the law and 
        # legal related areas. If you do not know the current situation then give answers according to what you know 
        # and state the date. Answer according to the earlier conversations: {history}. And also according to the 
        # following laws: {summaries}. You will also get the list of the varius laws detected in the text, you can also use
        # these as a basis of you answer. The detected laws:{detected_laws}"""

        ai_Template = """You are a chatbot for the german law, your purpose is to simplify this complex domain for the user,
        who is likely to be a layperson. The user might ask questions that aren't strictly law-related, that is not your purpose.
        You can respond briefly, but remind the user that you are a legal chatbot. If the user persists, stop responding. 
        Answer according to the earlier conversations: {history}. 
        The user may ask a question in german or english. Respond in whichever language the user chooses.
        You will also receive a set of laws which might be relevant to the users current query: {summaries}.
        They might not be relevant, so make your own judgement how strongly to lean on these for your answer.
        Ideally, the laws are very relevant, and you base your answer entirely on them, but this is unlikely to be the case.
        If the laws are irrelevant, or simply don't contain much information, just answer from your own knowledge to the best of your ability.
        The text may cite specific german laws, you may use these as a basis for your answer as well: {detected_laws}"""

        history = "NONE"
        if prev_qa:
            joined_elements = [f"{item[0]}" + " \n " + f"{item[1]}" for item in prev_qa]
            history = " \n ".join(joined_elements)

        detected_laws_str = "\n".join(
            [
                f"{idx+1}: {law['name']}: {law['text']}"
                for idx, law in enumerate(detected_laws)
            ]
        )
        ai_Template = ai_Template.format(
            history=history, summaries="{summaries}", detected_laws=detected_laws_str
        )

        messages = [
            SystemMessagePromptTemplate.from_template(ai_Template),
            HumanMessagePromptTemplate.from_template("{question}"),
        ]
        # add translated text
        prompt = ChatPromptTemplate.from_messages(messages)
        chain_type_kwargs = {"prompt": prompt}
        retriever = self.vectorDB.as_retriever(search_kwargs={"k": 10})
        compressor = FlashRerank()
        compression_retriever = ContextualCompressionRetriever(
            base_compressor=compressor, base_retriever=retriever
        )

        chain = RetrievalQAWithSourcesChain.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=compression_retriever,
            return_source_documents=True,
            chain_type_kwargs=chain_type_kwargs,
        )
        result = chain(new_question)
        """translation = self.translateSource(result["source_documents"])

         for i, trans in enumerate(translation):
            result["source_documents"][i].page_content = (
                result["source_documents"][i].page_content + trans
            )
            result["source_documents"][i].metadata["source"] = (
                result["source_documents"][i].metadata["source"] + trans
            )
        """

        return result["answer"], result["source_documents"]

    def translateViaGPT(self, reference) -> List[str]:
        prompt_template = """Translate the following text to english. 
         It is a legal text, so it is important that citations remain unchanged after translation. 
         Examples of citations are: § 92 Abs. 3 Satz 1 VwGO, § 173 Satz 1 VwGO, or § 6 Satz 2 Nummer.
         Here, the german words "Satz" and "Nummer" should remain german after the translation.
         It is important that your translation is accurate, but it is also important that it is simple and understandable.
         This is the text: {text}
        """

        prompt = PromptTemplate.from_template(prompt_template)
        llm_chain = LLMChain(llm=self.llm, prompt=prompt)
        stuff_chain = StuffDocumentsChain(
            llm_chain=llm_chain, document_variable_name="text"
        )

        docs = [
            Document(
                page_content=reference,
            )
        ]

        return str(stuff_chain.run(docs))
