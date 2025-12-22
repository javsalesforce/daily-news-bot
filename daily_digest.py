import feedparser
import google.generativeai as genai
import datetime
import os

# 1. SETUP: Connect to the AI Brain securely
# This looks for the key in GitHub Secrets instead of the file
API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    print("❌ Error: No API Key found. Make sure it's set in GitHub Secrets.")
    exit()

genai.configure(api_key=API_KEY)

# 2. SETUP: The Sources
feeds = [
    "https://admin.salesforce.com/feed",
    "https://www.salesforceben.com/feed/",
    "https://unofficialsf.com/feed/",
]

# 3. THE "REAL HUMAN" PERSONA
system_instruction = """
You are a Salesforce Admin with years of experience. You are posting on LinkedIn.
Your goal is to sound like a real person, not a corporate press release.

CRITICAL RULES:
1. NO numbered lists. NO bullet points. NO headers.
2. Do NOT summarize the article. Assume the reader can read the title.
3. Instead, share a specific OPINION or REACTION. Why does this actually matter to an Admin's daily work?
4. Use a natural, conversational tone. You can be critical or cautious.
5. Start directly with your thought. Do not say "Here is a post."
6. Keep it under 150 words.

Structure:
- A strong opening sentence about the topic.
- A middle sentence adding your personal perspective or a warning.
- End with a question to start a debate.
- Put the link on a new line at the very bottom.
"""

# 4. THE LOGIC
def generate_commentary():
    print("🔍 Reading feeds...")
    
    for url in feeds:
        try:
            news_data = feedparser.parse(url)
            if news_data.entries:
                article = news_data.entries[0]
                summary_text = getattr(article, 'summary', '')[:500]
                
                print(f"✅ Found: {article.title}")
                print("🧠 Writing natural post...")
                
                model = genai.GenerativeModel('gemini-2.0-flash')
                
                prompt = f"""
                Read this article summary and write a LinkedIn post about it.
                Title: {article.title}
                Summary: {summary_text}
                Link: {article.link}
                """
                
                response = model.generate_content(system_instruction + prompt)
                
                # Clean Output
                print("\n" + response.text + "\n")
                return 
                
        except Exception as e:
            print(f"⚠️ Error: {e}")

if __name__ == "__main__":
    generate_commentary()