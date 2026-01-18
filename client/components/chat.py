import pandas as pd
import streamlit as st

from datetime import datetime

from utils.helpers import process_user_input


# def render_user_input(model_provider, model):
  
#     disable_input = (
#         st.session_state.get("unsubmitted_files", False)
#         or not st.session_state.get(f"uploaded_files_{st.session_state.uploader_key}", [])
#         or not st.session_state.get("chat_ready")
#     )

#     question = st.chat_input(
#         "💬 Ask a Question from the PDF Files",
#         disabled=disable_input
#     )

#     if not question:
#         return

#     with st.chat_message("user"):
#         st.markdown(question)

#     with st.chat_message("ai"):
#         with st.spinner("Thinking..."):

#             output = process_user_input(model_provider, model, question)
#             st.markdown(output)

#             # ✅ 关键修复：保证 pdf_names 一定是 list
#             pdf_files = st.session_state.get("pdf_files") or []
#             pdf_names = [f.name for f in pdf_files]

#             # ✅ 关键修复：append 不放在 try 里
#             st.session_state.chat_history.append(
#                 (question, output, model_provider, model, pdf_names, datetime.now())
#             )

def render_user_input(model_provider, model):
    disable_input = (
        st.session_state.get("unsubmitted_files", False)
        or not st.session_state.get(f"uploaded_files_{st.session_state.uploader_key}", [])
        or not st.session_state.get("chat_ready")
    )

    question = st.chat_input(
        "💬 Ask a Question from the PDF Files",
        disabled=disable_input
    )

    if not question:
        return

    # 1️⃣ 即时渲染用户消息
    with st.chat_message("user"):
        st.markdown(question)

    # 2️⃣ 即时渲染模型回复
    with st.chat_message("ai"):
        with st.spinner("Thinking..."):
            output = process_user_input(model_provider, model, question)
            st.markdown(output)

    # 3️⃣ 写入 session_state（关键）
    pdf_files = st.session_state.get("pdf_files") or []
    pdf_names = [f.name for f in pdf_files]

    st.session_state.chat_history.append(
        (question, output, model_provider, model, pdf_names, datetime.now())
    )

    # 4️⃣ 🔥 关键一步：立刻 rerun，让 UI 看到最新状态
    st.rerun()

def render_uploaded_files_expander():
  uploaded_files = st.session_state.get(f"uploaded_files_{st.session_state.uploader_key}", [])
  if uploaded_files and not st.session_state.get("unsubmitted_files"):
    with st.expander("📎 Uploaded Files:"):
      for f in uploaded_files:
        st.markdown(f"- {f.name}")

def render_chat_history():
  for q, a, *_ in st.session_state.get("chat_history", []):
    with st.chat_message("user"):
      st.markdown(q)
    with st.chat_message("ai"):
      st.markdown(a)

def render_download_chat_history():
    records = []
    for q, a, provider, model, pdfs, ts in st.session_state.get("chat_history", []):
        records.append({
            "Question": q,
            "Answer": a,
            "Model Provider": provider,
            "Model Name": model,
            "PDF File": ", ".join(pdfs) if isinstance(pdfs, list) else str(pdfs),
            "Timestamp": ts
        })

    df = pd.DataFrame(records)

    with st.expander("📦 Download Chat History", expanded=True):
        st.download_button(
            "📥 Download as CSV",
            df.to_csv(index=False).encode("utf-8"),
            "chat_history.csv",
            "text/csv"
        )