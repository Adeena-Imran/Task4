After Context7 is connected, you will create an agent using:
● OpenAgents SDK
● Streamlit 
● PyPDF (for PDF text extraction)
● Gemini CLI
● Context7 MCP (tool provider)

What the Agent Will Do
Agent 1: PDF Summarizer
● User uploads a PDF.
● Text is extracted using PyPDF.
● Agent generates a clean, meaningful summary.
● Summary can appear in any UI style students choose (card, block,
container, etc.).

Agent 2: Quiz Generator
● After summarization, the user can click Create Quiz.
● The agent reads the original PDF (not the summary).
● It generates:
○ MCQs
○ Or mixed-style quizzes