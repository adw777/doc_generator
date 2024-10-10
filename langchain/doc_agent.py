import os
import tempfile
from git import Repo
import ast
from github import Github
from docx import Document
# from langchain_community.llms import Groq
from langchain_groq import ChatGroq
from groq import Groq
from langchain.agents import initialize_agent, Tool
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate


# Set up your Groq API key
os.environ["GROQ_API_KEY"] = "groq_api_here"

# Set up your GitHub access token
github_token = "github_token_here"

def clone_repo(repo_url):
    with tempfile.TemporaryDirectory() as tmp_dir:
        Repo.clone_from(repo_url, tmp_dir)
        return tmp_dir

agent_executor = create_react_agent(llm, tools)
def analyze_code(repo_path):
    analysis = []
    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.endswith('.py'):
                with open(os.path.join(root, file), 'r') as f:
                    content = f.read()
                    try:
                        tree = ast.parse(content)
                        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
                        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
                        analysis.append(f"File: {file}")
                        analysis.append(f"Classes: {len(classes)}")
                        analysis.append(f"Functions: {len(functions)}")
                        analysis.append("")
                    except SyntaxError:
                        analysis.append(f"Error parsing {file}")
    return "\n".join(analysis)

def read_readme(repo_path):
    readme_path = os.path.join(repo_path, 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r') as f:
            return f.read()
    return "README not found"

def generate_documentation(repo_url, code_analysis, readme_content):
    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.7, max_tokens=None,
    timeout=None, max_retries=2)
    prompt = PromptTemplate(
        input_variables=["repo_url", "code_analysis", "readme_content"],
        template="""
        Generate comprehensive documentation for the GitHub repository at {repo_url}.
        Use the following code analysis: {code_analysis}
        And the README content: {readme_content}
        
        The documentation should include:
        1. An overview of the project
        2. Installation instructions
        3. Usage guide
        4. API documentation (if applicable)
        5. Code structure explanation
        6. Contributing guidelines
        
        Format the output in Markdown.
        """
    )
    chain = LLMChain(llm=llm, prompt=prompt)
    return chain.run(repo_url=repo_url, code_analysis=code_analysis, readme_content=readme_content)

def save_to_docx(content, output_file):
    doc = Document()
    doc.add_paragraph(content)
    doc.save(output_file)

def process_github_repo(repo_url):
    # Clone the repository
    repo_path = clone_repo(repo_url)
    
    # Analyze the code
    code_analysis = analyze_code(repo_path)
    
    # Read the README file
    readme_content = read_readme(repo_path)
    
    # Generate documentation
    documentation = generate_documentation(repo_url, code_analysis, readme_content)
    
    # Save documentation to a .docx file
    output_file = "repository_documentation.docx"
    save_to_docx(documentation, output_file)
    
    return output_file

# Set up the LangChain agent
llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.7)

tools = [
    Tool(
        name="Process GitHub Repository",
        func=process_github_repo,
        description="Takes a GitHub repository URL and generates documentation"
    )
]

agent = initialize_agent(tools, llm, agent="zero-shot-react-description", verbose=True)

# Use the agent to process a GitHub repository
repo_url = input("Enter the GitHub repository URL: ")
result = agent.run(f"Generate documentation for the GitHub repository at {repo_url}")

print(result)