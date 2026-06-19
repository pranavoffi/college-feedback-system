# 🎓 College Feedback Analysis System

A fully AI-powered feedback analysis system built to automate sentiment detection, summarization, comparison, and conversational exploration of student feedback data across departments and years. It runs entirely on local LLMs via [Ollama](https://ollama.com/) — no external API keys, no data leaving your machine.

---

## 🚩 Problem Statement

- Colleges collect massive amounts of student feedback, often as unstructured CSVs containing free-form text.
- Manual review of feedback is slow, subjective, and rarely scalable to thousands of entries.
- There's no standard CSV format, which makes ingestion and processing difficult.
- Institutions lack tools to interactively analyze how feedback changes across years or departments.

## ✅ Solution Overview

- Automated ingestion, cleaning, and standardization of raw CSV files.
- Sentiment classification using LLaMA 3.2 with custom prompts.
- Deep summarization of feedback per department/professor, including hidden sentiment detection in "neutral" responses.
- An interactive chatbot powered by RAG (Retrieval-Augmented Generation) that answers questions directly from the feedback data, with no hallucination.
- The ability to compare two academic years side by side and highlight what improved or regressed.

---

## 🧠 How It Works

The system is organized as a set of cooperating agents, each handling one stage of the pipeline:

| Agent | File | What it does |
|---|---|---|
| 🧹 Data Cleaner | `data_cleaner.py` | Uses an Ollama LLM (with a fuzzy-matching fallback) to map mismatched column names to a standard schema. |
| 🔍 Sentiment Classifier | `agents/sentiment.py` | Classifies every feedback row as Positive, Neutral, or Negative. |
| 📝 Summarizer | `agents/summarizer.py` | Produces a bullet-point overall summary of positive and negative themes, including sentiment hidden in neutral comments. |
| 🧠 Vector Store / Ingestion | `ingest.py`, `config.py` | Embeds cleaned feedback with `nomic-embed-text` and stores it in ChromaDB for semantic search. |
| 🤖 Chatbot | `agents/chatbot.py` | A RAG-powered assistant (LangChain `RetrievalQA`) that answers questions using only retrieved feedback, and shows its retrieved context. |
| 📈 Comparison | `enhanced_feedback_system.py`, `main.py` | Embeds two CSVs (e.g. 2023 vs 2024) into separate Chroma collections and uses an LLM to compare trends across them. |

### 🧹 Data Cleaner Agent
- Uses LLaMA 3.2 (via Ollama) to intelligently map mismatched column names (e.g. `prof_name` → `Teacher`).
- Falls back to keyword/fuzzy matching if the LLM call fails or returns an unparsable response.
- Filters out irrelevant columns like "Sentiment", "Rating", or "Score".
- Guarantees a clean, standardized schema: `ID`, `Department`, `Teacher`, `FeedbackText`.

### 🔍 Sentiment Classifier Agent
- Classifies every row as Positive, Neutral, or Negative using a prompt-tuned LLaMA 3.2 model.
- Designed to support a fine-tuned model (`llama3.2_feedback_analyzer`) for improved, domain-specific accuracy — see [Setup Notes](#-setup-notes--things-to-configure-before-running) below.

### 📝 Summarization Agent
- Aggregates feedback and extracts key positive and negative themes with an LLM summarizer.
- Specifically analyzes neutral feedback for embedded sentiment instead of discarding it.
- Outputs a visually structured, bullet-point summary suitable for management review.

### 🧠 Vector Database (ChromaDB)
- All cleaned feedback is embedded using `nomic-embed-text` (served locally through Ollama) and stored in ChromaDB.
- Enables real-time semantic search and similarity-based retrieval.
- Each stored document carries `id`, `department`, and `teacher` metadata for contextual filtering.

### 🤖 Chatbot Agent (RAG-Powered)
- An interactive assistant built with LangChain's `RetrievalQA` chain and LLaMA 3.2.
- Answers only from what's retrieved out of ChromaDB — no hallucinated facts.
- Supports natural-language queries such as:
  - "How is Dr. Iyer performing in Mathematics?"
  - "What are the top concerns in the Chemistry department?"
- Displays the retrieved context alongside each answer for transparency.

### 📈 Comparison Agent (Multi-Year Feedback Analysis)
- Accepts two CSV uploads (e.g. `2023.csv` and `2024.csv`).
- Embeds and stores each year in its own Chroma collection.
- Retrieves relevant feedback from both years for a given question and asks the LLM to identify:
  - Areas that improved
  - Issues that remain unresolved
  - New negative concerns
- Useful for accreditation reports, quality audits, or strategic review meetings.

---

## 🚀 Key Technologies

- **LLM:** LLaMA 3.2 (served locally via [Ollama](https://ollama.com/))
- **Embeddings:** `nomic-embed-text`
- **Vector Store:** ChromaDB
- **Pipeline / Orchestration:** LangChain
- **Frontend:** Streamlit
- **Data handling:** pandas

---

## 📁 Project Structure

```
college-feedback-system/
├── app.py                       # Main Streamlit app: clean → classify → summarize → chat (single CSV)
├── main.py                      # Streamlit app for multi-year comparison (two CSVs)
├── enhanced_feedback_system.py  # Core helpers used by main.py (load/embed/store/compare across years)
├── data_cleaner.py              # LLM-assisted + fallback column mapping / cleaning
├── ingest.py                    # Converts cleaned feedback into LangChain Documents + Chroma store
├── config.py                    # Embedding model + vector store path configuration
├── visualize_vectors.py         # Utility script(s) for inspecting the vector store (currently disabled)
├── agents/
│   ├── sentiment.py              # Sentiment classification chain
│   ├── summarizer.py             # Overall feedback summarizer
│   └── chatbot.py                # RAG chatbot agent
├── db/                           # Persisted Chroma index + cleaned/classified feedback CSV
├── chroma_langchain/             # Per-year Chroma collections used by the comparison agent
└── requirements.txt
```

---

## 🧰 Prerequisites

- Python 3.10+
- [Ollama](https://ollama.com/) installed and running locally
- The following models pulled in Ollama:
  ```bash
  ollama pull llama3.2
  ollama pull llama3.2:3b
  ollama pull nomic-embed-text
  ```

## 📦 Installation

```bash
git clone https://github.com/pranavoffi/college-feedback-system.git
cd college-feedback-system
python -m venv venv
source venv/bin/activate      # on Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Make sure Ollama is running in the background (`ollama serve`) before launching either app.

---

## ▶️ Usage

This project ships with two Streamlit entry points:

**1. Single-dataset analysis (cleaning → sentiment → summary → chatbot)**
```bash
streamlit run app.py
```
- Upload a single feedback CSV.
- The app auto-cleans/maps columns, classifies sentiment, generates an overall summary, builds the vector store, and spins up the RAG chatbot.

**2. Multi-year comparison**
```bash
streamlit run main.py
```
- Upload two CSVs (one per year), label each year, embed both, and ask comparison questions across them.

### Expected CSV format
The data cleaner will try to auto-map your columns, but results are most reliable if your CSV contains columns that can be mapped to:

| Standard field | Example source columns |
|---|---|
| `ID` | `id`, `number` |
| `Department` | `dept`, `division` |
| `Teacher` | `prof_name`, `instructor`, `faculty` |
| `FeedbackText` | `comments`, `studentcomments`, `review` |

> Note: `main.py` / `enhanced_feedback_system.py` expect lowercase `feedback`, `teacher`, and `subject` columns directly, since they don't go through `data_cleaner.py`.

---

## ⚙️ Setup Notes / Things to Configure Before Running

- `agents/sentiment.py` references a custom Ollama model named `llama3.2_feedback_analyzer`. This is intended to be a fine-tuned/prompt-tuned variant of LLaMA 3.2 for this domain. If you haven't created that model yet, either:
  - build it locally with an Ollama `Modelfile`, or
  - swap the model name in `load_llm()` back to a base model such as `llama3.2:3b`.
- Vector store paths (`db/chroma_index` and `chroma_langchain/<year>/`) are created automatically on first run and persist locally — delete them if you want to start fresh.
- `visualize_vectors.py` contains utility functions for inspecting the vector store and running CLI-based inference, but the code is currently commented out and kept for reference/experimentation.

---

## 🗺️ Roadmap

- [ ] Fine-tune LLaMA 3.2 on labeled feedback for improved sentiment accuracy.
- [ ] Per-department and per-professor breakdown views (in addition to the overall summary).
- [ ] Export summaries and comparison reports as PDF/Word documents.
- [ ] Support for more than two years in the comparison agent.

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome. Feel free to open an issue or submit a pull request.

## 👤 Author

**Pranav** — [@pranavoffi](https://github.com/pranavoffi)

## 📄 License

This project is currently unlicensed. Add a `LICENSE` file (e.g. MIT) if you'd like to specify usage terms.
