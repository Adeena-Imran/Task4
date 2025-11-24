import os
import asyncio
from dotenv import load_dotenv
from openai import AsyncOpenAI
from agents import Agent, OpenAIChatCompletionsModel, Runner
from tools import (
    read_user_profile, 
    update_user_profile, 
    extract_text_from_pdf,
    summarize_document,
    generate_quiz
)

load_dotenv()

# Initialize Gemini API client
openai_client = AsyncOpenAI(
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    api_key=os.getenv("GEMINI_API_KEY")
)

gemini_model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=openai_client
)

# SUMMARIZER AGENT
SummarizerAgent = Agent(
    name="PDF Summarizer",
    instructions=(
        "You are an expert PDF summarization assistant. "
        "When a user requests a summary, use `summarize_document`. "
        "If the user provides a PDF path, extract text first using `extract_text_from_pdf`."
    ),
    model=gemini_model,
    tools=[
        read_user_profile,
        update_user_profile,
        extract_text_from_pdf,
        summarize_document
    ]
)

# QUIZ GENERATOR AGENT
QuizGeneratorAgent = Agent(
    name="PDF Quiz Generator",
    instructions=(
        "You generate quizzes based on provided text. "
        "Use `generate_quiz`. Extract text from PDFs first."
    ),
    model=gemini_model,
    tools=[
        read_user_profile,
        update_user_profile,
        extract_text_from_pdf,
        generate_quiz
    ]
)

# ------- TEST FUNCTION -------
async def main():
    # Correct way to run agents:
    result1 = await Runner.run(SummarizerAgent, "Summarize this PDF: myfile.pdf")
    print("\nSUMMARY OUTPUT:\n", result1.final_output)

    result2 = await Runner.run(QuizGeneratorAgent, "Generate a quiz from myfile.pdf")
    print("\nQUIZ OUTPUT:\n", result2.final_output)


if __name__ == "__main__":
    asyncio.run(main())


