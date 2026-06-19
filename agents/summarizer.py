# agents/summarizer.py

# from langchain.llms import Ollama
# from langchain.prompts import PromptTemplate
# from langchain.chains import LLMChain
# import pandas as pd
#
# class SummarizerAgent:
#     def __init__(self):
#         self.llm = Ollama(model="llama3.2:3b", temperature=0.3)
#         self._setup()
#
#     def _setup(self):
#         self.positive_chain = LLMChain(
#             llm=self.llm,
#             prompt=PromptTemplate(
#                 input_variables=["feedback_list"],
#                 template="Summarize the following positive feedback:\n\n{feedback_list}\n\nSummary:"
#             )
#         )
#         self.negative_chain = LLMChain(
#             llm=self.llm,
#             prompt=PromptTemplate(
#                 input_variables=["feedback_list"],
#                 template="Summarize the following negative feedback:\n\n{feedback_list}\n\nSummary:"
#             )
#         )
#
#     def _prepare(self, df, sentiment):
#         return "\n".join(
#             f"- {row['Department']} - {row['Teacher']}: {row['FeedbackText']}"
#             for _, row in df[df["Sentiment"] == sentiment].head(20).iterrows()
#         )
#
#     def generate(self, df: pd.DataFrame):
#         return {
#             "positive_summary": self.positive_chain.run(feedback_list=self._prepare(df, "Positive")),
#             "negative_summary": self.negative_chain.run(feedback_list=self._prepare(df, "Negative"))
#         }









# agents/summarizer.py

# from langchain.llms import Ollama
# from langchain.prompts import PromptTemplate
# from langchain.chains import LLMChain
# import pandas as pd
# from typing import Dict
#
# class SummarizerAgent:
#     def __init__(self):
#         self.llm = Ollama(model="llama3.2:3b", temperature=0.3)
#         self._setup()
#
#     def _setup(self):
#         self.department_prompt = PromptTemplate(
#             input_variables=["department", "feedback_block"],
#             template="""
#             📚 **Department: {department}**
#
#             You are an academic evaluator summarizing student feedback for the {department} department. Each entry may contain both positive and negative points. The goal is to present the findings in a readable, visually clear, and management-friendly format.
#
#             ---
#             ### ✨ **Overall Department Summary**
#             - Give 1–2 concise bullets on department-wide strengths and areas needing improvement.
#
#             ---
#             ### ✅ **Positive Feedback**
#             - Use bullet points to list **praise-worthy** teaching practices or experiences.
#             - Include professor names in parentheses.
#
#             ---
#             ### ⚠️ **Negative Feedback**
#             - Use bullet points to list **issues, challenges, or frustrations** expressed by students.
#             - Include professor names in parentheses.
#
#             Feedback to analyze:
#             {feedback_block}
#
#             🎯 **Your Output Format:**
#
#             📚 **Department: {department}**
#
#             ✨ **Overall Department Summary**
#             - [Overall summary point 1]
#             - [Overall summary point 2]
#
#             ✅ **Positive Feedback**
#             - [Positive point] (Prof. Name)
#             - ...
#
#             ⚠️ **Negative Feedback**
#             - [Negative point] (Prof. Name)
#             - ...
#             """
#         )
#
#         self.chain = LLMChain(llm=self.llm, prompt=self.department_prompt)
#
#     def _prepare_feedback_block(self, df: pd.DataFrame, department: str) -> str:
#         dept_df = df[df["Department"].str.lower() == department.lower()]
#         lines = []
#         for _, row in dept_df.iterrows():
#             text = row["FeedbackText"]
#             teacher = row["Teacher"]
#             lines.append(f"- {text} (Prof. {teacher})")
#         return "\n".join(lines)
#
#     def generate_department_summaries(self, df: pd.DataFrame) -> Dict[str, str]:
#         summaries = {}
#         departments = df["Department"].dropna().unique()
#
#         for dept in departments:
#             block = self._prepare_feedback_block(df, dept)
#             if block.strip():
#                 summary = self.chain.run(department=dept, feedback_block=block)
#                 summaries[dept.lower().replace(" ", "_")] = summary.strip()
#
#         return summaries
#
#     def generate(self, df: pd.DataFrame) -> Dict[str, str]:
#         """Main entrypoint: returns dict of department-based summaries"""
#         return self.generate_department_summaries(df)









# overall summery

from langchain.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import pandas as pd
from typing import Dict


class SummarizerAgent:
    def __init__(self):
        self.llm = Ollama(model="llama3.2:3b", temperature=0.3)
        self._setup()

    def _setup(self):
        self.prompt = PromptTemplate(
            input_variables=["feedback_block"],
            template="""
You are a feedback analyst helping a college management team understand student experiences. You are provided with raw student feedback from various departments and professors. Each feedback may contain a mix of praise and criticism — even if labeled neutral.

🎯 Your task:
- Read all feedback.
- Identify all meaningful positive and negative points.
- Summarize clearly and objectively in bullet format.
- Do NOT omit any feedback — especially embedded sentiments in neutral comments.

📚 Feedback to analyze:
{feedback_block}

---

📊 Output Format:

✨ **Overall Feedback Summary**
- [Concise overall insight 1]
- [Insight 2 about major themes or patterns]

✅ **Positive Feedback**
summarize overall positive feedback

⚠️ **Negative Feedback**
summarize overall negative feedback
"""
        )
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)

    def _prepare_feedback_block(self, df: pd.DataFrame) -> str:
        lines = []
        for _, row in df.iterrows():
            text = row.get("FeedbackText", "").strip()
            teacher = row.get("Teacher", "").strip()
            if text:
                lines.append(f"- {text} (Prof. {teacher})")
        return "\n".join(lines)

    def generate(self, df: pd.DataFrame) -> Dict[str, str]:
        """Generates one overall feedback summary"""
        block = self._prepare_feedback_block(df)
        summary = self.chain.run(feedback_block=block)
        return {"overall": summary.strip()}
