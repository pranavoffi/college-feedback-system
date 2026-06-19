# ingest.py

import os
import pandas as pd
import shutil
from langchain.schema import Document
from langchain.vectorstores import Chroma
from config import VECTOR_STORE_PATH, get_embedding_model


def clean_text(text: str) -> str:
    return str(text).strip().replace("\n", " ")


def feedback_to_documents(df: pd.DataFrame) -> list:
    docs = []
    for _, row in df.iterrows():
        feedback_text = clean_text(row["FeedbackText"])
        teacher = str(row["Teacher"]).strip()
        department = str(row["Department"]).strip()

        full_text = (
            f"Student Feedback:\n"
            f"Department: {department}\n"
            f"Professor: {teacher}\n"
            f"{feedback_text}"
        )

        doc = Document(
            page_content=full_text,
            metadata={
                "id": int(row["ID"]),
                "department": department,
                "teacher": teacher
            }
        )
        docs.append(doc)
    return docs


def reset_vector_store():
    if os.path.exists(VECTOR_STORE_PATH):
        shutil.rmtree(VECTOR_STORE_PATH)
        print("🗑️ Vector store reset.")


def save_vector_store(docs: list):
    vectordb = Chroma.from_documents(
        documents=docs,
        embedding=get_embedding_model(),
        persist_directory=VECTOR_STORE_PATH
    )
    vectordb.persist()
    print(f"✅ Vector store saved to {VECTOR_STORE_PATH}")
    return vectordb
