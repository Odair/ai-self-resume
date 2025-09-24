from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader

load_dotenv(override=True)


class Myself:

    def __init__(self):
        self.openai = OpenAI()
        self.name= 'Odair'
        reader = PdfReader("resume/profile.pdf")
        self.linkedin = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                self.linkedin += text
        
        self.generateSummary()
        
        with open("resume/summary.txt", "r", encoding="utf-8") as f:
            self.summary = f.read()


    def generateSummary(self):
        prompt = f"You act as curriculum resumer. You will receive a likendin professional profile and must summary it \
            focus on professional details and skills, don't need to summarize email and linkedin profile. \
            \n\n ### Profile: {self.linkedin}. With this context generate a summary, the output should be a paragraph"
        
        messages = [{"role": "user", "content": prompt}] 
        response = self.openai.chat.completions.create(model="gpt-4o-mini", messages=messages)
        with open("resume/summary.txt", "w", encoding="utf-8") as f:
            f.write(response.choices[0].message.content)


    def greeting(self):
        print(f"Hello I'm {self.name} ai-self-resume!")


if __name__ == "__main__":
    mysel = Myself()
