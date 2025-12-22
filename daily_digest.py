import feedparser
import google.generativeai as genai
import os
import requests # <--- New tool to talk to GitHub

# 1. SETUP: Keys & Tokens
API_KEY = os.environ.get("GEMINI_API_KEY")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN") # <--- New Key (Built-in)
REPO_NAME = os.environ.get("GITHUB_REPOSITORY") # <--- Gets "YourName/daily-news-bot"

genai.configure(api_key=API_KEY)

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
        print("✅ Draft saved to Issues tab!")
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
                summary_text = getattr(article, 'summary', '')[:500]
                
                # Check duplication (Optional optimization logic could go here)
                
                print(f"✅ Found: {article.title}")
                
                model = genai.GenerativeModel('gemini-2.0-flash')
                system_instruction = "You are a Salesforce Admin posting on LinkedIn. Keep it under 150 words. Be conversational. No lists."
                prompt = f"Write a LinkedIn post about: {article.title}. Summary: {summary_text}. Link: {article.link}"
                
                response = model.generate_content(system_instruction + prompt)
                draft_post = response.text
                
                # SAVE TO ISSUES
                issue_title = f"Draft: {article.title}"
                create_github_issue(issue_title, draft_post)
                return
                
        except Exception as e:
            print(f"⚠️ Error: {e}")

if __name__ == "__main__":
    run_bot()