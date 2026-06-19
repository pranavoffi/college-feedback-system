import streamlit as st
from enhanced_feedback_system import (
    load_csv_as_documents,
    store_in_chroma,
    retrieve_feedback,
    create_llm_chain,
    OllamaEmbeddings,
    Ollama,
    OLLAMA_EMBED_MODEL,
    OLLAMA_LLM_MODEL
)

st.set_page_config(page_title="📊 Feedback Analyzer", layout="wide")
st.title("📊 Teacher Feedback Comparison Assistant")
st.write("Upload two CSV files from different years and ask questions about feedback trends, improvement, and teaching quality.")

# Session state initialization
if "db1" not in st.session_state: st.session_state.db1 = None
if "db2" not in st.session_state: st.session_state.db2 = None
if "year1" not in st.session_state: st.session_state.year1 = ""
if "year2" not in st.session_state: st.session_state.year2 = ""
if "llm_chain" not in st.session_state: st.session_state.llm_chain = None

# Sidebar - Upload and settings
st.sidebar.header("🗂️ Upload CSV Feedback Files")

file1 = st.sidebar.file_uploader("Upload CSV for Year 1", type="csv")
year1 = st.sidebar.text_input("Label for Year 1", value="2023")

file2 = st.sidebar.file_uploader("Upload CSV for Year 2", type="csv")
year2 = st.sidebar.text_input("Label for Year 2", value="2024")

if file1 and file2 and st.sidebar.button("📥 Embed and Store"):
    with st.spinner("Processing and embedding feedback..."):
        embedder = OllamaEmbeddings(model=OLLAMA_EMBED_MODEL)
        docs1 = load_csv_as_documents(file1, year1)
        docs2 = load_csv_as_documents(file2, year2)
        db1 = store_in_chroma(docs1, year1, embedder)
        db2 = store_in_chroma(docs2, year2, embedder)

        st.session_state.db1 = db1
        st.session_state.db2 = db2
        st.session_state.year1 = year1
        st.session_state.year2 = year2
        st.session_state.llm_chain = create_llm_chain(Ollama(model=OLLAMA_LLM_MODEL))

    st.success("✅ Feedback embedded and stored!")

# Main interface for querying
st.divider()
st.subheader("🧠 Ask a Question")
query = st.text_input("Enter your analysis question here...")

if query and st.session_state.db1 and st.session_state.db2:
    with st.spinner("Generating analysis..."):
        result1 = retrieve_feedback(st.session_state.db1, query)
        result2 = retrieve_feedback(st.session_state.db2, query)
        context = f"{result1}\n---\n{result2}"

        response = st.session_state.llm_chain.run(feedback_data=context, question=query)

    st.markdown("### 💬 AI Response")
    st.markdown(response)
elif query:
    st.warning("Please upload and embed both CSV files before asking a question.")
