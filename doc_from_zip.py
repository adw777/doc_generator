import os
import groq
import markdown
from html import escape
from extractFromZip import extract_text_from_zip

def generate_documentation(content):
    client = groq.Groq()
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a technical writer tasked with creating comprehensive, beginner-friendly documentation for a programming project. Analyze the provided content and generate detailed documentation that explains the project's purpose, structure, and functionality. Use clear language and provide examples where appropriate. Structure the documentation with headings and subheadings for better readability."
            },
            {
                "role": "user",
                "content": f"Here's the content of a programming project. Please generate detailed, beginner-friendly documentation for it:\n\n{content}"
            }
        ],
        model="llama-3.1-8b-instant",
    )
    return chat_completion.choices[0].message.content

def save_documentation(documentation, filename):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(documentation)

def create_html_page(documentation, filename):
    html_content = markdown.markdown(documentation)
    page_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Doc From Zip file</title>
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
    with open(filename, "w", encoding="utf-8") as f:
        f.write(page_content)

def get_next_file_number():
    i = 1
    while os.path.exists(f"doc_zip{i}.txt") or os.path.exists(f"doc_zip{i}.html"):
        i += 1
    return i

def main():
    # Get the zip file path
    zip_file_path = input("Enter the path to the zip file: ")

    # Extract text from the zip file
    extracted_text = extract_text_from_zip(zip_file_path)

    # Combine all extracted text into a single string
    combined_text = "\n\n".join(extracted_text)

    # Generate documentation
    documentation = generate_documentation(combined_text)

    # Get the next available file number
    file_number = get_next_file_number()

    # Save documentation as text file
    txt_filename = f"doc_zip{file_number}.txt"
    save_documentation(documentation, txt_filename)
    print(f"Documentation saved as {txt_filename}")

    # Create and save HTML documentation
    html_filename = f"doc_zip{file_number}.html"
    create_html_page(documentation, html_filename)
    print(f"HTML documentation saved as {html_filename}")

if __name__ == "__main__":
    main()