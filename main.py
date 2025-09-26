from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader
import gradio as gr
import json

load_dotenv(override=True)

def record_user_contact(email, name="Name not provided", notes="not provided"):
   with open("resume/contacts.txt", "a", encoding="utf-8") as f:
        f.write(f"\tEmail: {email} - Name: {name} - Notes: {notes}\n")

def record_unknown_question(question):
        with open("resume/questions.txt", "a", encoding="utf-8") as f:
            f.write(f"{question}\n")


record_user_contact_json = {
    "name": "record_user_contact",
    "description": "Use this tool to record that a user is interested in being in touch and provided an email address, name and some notes",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {
                "type": "string",
                "description": "The email address of this user"
            },
            "name": {
                "type": "string",
                "description": "The user's name, if they provided it"
            }
            ,
            "notes": {
                "type": "string",
                "description": "Any additional information about the conversation that's worth recording to give context"
            }
        },
        "required": ["email"],
        "additionalProperties": False
    }
}

record_unknown_question_json = {
    "name": "record_unknown_question",
    "description": "Always use this tool to record any question that couldn't be answered as you didn't know the answer",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "The question that couldn't be answered"
            },
        },
        "required": ["question"],
        "additionalProperties": False
    }
}

tools =[{"type": "function", "function": record_user_contact_json}, {"type": "function", "function": record_unknown_question_json}]


class Myself:

    def __init__(self):
        self.openai = OpenAI()
        self.name= 'Odair Santiago'
        reader = PdfReader("resume/profile.pdf")
        self.linkedin = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                self.linkedin += text
        
        self.generateSummary()
        
        with open("resume/summary.txt", "r", encoding="utf-8") as f:
            self.summary = f.read()

    def systemPrompt(self):
        prompt = f"""
                    You are acting as {self.name}, faithfully representing their professional background and career story. 
                    Your role is to answer questions about {self.name}'s career, work experience, job challenges, and skill set.  

                    You are provided with a professional summary and LinkedIn profile to base your answers on. 
                    Always remain professional, clear, and engaging — as if speaking to a potential client, recruiter, or employer visiting the website.  

                    ### Important Guidelines:
                    - Stay in character as {self.name} at all times.  
                    - If you don't know the answer, use the `record_unknown_question` tool to log the question (even if it seems trivial or unrelated to career).  
                    - If the user shows genuine interest or starts a conversation, guide them toward leaving their email, name and notes.  
                    - Politely ask for their email, name and notes.  
                    - Record it using the `record_user_contact` tool.  

                    ### Resources:
                    **Summary:**  
                    {self.summary}  

                    **LinkedIn Profile:**  
                    {self.linkedin}  

                    With this context, engage in conversation as {self.name}.
                    """
        return prompt



    def generateSummary(self):
        prompt = f"""
                    You are an AI specialized in summarizing professional profiles. 
                    Your task is to read a LinkedIn profile and produce a concise summary 
                    focused only on professional background, experiences, and skills. 
                    Do not include personal details such as email, phone number, or links.  

                    ### Profile:
                    {self.linkedin}

                    ### Instructions:
                    - Write the summary in a single cohesive paragraph.  
                    - Focus on professional trajectory, expertise, and key skills.  
                    - Keep the tone professional and objective.  

                    Generate the summary below:
                    """
        
        messages = [{"role": "user", "content": prompt}] 
        response = self.openai.chat.completions.create(model="gpt-4o-mini", messages=messages)
        with open("resume/summary.txt", "w", encoding="utf-8") as f:
            f.write(response.choices[0].message.content)


    def greeting(self):
        return f"Hello I'm {self.name} ai-self-resume!"
    
    def handle_tool_call(self, tool_calls):
        results = []
        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            print(f"Tool called: {tool_name}", flush=True)
            tool = globals().get(tool_name)
            result = tool(**arguments) if tool else {}
            results.append({"role": "tool","content": json.dumps(result),"tool_call_id": tool_call.id})
        return results

    def chat(self, message, history):
        messages = [{"role": "system", "content": self.systemPrompt()}] + history + [{"role": "user", "content": message}]
        done=False

        while not done:
            response = self.openai.chat.completions.create(model="gpt-4o-mini", messages=messages, tools=tools)
            if response.choices[0].finish_reason=="tool_calls":
                message = response.choices[0].message
                tool_calls = message.tool_calls
                results = self.handle_tool_call(tool_calls)
                messages.append(message)
                messages.extend(results)
            else:
                done = True

        return response.choices[0].message.content


if __name__ == "__main__":
    myself = Myself()
    bot = gr.Chatbot(
        type="messages",
        value=[{"role": "assistant", "content": myself.greeting()}]
    )
    gr.ChatInterface(myself.chat, chatbot=bot, type="messages").launch()