import requests
from bs4 import BeautifulSoup
from groq import Groq
import os

def parse_webpage(url):
    """
    Take the URL link, parse the complete page, and return the parsed text.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        text = soup.get_text()
        # Break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # Break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # Drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)
        return text
    except requests.RequestException as e:
        print(f"An error occurred while fetching the webpage: {e}")
        return None

def generate_documentation(text):
    """
    Take the parsed text and return a detailed documentation of the text using Groq.
    """
    client = Groq(api_key="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")
    
    prompt = f"""
    Please provide a detailed documentation of the following text. Include:
    1. A summary of the main topics or themes
    2. Key points or important information
    3. Any notable features or characteristics of the content
    4. Suggestions for further exploration or related topics

    Text to analyze:
    {text[:4000]}  # Limiting to 4000 characters to avoid token limits
    """

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama-3.1-8b-instant",
            temperature=0.5,
            max_tokens=1000,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"An error occurred while generating documentation: {e}")
        return None

def save_documentation(documentation):
    """
    Save the generated documentation to a text file.
    """
    i = 1
    while os.path.exists(f"doc{i}.txt"):
        i += 1
    filename = f"doc{i}.txt"
    
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(documentation)
        print(f"Documentation saved to {filename}")
    except IOError as e:
        print(f"An error occurred while saving the file: {e}")

def main(repo_url):
    """
    Main function to parse a webpage, generate documentation, and save it to a file.
    """
    parsed_text = parse_webpage(repo_url)
    if parsed_text:
        documentation = generate_documentation(parsed_text)
        if documentation:
            #print("Detailed Documentation:")
            #print(documentation)
            save_documentation(documentation)
        else:
            print("Failed to generate documentation.")
    else:
        print("Failed to parse the webpage.")

if __name__ == "__main__":
    repo_url = input("Enter the URL of the repository: ")
    main(repo_url)



