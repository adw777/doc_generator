import os
import json
import requests
from groq import Groq
from datetime import datetime
import sqlite3

# Initialize Groq client
client = Groq(api_key=os.environ["GROQ_API_KEY"])

# External tools
def get_weather(location):
    try:
        api_key = os.environ["OPENWEATHERMAP_API_KEY"]
        url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"
        response = requests.get(url)
        data = response.json()
        return f"The current temperature in {location} is {data['main']['temp']}°C"
    except Exception as e:
        return f"Error getting weather for {location}: {str(e)}"

def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Data storage and retrieval
def init_db():
    conn = sqlite3.connect('agent_memory.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS memory
                 (key TEXT PRIMARY KEY, value TEXT)''')
    conn.commit()
    conn.close()

def store_data(key, value):
    conn = sqlite3.connect('agent_memory.db')
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO memory (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()
    return f"Data stored with key: {key}"

def retrieve_data(key):
    conn = sqlite3.connect('agent_memory.db')
    c = conn.cursor()
    c.execute("SELECT value FROM memory WHERE key=?", (key,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else f"No data found for key: {key}"

# Function calling
def execute_function(func_name, args):
    function_map = {
        "get_weather": get_weather,
        "get_current_time": get_current_time,
        "store_data": store_data,
        "retrieve_data": retrieve_data
    }
    
    if func_name not in function_map:
        return f"Function {func_name} not found"
    
    function = function_map[func_name]
    
    try:
        if func_name == "get_weather":
            return function(args.get("location", ""))
        elif func_name == "get_current_time":
            return function()
        elif func_name == "store_data":
            return function(args.get("key", ""), args.get("value", ""))
        elif func_name == "retrieve_data":
            return function(args.get("key", ""))
    except Exception as e:
        return f"Error executing {func_name}: {str(e)}"

# Agent class
class SimpleAgent:
    def __init__(self):
        self.conversation_history = []
        init_db()

    def run(self, user_input):
        self.conversation_history.append(f"Human: {user_input}")
        
        prompt = f"""You are a helpful AI assistant. Based on the conversation history and the user's input, determine if you need to call any functions to complete the task. If so, return a JSON object with the function name and arguments. If not, provide a direct response.

Conversation history:
{' '.join(self.conversation_history)}

Available functions:
- get_weather(location: str)
- get_current_time()
- store_data(key: str, value: str)
- retrieve_data(key: str)

User input: {user_input}

Response (either a JSON object for function call or a direct answer):"""

        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.7,
            )

            assistant_response = response.choices[0].message.content.strip()
            
            try:
                func_call = json.loads(assistant_response)
                if isinstance(func_call, dict) and ("function" in func_call or "function_name" in func_call):
                    function_name = func_call.get("function") or func_call.get("function_name")
                    arguments = func_call.get("arguments") or func_call.get("function_args", {})
                    
                    result = execute_function(function_name, arguments)
                    self.conversation_history.append(f"Assistant: {result}")
                    return result
            except json.JSONDecodeError:
                # If it's not a valid JSON, treat it as a direct response
                if assistant_response.lower().startswith("since the user asked for the current time"):
                    result = execute_function("get_current_time", {})
                    self.conversation_history.append(f"Assistant: {result}")
                    return result
                else:
                    self.conversation_history.append(f"Assistant: {assistant_response}")
                    return assistant_response

        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            self.conversation_history.append(f"Assistant: {error_message}")
            return error_message

# Example usage
agent = SimpleAgent()

while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        break
    response = agent.run(user_input)
    print(f"Assistant: {response}")