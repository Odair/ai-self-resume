from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader
import gradio as gr

load_dotenv(override=True)


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
                    - If the user shows genuine interest or starts a conversation, guide them toward leaving their email.  
                    - Politely ask for their email.  
                    - Record it using the `record_user_details` tool.  

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

    def chat(self, message, history):
        messages = [{"role": "system", "content": self.systemPrompt()}] + history + [{"role": "user", "content": message}]
        response = self.openai.chat.completions.create(model="gpt-4o-mini", messages=messages)
        return response.choices[0].message.content


if __name__ == "__main__":
    myself = Myself()
    bot = gr.Chatbot(
        type="messages",
        value=[{"role": "assistant", "content": myself.greeting()}]
    )
    gr.ChatInterface(myself.chat, chatbot=bot, type="messages").launch()