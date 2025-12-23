import feedparser
import google.generativeai as genai
import os
import requests

# 1. SETUP: Keys & Tokens
API_KEY = os.environ.get("GEMINI_API_KEY")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN") 
REPO_NAME = os.environ.get("GITHUB_REPOSITORY") 

# Configure the AI model
genai.configure(api_key=API_KEY)

# List of Salesforce News Feeds
feeds = [
    "https://admin.salesforce.com/feed",
    "https://www.salesforceben.com/feed/",
    "https://unofficialsf.com/feed/",
]

# 2. FUNCTION: Create a "Ticket" (Issue) in GitHub
def create_github_issue(title, body):
    url = f"https://api.github.com/repos/{REPO_NAME}/issues"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {"title": title, "body": body}
    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code == 201:
        print("✅ SUCCESS: Draft saved to Issues tab!")
    else:
        print(f"❌ Error creating issue: {response.text}")

# 3. THE LOGIC
def run_bot():
    print("🔍 Reading feeds...")
    
    for url in feeds:
        try:
            news_data = feedparser.parse(url)
            if news_data.entries:
                article = news_data.entries[0]
                
                # Grab the summary so the AI has context
                summary_text = getattr(article, 'summary', '')[:1000]
                
                print(f"✅ Found: {article.title}")
                print("🧠 Writing deep analysis...")
                
                model = genai.GenerativeModel('gemini-2.0-flash')
                
                # --- UPDATED PERSONALITY: VETERAN ARCHITECT ---
                system_instruction = """
                You are a veteran Salesforce Architect with deep technical expertise.
                You are writing a thoughtful LinkedIn post to share high-value analysis with your network.

                YOUR GOAL:
                - Do not just report the news; analyze the STRATEGIC IMPACT.
                - Discuss the "Why" and the "So What." How does this affect technical debt, security, or user adoption?
                - Write 2-3 substantial paragraphs. Do not be brief.
                - It is okay to be skeptical or point out potential risks (e.g., "This looks great, but watch out for...").

                TONE:
                - Professional, authoritative, and nuanced.
                - Use "I" statements ("I believe...", "In my experience...").
                - No "sales fluff" or exclamation points.

                STRUCTURE:
                - Paragraph 1: The Context (What is happening and why it matters).
                - Paragraph 2: The Deep Dive (Your expert critique or advice).
                - Paragraph 3: The Interaction (Ask a specific, hard question).
                """
                
                prompt = f"""
                Write a LinkedIn post about this article.
                
                Title: {article.title}
                Summary: {summary_text}
                Link: {article.link}
                """
                
                # Generate content
                response = model.generate_content(system_instruction + prompt)
                draft_post = response.text
                
                # 4. SAVE TO ISSUES
                issue_title = f"Draft: {article.title}"
                create_github_issue(issue_title, draft_post)
                return 
                
        except Exception as e:
            print(f"⚠️ Error reading feed {url}: {e}")

if __name__ == "__main__":
    run_bot()