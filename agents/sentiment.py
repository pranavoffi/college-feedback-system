# agents/sentiment.py

from langchain.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import pandas as pd

def load_llm():
    # return Ollama(model="llama3.2_feedback_analyzer")
    return Ollama(model="llama3.2_feedback_analyzer")

def get_sentiment_chain(llm):
    prompt = PromptTemplate(
        input_variables=["feedback"],
        template="""You are an expert at analyzing student feedback sentiment. Classify the sentiment of the following student feedback about their teacher/course.

Guidelines:
- POSITIVE: Feedback expressing satisfaction, praise, appreciation, or positive learning experience
- NEGATIVE: Feedback expressing dissatisfaction, complaints, criticism, or poor learning experience  
- NEUTRAL: Feedback that is purely factual, balanced, or neither clearly positive nor negative

Feedback: "{feedback}"

Sentiment:"""
    )
    return LLMChain(llm=llm, prompt=prompt)

def classify_sentiment(df: pd.DataFrame, chain: LLMChain) -> pd.DataFrame:
    sentiments = []
    for text in df["FeedbackText"]:
        try:
            response = chain.run(feedback=text).strip().lower()
            if "pos" in response:
                sentiments.append("Positive")
            elif "neg" in response:
                sentiments.append("Negative")
            else:
                sentiments.append("Neutral")
        except:
            sentiments.append("Neutral")
    df["Sentiment"] = sentiments
    return df
