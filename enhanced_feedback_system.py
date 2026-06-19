#
# import os
# import sqlite3
# import pandas as pd
# import requests
# import chromadb
# from chromadb.config import Settings
# from chromadb.utils.embedding_functions import EmbeddingFunction
# from typing import List, Dict, Any, Tuple
# import re
# from tqdm import tqdm
# import time
# import numpy as np
# from datetime import datetime
# import json
#
# # Configuration
# CHROMA_DB_DIR = "./chroma_db"
# SQLITE_DB_PATH = "./feedback_analytics.db"
#
#
# class EnhancedFeedbackSystem:
#     def __init__(self):
#         self.setup_chromadb()
#         self.setup_sqlite()
#
#     def setup_chromadb(self):
#         """Initialize ChromaDB for semantic search"""
#         self.embedding_function = OllamaEmbeddingFunction()
#         self.chroma_client = chromadb.Client(Settings(
#             persist_directory=CHROMA_DB_DIR,
#             anonymized_telemetry=False
#         ))
#         self.collection = self.chroma_client.get_or_create_collection(
#             name="teacher_feedback",
#             embedding_function=self.embedding_function
#         )
#
#     def setup_sqlite(self):
#         """Initialize SQLite for structured analytics"""
#         self.conn = sqlite3.connect(SQLITE_DB_PATH)
#         self.create_tables()
#
#     def create_tables(self):
#         """Create necessary tables for analytics"""
#         cursor = self.conn.cursor()
#
#         # Teacher metrics table for fast analytics
#         cursor.execute('''
#             CREATE TABLE IF NOT EXISTS teacher_metrics (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 teacher TEXT NOT NULL,
#                 subject TEXT,
#                 department TEXT,
#                 year TEXT NOT NULL,
#                 total_feedback INTEGER DEFAULT 0,
#                 avg_rating REAL,
#                 positive_feedback_count INTEGER DEFAULT 0,
#                 negative_feedback_count INTEGER DEFAULT 0,
#                 neutral_feedback_count INTEGER DEFAULT 0,
#                 improvement_mentioned INTEGER DEFAULT 0,
#                 last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#                 UNIQUE(teacher, subject, year)
#             )
#         ''')
#
#         # Individual feedback records
#         cursor.execute('''
#             CREATE TABLE IF NOT EXISTS feedback_records (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 teacher TEXT NOT NULL,
#                 subject TEXT,
#                 department TEXT,
#                 year TEXT NOT NULL,
#                 feedback_text TEXT,
#                 rating REAL,
#                 sentiment_score REAL,
#                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#             )
#         ''')
#
#         self.conn.commit()
#
#     def analyze_sentiment(self, text: str) -> Tuple[str, float]:
#         """Simple sentiment analysis using keyword matching"""
#         if not text:
#             return "neutral", 0.0
#
#         text_lower = text.lower()
#
#         positive_words = [
#             'excellent', 'great', 'good', 'amazing', 'helpful', 'clear', 'engaging',
#             'knowledgeable', 'patient', 'encouraging', 'inspiring', 'improved',
#             'better', 'best', 'love', 'appreciate', 'thank', 'wonderful'
#         ]
#
#         negative_words = [
#             'poor', 'bad', 'terrible', 'unclear', 'confusing', 'boring', 'difficult',
#             'slow', 'fast', 'needs improvement', 'disappointing', 'frustrating',
#             'hard to follow', 'unclear', 'disorganized', 'unprepared'
#         ]
#
#         positive_count = sum(1 for word in positive_words if word in text_lower)
#         negative_count = sum(1 for word in negative_words if word in text_lower)
#
#         if positive_count > negative_count:
#             return "positive", min(positive_count / 5.0, 1.0)
#         elif negative_count > positive_count:
#             return "negative", -min(negative_count / 5.0, 1.0)
#         else:
#             return "neutral", 0.0
#
#     def extract_rating_from_text(self, text: str) -> float:
#         """Extract numeric rating from feedback text"""
#         if not text or not isinstance(text, str):
#             return None
#
#         # Look for patterns like "8/10", "4.5/5", "3 out of 5"
#         patterns = [
#             r'(\d+\.?\d*)\s*/\s*(\d+)',  # 8/10, 4.5/5
#             r'(\d+\.?\d*)\s+out\s+of\s+(\d+)',  # 4 out of 5
#             r'rate.*?(\d+\.?\d*)',  # rate 8
#         ]
#
#         try:
#             for pattern in patterns:
#                 match = re.search(pattern, text.lower())
#                 if match:
#                     if len(match.groups()) == 2:
#                         numerator, denominator = float(match.group(1)), float(match.group(2))
#                         return (numerator / denominator) * 5.0  # Normalize to 5-point scale
#                     else:
#                         return min(float(match.group(1)), 5.0)
#         except (ValueError, TypeError):
#             pass
#
#         return None
#
#     def process_csv_enhanced(self, file_path: str, year: str = None) -> bool:
#         """Enhanced CSV processing with analytics"""
#         try:
#             print(f"📁 Loading CSV: {file_path}")
#             df = pd.read_csv(file_path)
#
#             if df.empty:
#                 print("❌ CSV file is empty")
#                 return False
#
#             # Column mapping (same as original)
#             HEADER_MAP = {
#                 'teacher': ['teacher', 'instructor', 'faculty', 'professor', 'prof', 'teacher_name', 'instructor_name',
#                             'mentor'],
#                 'subject': ['subject', 'course', 'class', 'module', 'course_name', 'subject_name', 'course_code',
#                             'subject name'],
#                 'feedback': ['feedback', 'comments', 'review', 'remarks', 'comment', 'student_feedback', 'evaluation',
#                              'studentcomments'],
#                 'rating': ['rating', 'score', 'grade', 'marks', 'satisfaction', 'rating_score'],
#                 'department': ['department', 'dept', 'division', 'school', 'faculty_dept', 'branch']
#             }
#
#             def match_column(df_columns: List[str], target_key: str) -> str:
#                 df_columns_lower = [col.lower().strip() for col in df_columns]
#                 if target_key in HEADER_MAP:
#                     for synonym in HEADER_MAP[target_key]:
#                         for i, col in enumerate(df_columns_lower):
#                             if synonym in col or col in synonym:
#                                 return df_columns[i]
#                 return None
#
#             # Map columns
#             teacher_col = match_column(df.columns.tolist(), 'teacher')
#             subject_col = match_column(df.columns.tolist(), 'subject')
#             feedback_col = match_column(df.columns.tolist(), 'feedback')
#             rating_col = match_column(df.columns.tolist(), 'rating')
#             dept_col = match_column(df.columns.tolist(), 'department')
#
#             print(f"🔍 Column mapping:")
#             print(f"  Teacher: {teacher_col}")
#             print(f"  Subject: {subject_col}")
#             print(f"  Feedback: {feedback_col}")
#             print(f"  Department: {dept_col}")
#
#             if not feedback_col:
#                 print("❌ Could not find feedback column")
#                 return False
#
#             # Process each row
#             teacher_stats = {}
#             documents = []
#             metadatas = []
#             ids = []
#
#             print("🔄 Processing feedback data...")
#
#             for idx, row in tqdm(df.iterrows(), total=len(df), desc="Processing rows"):
#                 feedback_text = str(row.get(feedback_col, "")).strip()
#
#                 if not feedback_text or len(feedback_text) < 10:
#                     continue
#
#                 teacher = str(row.get(teacher_col, "Unknown")).strip() if teacher_col else "Unknown"
#                 subject = str(row.get(subject_col, "Unknown")).strip() if subject_col else "Unknown"
#                 department = str(row.get(dept_col, "Unknown")).strip() if dept_col else "Unknown"
#                 data_year = year or str(datetime.now().year)
#
#                 # Extract or analyze rating
#                 rating = None
#                 if rating_col and pd.notna(row.get(rating_col)):
#                     try:
#                         rating = float(row.get(rating_col))
#                     except (ValueError, TypeError):
#                         rating = self.extract_rating_from_text(str(row.get(rating_col)))
#                 else:
#                     rating = self.extract_rating_from_text(feedback_text)
#
#                 # Sentiment analysis
#                 sentiment, sentiment_score = self.analyze_sentiment(feedback_text)
#
#                 # Store in SQLite
#                 cursor = self.conn.cursor()
#                 try:
#                     cursor.execute('''
#                         INSERT INTO feedback_records
#                         (teacher, subject, department, year, feedback_text, rating, sentiment_score)
#                         VALUES (?, ?, ?, ?, ?, ?, ?)
#                     ''', (teacher, subject, department, data_year, feedback_text, rating, sentiment_score))
#                 except Exception as e:
#                     print(f"⚠️ Error inserting record {idx}: {e}")
#                     continue
#
#                 # Aggregate teacher stats
#                 key = (teacher, subject, data_year)
#                 if key not in teacher_stats:
#                     teacher_stats[key] = {
#                         'teacher': teacher,
#                         'subject': subject,
#                         'department': department,
#                         'year': data_year,
#                         'total_feedback': 0,
#                         'ratings': [],
#                         'positive': 0,
#                         'negative': 0,
#                         'neutral': 0,
#                         'improvement_mentioned': 0
#                     }
#
#                 stats = teacher_stats[key]
#                 stats['total_feedback'] += 1
#
#                 if rating:
#                     stats['ratings'].append(rating)
#
#                 if sentiment == 'positive':
#                     stats['positive'] += 1
#                 elif sentiment == 'negative':
#                     stats['negative'] += 1
#                 else:
#                     stats['neutral'] += 1
#
#                 if any(word in feedback_text.lower() for word in ['improve', 'better', 'progress']):
#                     stats['improvement_mentioned'] += 1
#
#                 # Prepare for ChromaDB
#                 enriched_text = f"Teacher: {teacher} | Subject: {subject} | Feedback: {feedback_text}"
#                 if rating:
#                     enriched_text += f" | Rating: {rating}"
#
#                 documents.append(enriched_text)
#                 metadatas.append({
#                     'teacher': teacher,
#                     'subject': subject,
#                     'feedback': feedback_text,
#                     'rating': str(rating) if rating else "",
#                     'year': data_year,
#                     'department': department,
#                     'sentiment': sentiment,
#                     'sentiment_score': sentiment_score,
#                     'source_file': os.path.basename(file_path),
#                     'row_index': idx
#                 })
#                 ids.append(f"{file_path}_{idx}")
#
#             # Insert aggregated teacher metrics
#             cursor = self.conn.cursor()
#             for key, stats in teacher_stats.items():
#                 avg_rating = np.mean(stats['ratings']) if stats['ratings'] else None
#
#                 cursor.execute('''
#                     INSERT OR REPLACE INTO teacher_metrics
#                     (teacher, subject, department, year, total_feedback, avg_rating,
#                      positive_feedback_count, negative_feedback_count, neutral_feedback_count,
#                      improvement_mentioned)
#                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
#                 ''', (stats['teacher'], stats['subject'], stats['department'], stats['year'],
#                       stats['total_feedback'], avg_rating, stats['positive'],
#                       stats['negative'], stats['neutral'], stats['improvement_mentioned']))
#
#             self.conn.commit()
#
#             # Add to ChromaDB
#             if documents:
#                 print(f"📝 Adding {len(documents)} documents to ChromaDB...")
#                 batch_size = 100
#                 for i in range(0, len(documents), batch_size):
#                     batch_docs = documents[i:i + batch_size]
#                     batch_metas = metadatas[i:i + batch_size]
#                     batch_ids = ids[i:i + batch_size]
#
#                     try:
#                         self.collection.add(
#                             documents=batch_docs,
#                             metadatas=batch_metas,
#                             ids=batch_ids
#                         )
#                     except Exception as e:
#                         print(f"⚠️ ChromaDB batch error: {e}")
#                         continue
#
#             print(f"✅ Successfully processed {len(documents)} feedback records")
#             return True
#
#         except Exception as e:
#             print(f"❌ Error processing {file_path}: {e}")
#             return False
#
#     def compare_teachers_across_years(self, teacher_name: str = None) -> str:
#         """Compare teacher performance across years"""
#         cursor = self.conn.cursor()
#
#         if teacher_name:
#             query = '''
#                 SELECT teacher, year, avg_rating, total_feedback,
#                        positive_feedback_count, negative_feedback_count,
#                        improvement_mentioned
#                 FROM teacher_metrics
#                 WHERE teacher LIKE ?
#                 ORDER BY teacher, year
#             '''
#             cursor.execute(query, (f'%{teacher_name}%',))
#         else:
#             query = '''
#                 SELECT teacher, year, avg_rating, total_feedback,
#                        positive_feedback_count, negative_feedback_count,
#                        improvement_mentioned
#                 FROM teacher_metrics
#                 ORDER BY teacher, year
#             '''
#             cursor.execute(query)
#
#         results = cursor.fetchall()
#
#         if not results:
#             return "No data found for the specified criteria."
#
#         # Group by teacher
#         teacher_data = {}
#         for row in results:
#             teacher, year, avg_rating, total_feedback, positive, negative, improvement = row
#             if teacher not in teacher_data:
#                 teacher_data[teacher] = []
#             teacher_data[teacher].append({
#                 'year': year,
#                 'avg_rating': avg_rating,
#                 'total_feedback': total_feedback,
#                 'positive': positive,
#                 'negative': negative,
#                 'improvement_mentioned': improvement
#             })
#
#         # Generate comparison report
#         report = "📊 TEACHER PERFORMANCE COMPARISON\n" + "=" * 50 + "\n\n"
#
#         for teacher, years_data in teacher_data.items():
#             if len(years_data) < 2:
#                 continue
#
#             report += f"👨‍🏫 {teacher}\n" + "-" * 30 + "\n"
#
#             # Sort by year
#             years_data.sort(key=lambda x: x['year'])
#
#             for year_data in years_data:
#                 year = year_data['year']
#                 rating = year_data['avg_rating']
#                 total = year_data['total_feedback']
#                 positive = year_data['positive']
#                 negative = year_data['negative']
#
#                 report += f"  📅 {year}: "
#                 if rating:
#                     report += f"Rating {rating:.2f}/5.0 "
#                 report += f"({total} feedback, {positive} positive, {negative} negative)\n"
#
#             # Calculate improvement
#             if len(years_data) >= 2:
#                 latest = years_data[-1]
#                 previous = years_data[-2]
#
#                 if latest['avg_rating'] and previous['avg_rating']:
#                     rating_change = latest['avg_rating'] - previous['avg_rating']
#                     if rating_change > 0.2:
#                         report += f"  📈 IMPROVED: Rating increased by {rating_change:.2f} points\n"
#                     elif rating_change < -0.2:
#                         report += f"  📉 DECLINED: Rating decreased by {abs(rating_change):.2f} points\n"
#                     else:
#                         report += f"  ➡️ STABLE: Rating changed by {rating_change:.2f} points\n"
#
#                 positive_change = latest['positive'] - previous['positive']
#                 if positive_change > 0:
#                     report += f"  ✅ {positive_change} more positive feedback\n"
#                 elif positive_change < 0:
#                     report += f"  ❌ {abs(positive_change)} fewer positive feedback\n"
#
#             report += "\n"
#
#         return report
#
#     def get_semantic_analysis(self, query: str, n_results: int = 10) -> str:
#         """Get semantic analysis using ChromaDB + LLM"""
#         try:
#             # Search ChromaDB
#             results = self.collection.query(
#                 query_texts=[query],
#                 n_results=n_results
#             )
#
#             if not results["documents"][0]:
#                 return "No relevant feedback found."
#
#             documents = results["documents"][0]
#             metadatas = results["metadatas"][0] if results["metadatas"] else [{}] * len(documents)
#
#             # Prepare context for LLM
#             context = ""
#             for i, (doc, meta) in enumerate(zip(documents, metadatas)):
#                 teacher = meta.get('teacher', 'Unknown')
#                 subject = meta.get('subject', 'Unknown')
#                 year = meta.get('year', 'Unknown')
#                 sentiment = meta.get('sentiment', 'unknown')
#                 feedback = meta.get('feedback', doc.split('Feedback: ')[-1] if 'Feedback: ' in doc else doc)
#
#                 context += f"[{year}] {teacher} - {subject} ({sentiment}): {feedback}\n"
#
#             # Get LLM analysis
#             prompt = f"""You are an educational feedback analysis assistant. Analyze the following feedback data and answer the user's question.
#
# FEEDBACK DATA:
# {context}
#
# USER QUESTION: {query}
#
# Provide a comprehensive analysis focusing on:
# 1. Key patterns and trends
# 2. Specific teacher performance insights
# 3. Year-over-year comparisons if applicable
# 4. Actionable recommendations
#
# ANALYSIS:"""
#
#             try:
#                 response = requests.post(
#                     "http://localhost:11434/api/generate",
#                     json={
#                         "model": "llama3.2:3b",
#                         "prompt": prompt,
#                         "stream": False,
#                         "options": {
#                             "temperature": 0.3,
#                             "num_predict": 500
#                         }
#                     },
#                     timeout=60
#                 )
#                 response.raise_for_status()
#                 llm_analysis = response.json()["response"].strip()
#
#                 return f"🤖 AI ANALYSIS:\n{llm_analysis}\n\n📝 SOURCE DATA:\n{context}"
#
#             except Exception as e:
#                 return f"📝 SEARCH RESULTS:\n{context}\n\n⚠️ LLM analysis unavailable: {e}"
#
#         except Exception as e:
#             return f"❌ Search error: {e}"
#
#     def get_quick_stats(self) -> str:
#         """Get quick database statistics"""
#         cursor = self.conn.cursor()
#
#         # Basic stats
#         cursor.execute("SELECT COUNT(*) FROM feedback_records")
#         total_feedback = cursor.fetchone()[0]
#
#         cursor.execute("SELECT COUNT(DISTINCT teacher) FROM teacher_metrics")
#         total_teachers = cursor.fetchone()[0]
#
#         cursor.execute("SELECT COUNT(DISTINCT year) FROM teacher_metrics")
#         total_years = cursor.fetchone()[0]
#
#         # Year-wise breakdown
#         cursor.execute("""
#             SELECT year, COUNT(*) as feedback_count,
#                    AVG(avg_rating) as avg_rating,
#                    SUM(positive_feedback_count) as total_positive
#             FROM teacher_metrics
#             GROUP BY year
#             ORDER BY year
#         """)
#         year_stats = cursor.fetchall()
#
#         stats = f"📊 DATABASE STATISTICS\n" + "=" * 40 + "\n"
#         stats += f"📋 Total Feedback: {total_feedback}\n"
#         stats += f"👨‍🏫 Total Teachers: {total_teachers}\n"
#         stats += f"📅 Years Covered: {total_years}\n\n"
#
#         stats += "📈 Year-wise Summary:\n" + "-" * 25 + "\n"
#         for year, count, avg_rating, positive in year_stats:
#             avg_rating_str = f"{avg_rating:.2f}" if avg_rating else "N/A"
#             stats += f"  {year}: {count} records, Avg Rating: {avg_rating_str}, Positive: {positive}\n"
#
#         return stats
#
#
# # Custom embedding function (same as original)
# class OllamaEmbeddingFunction(EmbeddingFunction):
#     def __call__(self, texts: List[str]) -> List[List[float]]:
#         results = []
#         for text in texts:
#             try:
#                 response = requests.post(
#                     "http://localhost:11434/api/embeddings",
#                     json={"model": "llama3.2:3b", "prompt": text},
#                     timeout=30
#                 )
#                 response.raise_for_status()
#                 results.append(response.json()["embedding"])
#             except Exception as e:
#                 print(f"Error getting embedding: {e}")
#                 results.append([0.0] * 4096)
#         return results
#
#
# def main():
#     """Enhanced main interface"""
#     system = EnhancedFeedbackSystem()
#
#     print("🎓 ENHANCED COLLEGE FEEDBACK ANALYSIS SYSTEM")
#     print("=" * 60)
#
#     while True:
#         print("\n" + "=" * 50)
#         print("MAIN MENU")
#         print("=" * 50)
#         print("1. 📁 Upload & Process CSV File")
#         print("2. 🔍 Ask Semantic Questions (AI-Powered)")
#         print("3. 📊 Compare Teachers Across Years")
#         print("4. 📈 View Database Statistics")
#         print("5. 🧹 Clear All Data")
#         print("6. ❌ Exit")
#         print("=" * 50)
#
#         choice = input("Choose an option (1-6): ").strip()
#
#         if choice == "1":
#             file_path = input("Enter CSV file path: ").strip()
#             year = input("Enter year (optional): ").strip()
#
#             if file_path:
#                 print(f"\n🔄 Processing {file_path}...")
#                 success = system.process_csv_enhanced(file_path, year if year else None)
#                 if success:
#                     print("\n✅ Processing completed successfully!")
#                     print("\n" + system.get_quick_stats())
#
#         elif choice == "2":
#             print("\n🤖 AI-POWERED SEMANTIC ANALYSIS")
#             print("💡 Example questions:")
#             print("  • How did teaching quality change from 2023 to 2024?")
#             print("  • Which teachers show improvement trends?")
#             print("  • What are common student complaints?")
#             print("  • Compare Dr. Kumar's performance across years")
#
#             while True:
#                 query = input("\n🧠 Your question (or 'back' to return): ").strip()
#                 if query.lower() == 'back':
#                     break
#                 if query:
#                     print("\n🔍 Analyzing...")
#                     result = system.get_semantic_analysis(query)
#                     print(f"\n{result}\n")
#
#         elif choice == "3":
#             teacher_filter = input("Enter teacher name to filter (or press Enter for all): ").strip()
#             print("\n🔄 Generating comparison report...")
#
#             comparison = system.compare_teachers_across_years(
#                 teacher_filter if teacher_filter else None
#             )
#             print(f"\n{comparison}")
#
#         elif choice == "4":
#             print("\n" + system.get_quick_stats())
#
#         elif choice == "5":
#             confirm = input("\n⚠️ Clear all data? Type 'yes' to confirm: ")
#             if confirm.lower() == 'yes':
#                 try:
#                     # Clear ChromaDB
#                     system.collection.delete()
#
#                     # Clear SQLite
#                     cursor = system.conn.cursor()
#                     cursor.execute("DELETE FROM teacher_metrics")
#                     cursor.execute("DELETE FROM feedback_records")
#                     system.conn.commit()
#
#                     print("✅ All data cleared successfully")
#                 except Exception as e:
#                     print(f"❌ Error clearing data: {e}")
#             else:
#                 print("❌ Operation cancelled")
#
#         elif choice == "6":
#             print("\n👋 Thank you for using the Enhanced Feedback Analysis System!")
#             system.conn.close()
#             break
#
#         else:
#             print("\n❌ Invalid choice. Please select 1-6.")
#
#
# if __name__ == "__main__":
#     try:
#         main()
#     except KeyboardInterrupt:
#         print("\n\n👋 Goodbye!")
#     except Exception as e:
#         print(f"\n❌ Unexpected error: {e}")




import os
import pandas as pd
from langchain.embeddings import OllamaEmbeddings
from langchain.vectorstores import Chroma
from langchain.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.schema import Document
from langchain.chains import LLMChain

VECTOR_DB_ROOT = "./chroma_langchain"
OLLAMA_EMBED_MODEL = "nomic-embed-text"
OLLAMA_LLM_MODEL = "llama3.2"
TOP_K = 10


def load_csv_as_documents(csv_path: str, year_tag: str) -> list[Document]:
    df = pd.read_csv(csv_path, encoding="utf-8", encoding_errors="ignore")
    if 'feedback' not in df.columns:
        raise ValueError("CSV must contain a 'feedback' column.")

    documents = []
    for _, row in df.iterrows():
        feedback = str(row.get("feedback", "")).strip()
        if not feedback or len(feedback) < 5:
            continue
        teacher = row.get("teacher", "Unknown")
        subject = row.get("subject", "Unknown")
        metadata = {
            "year": year_tag,
            "teacher": teacher,
            "subject": subject
        }
        content = f"[{year_tag}] Teacher: {teacher}, Subject: {subject}, Feedback: {feedback}"
        documents.append(Document(page_content=content, metadata=metadata))
    return documents


def store_in_chroma(docs: list[Document], year_tag: str, embedder: OllamaEmbeddings) -> Chroma:
    collection_path = os.path.join(VECTOR_DB_ROOT, year_tag)
    if not os.path.exists(collection_path):
        os.makedirs(collection_path)
    db = Chroma.from_documents(
        documents=docs,
        embedding=embedder,
        persist_directory=collection_path,
        collection_name=f"feedback_{year_tag}"
    )
    db.persist()
    return db


def retrieve_feedback(db: Chroma, query: str) -> str:
    docs = db.similarity_search(query, k=TOP_K)
    return "\n".join([doc.page_content for doc in docs])


def create_llm_chain(llm: Ollama) -> LLMChain:
    prompt = PromptTemplate(
        input_variables=["feedback_data", "question"],
        template="""You are a feedback analysis assistant. Analyze the following feedbacks to answer the user's question.

FEEDBACK DATA:
{feedback_data}

QUESTION:
{question}

Provide:
- Year-over-year comparison
- Trends and teacher performance
- Areas needing improvement

Answer:"""
    )
    return LLMChain(llm=llm, prompt=prompt)


def main():
    embedder = OllamaEmbeddings(model=OLLAMA_EMBED_MODEL)
    llm = Ollama(model=OLLAMA_LLM_MODEL)
    chain = create_llm_chain(llm)

    print("📂 Upload first CSV (e.g. 2023)")
    csv1 = input("CSV path for year 1: ").strip()
    year1 = input("Year label (e.g. 2023): ").strip()
    docs1 = load_csv_as_documents(csv1, year1)
    db1 = store_in_chroma(docs1, year1, embedder)

    print("\n📂 Upload second CSV (e.g. 2024)")
    csv2 = input("CSV path for year 2: ").strip()
    year2 = input("Year label (e.g. 2024): ").strip()
    docs2 = load_csv_as_documents(csv2, year2)
    db2 = store_in_chroma(docs2, year2, embedder)

    print("\n✅ Data stored. Ask your analysis questions!")

    while True:
        query = input("\nAsk a question (or type 'exit'): ").strip()
        if query.lower() == "exit":
            break
        # Retrieve from both DBs
        result1 = retrieve_feedback(db1, query)
        result2 = retrieve_feedback(db2, query)
        context = f"{result1}\n---\n{result2}"
        # LLM analysis
        response = chain.run(feedback_data=context, question=query)
        print("\n🧠 AI Analysis:\n", response)


if __name__ == "__main__":
    main()
