import requests
from bs4 import BeautifulSoup
import os
import groq
from http.server import HTTPServer, SimpleHTTPRequestHandler
import webbrowser
import re
import markdown

def fetch_github_content(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f"Failed to fetch content from {url}")

def parse_github_content(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    # This is a simplified parsing. You may need to adjust based on GitHub's actual structure
    content = soup.find('div', {'class': 'repository-content'})
    return content.get_text() if content else ""

def generate_documentation(content):
    client = groq.Groq()
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a technical writer tasked with creating comprehensive documentation for a GitHub project. Analyze the provided content and generate detailed documentation that explains the project's purpose, structure, and functionality. Use Markdown formatting for better readability."
            },
            {
                "role": "user",
                "content": f"Here's the content of a GitHub repository. Please generate detailed documentation for it:\n\n{content}"
            }
        ],
        model="llama-3.1-8b-instant",
    )
    return chat_completion.choices[0].message.content

def clean_documentation(raw_doc):
    # Remove GitHub-specific formatting
    cleaned = re.sub(r'```[\s\S]*?```', '', raw_doc)  # Remove code blocks
    cleaned = re.sub(r'`(.*?)`', r'\1', cleaned)  # Remove inline code formatting
    cleaned = re.sub(r'#{1,6}\s', '', cleaned)  # Remove heading indicators
    cleaned = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', cleaned)  # Remove links, keep text
    cleaned = re.sub(r'!\[.*?\]\(.*?\)', '', cleaned)  # Remove images
    cleaned = re.sub(r'[\*_]{1,2}(.*?)[\*_]{1,2}', r'\1', cleaned)  # Remove bold/italic
    cleaned = re.sub(r'- ', '• ', cleaned)  # Replace dashes with bullets
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)  # Reduce multiple newlines
    return cleaned.strip()

def save_documentation(documentation, filename):
    with open(filename, "w") as f:
        f.write(documentation)

def create_html_page(documentation, filename):
    html_content = markdown.markdown(documentation)
    page_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Project Documentation</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }}
            h1, h2, h3 {{ color: #2c3e50; }}
            code {{
                background-color: #f7f7f7;
                padding: 2px 4px;
                border-radius: 4px;
                font-family: Consolas, monospace;
            }}
            pre {{
                background-color: #f7f7f7;
                padding: 15px;
                border-radius: 5px;
                overflow-x: auto;
            }}
            a {{ color: #3498db; }}
            ul, ol {{ padding-left: 25px; }}
        </style>
    </head>
    <body>
        <h1>Project Documentation</h1>
        {html_content}
    </body>
    </html>
    """
    with open(filename, "w") as f:
        f.write(page_content)

def start_local_server():
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print("Server started at http://localhost:8000")
    webbrowser.open('http://localhost:8000/documentation.html')
    httpd.serve_forever()

def get_next_file_number():
    i = 1
    while os.path.exists(f"doc_url{i}.txt") or os.path.exists(f"doc_url{i}.html"):
        i += 1
    return i

def main():
    github_url = input("Enter the GitHub repository URL: ")
    
    try:
        html_content = fetch_github_content(github_url)
        parsed_content = parse_github_content(html_content)
        raw_documentation = generate_documentation(parsed_content)
        cleaned_documentation = clean_documentation(raw_documentation)
        
        file_number = get_next_file_number()
        txt_filename = f"doc_url{file_number}.txt"
        html_filename = f"doc_url{file_number}.html"
        
        save_documentation(cleaned_documentation, txt_filename)
        create_html_page(cleaned_documentation, html_filename)
        
        print(f"Documentation saved as {txt_filename} and {html_filename}")
        # Uncomment the following line if you want to start the local server
        # start_local_server()
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()