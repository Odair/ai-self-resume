# ai-self-resume
An assistant that speaks as the professional (e.g., Odair Santiago) to answer questions about career, experience, and skills.
It uses Gradio for the chat UI, OpenAI for responses, PyPDF to read a LinkedIn profile PDF, and function calling to log:

interested contacts (record_user_contact)

unknown questions the assistant couldn’t answer (record_unknown_question)

## Features

Automatic profile summary from resume/profile.pdf → generates resume/summary.txt.

First-person chat (stays in character as {self.name}).

Initial greeting in the chat.

Tools (function calling):

record_user_contact(email, name?, notes?) → appends to resume/contacts.txt

record_unknown_question(question) → appends to resume/questions.txt

## Requirements

Python 3.10+
uv 0.8.8+

Install deps:
uv sync


### Environment variables
Create a .env file at the project root:

OPENAI_API_KEY=sk-xxxxxxx

### Files

Download your profile pdf from linkedin or use some resume in pdf
