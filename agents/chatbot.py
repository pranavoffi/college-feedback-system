#finalized
# chatbot.py

# from langchain.llms import Ollama
# from langchain.prompts import PromptTemplate
# from langchain.chains import RetrievalQA
#
#
# class ChatbotAgent:
#     def __init__(self):
#         self.llm = Ollama(model="llama3.2:3b", temperature=0.2)
#         self.vectordb = None
#         self.base_prompt = PromptTemplate(
#             input_variables=["context", "question"],
#             template="""
# You are a helpful assistant analyzing **student-written feedback**. All feedback is written by students and refers to professors and departments. Do not treat feedback as being authored by the professors.
#
# Each feedback includes:
# - The department
# - The professor being referred to
# - The student’s comment
#
# 📚 Context:
# {context}
#
# ❓ Question:
# {question}
#
# ✅ Instructions:
# - Only refer to feedback made by students.
# - Mention professors and departments as subjects, not speakers.
# - Use only the context provided — do not hallucinate.
#
# 💬 Answer:
# """
#         )
#
#     def setup(self, vectordb):
#         self.vectordb = vectordb
#
#     def ask(self, query: str) -> str:
#         retriever = self.vectordb.as_retriever(search_kwargs={"k": 10})
#         chain = RetrievalQA.from_chain_type(
#             llm=self.llm,
#             chain_type="stuff",
#             retriever=retriever,
#             chain_type_kwargs={"prompt": self.base_prompt}
#         )
#         return chain.run(query)
















# chatbot.py

from langchain.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA


class ChatbotAgent:
    def __init__(self):
        self.llm = Ollama(model="llama3.2:3b", temperature=0.2)
        self.vectordb = None
        self.base_prompt = PromptTemplate(
            input_variables=["context", "question"],
            template="""
You are a helpful assistant analyzing **student-written feedback**. All feedback is written by students and refers to professors and departments. Do not treat the feedback as being authored by the professors.

Each feedback includes:
- The department
- The professor being referred to
- The student’s comment

📚 Context:
{context}

❓ Question:
{question}

✅ Instructions:
- Only refer to feedback made by students.
- Mention professors and departments as subjects, not speakers.
- Use only the context provided — do not hallucinate.

💬 Answer:
"""
        )

    def setup(self, vectordb):
        self.vectordb = vectordb

    def ask(self, query: str) -> tuple[str, list]:
        retriever = self.vectordb.as_retriever(search_kwargs={"k": 10})
        docs = retriever.get_relevant_documents(query)

        chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            chain_type_kwargs={"prompt": self.base_prompt}
        )

        answer = chain.run(query)
        return answer, docs
