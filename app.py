# app.py

# import streamlit as st
# import pandas as pd
# from ingest import reset_vector_store, feedback_to_documents, save_vector_store, load_vector_store
# from agents.sentiment import load_llm, get_sentiment_chain, classify_sentiment
# from agents.summarizer import SummarizerAgent
# from agents.chatbot import ChatbotAgent
# from memory import SharedMemoryBuffer
#
# st.set_page_config(page_title="College Feedback Analyzer", layout="wide")
#
# # Session state initialization
# if "df" not in st.session_state:
#     st.session_state.df = None
# if "summaries" not in st.session_state:
#     st.session_state.summaries = None
# if "vectordb" not in st.session_state:
#     st.session_state.vectordb = None
# if "chatbot" not in st.session_state:
#     st.session_state.chatbot = None
# if "memory" not in st.session_state:
#     st.session_state.memory = SharedMemoryBuffer()
#
# st.title("📊 College Feedback Analyzer")
#
# uploaded = st.file_uploader("Upload Feedback CSV", type=["csv"])
#
# if uploaded:
#     df = pd.read_csv(uploaded)
#     st.success("✅ CSV Loaded")
#
#     if st.button("🚀 Process Data"):
#         st.info("🔄 Resetting vector store...")
#         reset_vector_store()
#         docs = feedback_to_documents(df)
#         vectordb = save_vector_store(docs)
#         st.session_state.vectordb = vectordb
#
#         st.info("🤖 Classifying sentiments...")
#         chain = get_sentiment_chain(load_llm())
#         df = classify_sentiment(df, chain)
#         df.to_csv("db/feedback_store.csv", index=False)
#         st.session_state.df = df
#         st.session_state.memory.update_data(df)
#
#         sentiment_counts = df["Sentiment"].value_counts()
#         st.success("✅ Sentiment analysis complete")
#         st.markdown(f"""### 📊 Sentiment Summary:
#         - 🟢 Positive: **{sentiment_counts.get("Positive", 0)}**
#         - 🟡 Neutral: **{sentiment_counts.get("Neutral", 0)}**
#         - 🔴 Negative: **{sentiment_counts.get("Negative", 0)}**
#         """)
#         st.dataframe(df, use_container_width=True)
#
#         st.info("📝 Generating summaries...")
#         summarizer = SummarizerAgent()
#         summaries = summarizer.generate(df)
#         st.session_state.summaries = summaries
#         st.session_state.memory.update_summaries(summaries)
#         st.success("🧠 Summarization complete")
#
#         for dept_key, summary in summaries.items():
#             dept_name = dept_key.replace("_", " ").title()
#             st.markdown(f"### 📚 {dept_name}")
#             st.markdown(summary, unsafe_allow_html=True)
#
#         st.session_state.chatbot = ChatbotAgent()
#         st.session_state.chatbot.setup(vectordb)
#         st.success("🤖 Chatbot is ready!")
#
# # Display existing results if already processed
# if st.session_state.df is not None and st.session_state.summaries:
#     st.divider()
#     st.subheader("💬 Ask the Chatbot")
#
#     query = st.text_input("Ask a question about feedback...")
#     if query and st.session_state.chatbot:
#         answer = st.session_state.chatbot.ask(query)
#         st.write("🤖", answer)
#












#finalized
# app.py

# import streamlit as st
# import pandas as pd
# from ingest import reset_vector_store, feedback_to_documents, save_vector_store
# from agents.sentiment import load_llm, get_sentiment_chain, classify_sentiment
# from agents.summarizer import SummarizerAgent
# from agents.chatbot import ChatbotAgent
#
# st.set_page_config(page_title="College Feedback Analyzer", layout="wide")
# st.title("📊 College Feedback Analyzer")
#
# # Session state
# for key in ["df", "summaries", "vectordb", "chatbot"]:
#     if key not in st.session_state:
#         st.session_state[key] = None
#
# uploaded = st.file_uploader("Upload Feedback CSV", type=["csv"])
#
# if uploaded:
#     df = pd.read_csv(uploaded)
#     st.success("✅ CSV Loaded")
#
#     if st.button("🚀 Process Data"):
#         st.info("🔄 Resetting vector store...")
#         reset_vector_store()
#         docs = feedback_to_documents(df)
#         vectordb = save_vector_store(docs)
#         st.session_state.vectordb = vectordb
#
#         st.info("🧠 Classifying sentiments...")
#         chain = get_sentiment_chain(load_llm())
#         df = classify_sentiment(df, chain)
#         df.to_csv("db/feedback_store.csv", index=False)
#         st.session_state.df = df
#
#         sentiment_counts = df["Sentiment"].value_counts()
#         st.success("✅ Sentiment analysis complete")
#         st.markdown(f"""### 📊 Sentiment Summary:
#         - 🟢 Positive: **{sentiment_counts.get("Positive", 0)}**
#         - 🟡 Neutral: **{sentiment_counts.get("Neutral", 0)}**
#         - 🔴 Negative: **{sentiment_counts.get("Negative", 0)}**
#         """)
#         st.dataframe(df, use_container_width=True)
#
#         st.info("📝 Generating summaries...")
#         summarizer = SummarizerAgent()
#         summaries = summarizer.generate(df)
#         st.session_state.summaries = summaries
#         st.success("🧠 Summarization complete")
#
#         for dept, summary in summaries.items():
#             st.markdown(f"### 📚 {dept.replace('_', ' ').title()}")
#             st.markdown(summary, unsafe_allow_html=True)
#
#         chatbot = ChatbotAgent()
#         chatbot.setup(vectordb)
#         st.session_state.chatbot = chatbot
#         st.success("🤖 Chatbot is ready!")
#
# # Chatbot UI
# if st.session_state.chatbot:
#     st.subheader("💬 Ask the Chatbot")
#     query = st.text_input("Ask about a department, professor, or feedback...")
#     if query:
#         answer = st.session_state.chatbot.ask(query)
#         st.write("🤖", answer)

























# app.py

import streamlit as st
import pandas as pd
from data_cleaner import smart_map_columns
from ingest import reset_vector_store, feedback_to_documents, save_vector_store
from agents.sentiment import load_llm, get_sentiment_chain, classify_sentiment
from agents.summarizer import SummarizerAgent
from agents.chatbot import ChatbotAgent

st.set_page_config(page_title="College Feedback Analyzer", layout="wide")
st.title("📊 College Feedback Analyzer")

# Initialize state
for key in ["df", "summaries", "vectordb", "chatbot", "messages"]:
    if key not in st.session_state:
        st.session_state[key] = [] if key == "messages" else None

# Upload CSV
uploaded = st.file_uploader("Upload Feedback CSV", type=["csv"])

if uploaded:
    df = smart_map_columns(uploaded)
    st.success("✅ CSV Cleaned & Loaded")

    if st.button("🚀 Process Data"):
        st.info("🔄 Resetting vector store...")
        reset_vector_store()
        docs = feedback_to_documents(df)
        vectordb = save_vector_store(docs)
        st.session_state.vectordb = vectordb

        st.info("🧠 Classifying sentiments...")
        chain = get_sentiment_chain(load_llm())
        df = classify_sentiment(df, chain)
        df.to_csv("db/feedback_store.csv", index=False)
        st.session_state.df = df

        sentiment_counts = df["Sentiment"].value_counts()
        st.success("✅ Sentiment analysis complete")
        st.markdown(f"""### 📊 Sentiment Summary:
        - 🟢 Positive: {sentiment_counts.get("Positive", 0)}
        - 🟡 Neutral: {sentiment_counts.get("Neutral", 0)}
        - 🔴 Negative: {sentiment_counts.get("Negative", 0)}
        """)
        st.dataframe(df, use_container_width=True)

        st.info("📝 Generating summaries...")
        summarizer = SummarizerAgent()
        summaries = summarizer.generate(df)
        st.session_state.summaries = summaries
        st.success("🧠 Summarization complete")

        #to summerize dept wise
        # for dept, summary in summaries.items():
        #     st.markdown(f"### 📚 {dept.replace('_', ' ').title()}")
        #     st.markdown(summary, unsafe_allow_html=True)

        st.markdown("### 📋 Overall Feedback Summary")
        st.markdown(summaries["overall"], unsafe_allow_html=True)


        chatbot = ChatbotAgent()
        chatbot.setup(vectordb)
        st.session_state.chatbot = chatbot
        st.success("🤖 Chatbot is ready!")

# -------------------------------
# 💬 Chatbot UI
# -------------------------------
if st.session_state.chatbot:
    st.divider()
    st.subheader("💬 Ask the Chatbot")

    if st.button("🔁 Clear Chat"):
        st.session_state.messages = []

    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant" and "docs" in msg:
                with st.expander("🔍 View Retrieved Context"):
                    for i, doc in enumerate(msg["docs"]):
                        st.markdown(f"**Doc {i+1}:**\n```\n{doc.page_content.strip()}\n```")

    # User input
    user_input = st.chat_input("Ask about feedback, professors, or departments...")
    if user_input:
        st.chat_message("user").markdown(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.spinner("Retrieving insights from student feedback..."):
            answer, docs = st.session_state.chatbot.ask(user_input)

        st.chat_message("assistant").markdown(answer)
        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
            "docs": docs
        })
