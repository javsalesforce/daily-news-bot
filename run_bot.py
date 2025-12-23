import feedparser
import google.generativeai as genai
import os
import requests

# 1. SETUP: Keys & Tokens
API_KEY = os.environ.get("GEMINI_API_KEY")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN") 
REPO_NAME = os.environ.get("GITHUB_REPOSITORY") 

genai.configure(api_key=API_KEY)

feeds = [
    "https://admin.salesforce.com/feed",
    "https://www.salesforceben.com/feed/",
    "https://unofficialsf.com/feed/",
]

# 2. HELPER: Memory - Check if we already posted this
def get_posted_titles():
    url = f"https://api.github.com/repos/{REPO_NAME}/issues?state=all&per_page=100"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        issues = response.json()
        return [issue['title'] for issue in issues]
    else:
        print("⚠️ Could not fetch history. Assuming everything is new.")
        return []

# 3. FUNCTION: Create a new "Ticket"
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

# 4. THE MAIN LOGIC
def run_bot():
    print("🔍 Checking history...")
    existing_titles = get_posted_titles()
    
    print("🔍 Reading feeds...")
    for url in feeds:
        try:
            news_data = feedparser.parse(url)
            
            for article in news_data.entries:
                potential_title = f"Draft: {article.title}"
                
                # CHECK: Have we seen this before?
                if potential_title in existing_titles:
                    print(f"✋ Skipping (Already posted): {article.title}")
                    continue 
                
                # If we get here, it is NEW!
                summary_text = getattr(article, 'summary', '')[:1000]
                print(f"✅ Found New Article: {article.title}")
                print("🧠 Writing deep analysis...")
                
                model = genai.GenerativeModel('gemini-2.0-flash')
                
                # --- VETERAN ARCHITECT PERSONA (FULL DETAILED VERSION) ---
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
                
                response = model.generate_content(system_instruction + prompt)
                
                # --- LINK ADDITION ---
                # We append the link manually to ensure it is always there.
                final_post = f"{response.text}\n\nRead the full article here: {article.link}"
                
                create_github_issue(potential_title, final_post)
                
                # STOP after finding ONE new article
                return 
                
        except Exception as e:
            print(f"⚠️ Error reading feed {url}: {e}")

if __name__ == "__main__":
    run_bot()
