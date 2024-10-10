import zipfile
import os
import docx2txt
import PyPDF2
import nbformat
import pandas as pd
import shutil

def extract_text_from_zip(zip_file_path):
    # Create a folder to extract files
    extract_folder = "extracted_text"
    os.makedirs(extract_folder, exist_ok=True)
    # print(f"Created folder: {extract_folder}")

    try:
        # Open the zip file
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            # Extract all files
            zip_ref.extractall(extract_folder)
            # print(f"Extracted files to: {extract_folder}")

            # Extract text from supported file types
            extracted_text = []
            for root, dirs, files in os.walk(extract_folder):
                for file in files:
                    file_path = os.path.join(root, file)

                    # Extract text from .docx files
                    if file.endswith(".docx"):
                        text = docx2txt.process(file_path)
                        extracted_text.append(text)

                    # Extract text from PDF files
                    elif file.endswith(".pdf"):
                        with open(file_path, "rb") as pdf_file:
                            pdf_reader = PyPDF2.PdfReader(pdf_file)
                            text = ""
                            for page_num in range(len(pdf_reader.pages)):
                                page = pdf_reader.pages[page_num]
                                text += page.extract_text()
                        extracted_text.append(text)

                    # Extract code and markdown from .ipynb files
                    elif file.endswith(".ipynb"):
                        with open(file_path, "r", encoding="utf-8") as notebook_file:
                            notebook_content = nbformat.read(notebook_file, as_version=4)
                            for cell in notebook_content['cells']:
                                if cell['cell_type'] == 'code':
                                    extracted_text.append(cell['source'])
                                elif cell['cell_type'] == 'markdown':
                                    extracted_text.append(cell['source'])

                    # Extract text from .py, .txt, .csv, and other text files
                    elif file.endswith((".py", ".txt", ".csv", ".cpp")):
                        if file.endswith(".csv"):
                            # Use pandas to read CSV content
                            csv_content = pd.read_csv(file_path)
                            text = csv_content.to_string(index=False)
                        else:
                            # Read text from other text files
                            with open(file_path, "r", encoding="utf-8") as text_file:
                                text = text_file.read()
                        extracted_text.append(text)

                    # Add more conditions for other file types as needed

    except Exception as e:
        print(f"Error during extraction: {e}")
        extracted_text = []  # Reset the list in case of an error

    # Clean up: Remove the temporary extraction folder
    try:
        shutil.rmtree(extract_folder)
        # print(f"Removed folder: {extract_folder}")
    except Exception as e:
        print(f"Error during cleanup: {e}")

    return extracted_text



zip_file_path = "segmentation_and_analysis-main.zip"
text_from_zip = extract_text_from_zip(zip_file_path)

"""
for idx, text in enumerate(text_from_zip, start=1):
    print(f"Text from file {idx}:\n{text}\n{'='*40}")
"""