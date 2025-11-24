import streamlit as st
import asyncio
import os
import tempfile

from my_agent import SummarizerAgent, QuizGeneratorAgent   # <-- TWO AGENTS NOW
from my_agent import Runner


# ---------------------------
# ASYNC EXECUTOR
# ---------------------------
async def run_agent_and_display_tools(selected_agent, prompt: str) -> str:
    result = await Runner.run(selected_agent, prompt)
    final_output = result.final_output

    # Capture tool outputs
    tool_outputs = [
        item for item in result.new_items
        if item.__class__.__name__ == "ToolCallOutputItem"
    ]

    if tool_outputs:
        combined = "\n".join(
            getattr(item, "output", "No tool output") for item in tool_outputs
        )
        with st.expander("Agent Tool Outputs (Debugging)"):
            st.info(combined)
        return combined

    return final_output


# ---------------------------
# STREAMLIT UI
# ---------------------------
st.set_page_config(page_title="PDF Assistant", layout="wide")
st.title("📄 PDF Summarizer & Quiz Generator")

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploaded_file_name" not in st.session_state:
    st.session_state.uploaded_file_name = None
if "summary" not in st.session_state:
    st.session_state.summary = None
if "quiz" not in st.session_state:
    st.session_state.quiz = None


# ---------------------------
# SIDEBAR CHAT (memory-enabled)
# ---------------------------
with st.sidebar:
    st.header("Chat with Assistant")

    # Show history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # New user message
    if user_prompt := st.chat_input("Ask me anything..."):
        st.session_state.messages.append({"role": "user", "content": user_prompt})

        with st.chat_message("user"):
            st.markdown(user_prompt)

        with st.spinner("Agent Thinking..."):

            # Use SummarizerAgent for general assistant chat
            response = asyncio.run(run_agent_and_display_tools(SummarizerAgent, user_prompt))

        st.session_state.messages.append({"role": "assistant", "content": response})

        with st.chat_message("assistant"):
            st.markdown(response)


# ---------------------------
# MAIN AREA – PDF PROCESSING
# ---------------------------
st.header("Upload PDF for Summary & Quiz")
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:

    # Detect new file uploaded
    if (
        st.session_state.uploaded_file_name != uploaded_file.name
        or f"extracted_text_{uploaded_file.name}" not in st.session_state
    ):
        st.write("Extracting text from PDF...")

        # Save temp file for agent tools
        pdf_bytes = uploaded_file.getvalue()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            temp_pdf.write(pdf_bytes)
            temp_path = temp_pdf.name

        with st.spinner("Extracting via SummarizerAgent..."):
            extract_prompt = f"Extract text from PDF at this file path: {temp_path}"
            extracted = asyncio.run(run_agent_and_display_tools(SummarizerAgent, extract_prompt))

        # Clean temp file
        try:
            os.remove(temp_path)
        except Exception as e:
            st.warning(f"Could not delete temporary file: {e}")

        # Store
        if extracted.startswith("Error"):
            st.error(extracted)
            st.session_state[f"extracted_text_{uploaded_file.name}"] = ""
        else:
            st.session_state[f"extracted_text_{uploaded_file.name}"] = extracted

        st.session_state.uploaded_file_name = uploaded_file.name
        st.session_state.summary = None
        st.session_state.quiz = None

        if not extracted.startswith("Error"):
            st.success("Text extracted successfully!")

    extracted_text = st.session_state.get(f"extracted_text_{uploaded_file.name}", "")

    if extracted_text and not extracted_text.startswith("Error"):

        with st.expander("View Extracted Text"):
            st.text_area("Extracted Text", extracted_text, height=300, disabled=True)

        col1, col2 = st.columns(2)

        # ---------------------------
        # SUMMARY BUTTON
        # ---------------------------
        with col1:
            if st.button("Generate Summary"):
                with st.spinner("Summarizing..."):
                    summary_prompt = f"Summarize this document:\n\n{extracted_text}"
                    summary_output = asyncio.run(
                        run_agent_and_display_tools(SummarizerAgent, summary_prompt)
                    )
                    st.session_state.summary = summary_output

                if not summary_output.startswith("Error"):
                    st.success("Summary generated!")

        # ---------------------------
        # QUIZ BUTTON
        # ---------------------------
        with col2:
            if st.button("Generate Quiz"):
                with st.spinner("Generating quiz..."):
                    quiz_prompt = f"Generate a quiz from this document:\n\n{extracted_text}"
                    quiz_output = asyncio.run(
                        run_agent_and_display_tools(QuizGeneratorAgent, quiz_prompt)
                    )
                    st.session_state.quiz = quiz_output

                if not quiz_output.startswith("Error"):
                    st.success("Quiz generated!")

        # Output sections
        if st.session_state.summary:
            st.subheader("Document Summary")
            if st.session_state.summary.startswith("Error"):
                st.error(st.session_state.summary)
            else:
                st.markdown(st.session_state.summary)

        if st.session_state.quiz:
            st.subheader("Generated Quiz")
            if st.session_state.quiz.startswith("Error"):
                st.error(st.session_state.quiz)
            else:
                st.markdown(st.session_state.quiz)
