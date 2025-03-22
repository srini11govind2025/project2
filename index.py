from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
import subprocess
import requests
import hashlib
import json
import datetime
import pandas as pd
from bs4 import BeautifulSoup
from typing import Optional

app = FastAPI()

@app.get("/")
def home():
    return {"message": "IITM Tools API is running!"}

# Define the request model
class QueryRequest(BaseModel):
    question: str

# Utility Functions

def is_vscode_installed():
    """Check if VS Code is installed."""
    try:
        subprocess.run(["code", "-v"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except:
        return False

def hash_string(value: str):
    """Return SHA-256 hash of a string."""
    return hashlib.sha256(value.encode()).hexdigest()

def count_wednesdays(start_date, end_date):
    """Count the number of Wednesdays in a date range."""
    return sum(1 for d in range((end_date - start_date).days + 1)
               if (start_date + datetime.timedelta(days=d)).weekday() == 2)

def extract_hidden_value(html: str, input_id: str):
    """Extract value from a hidden input field in HTML."""
    soup = BeautifulSoup(html, "html.parser")
    element = soup.find("input", {"id": input_id})
    return element["value"] if element else "Not found"

def get_github_latest_commit(repo_url: str):
    """Fetch the latest commit hash from GitHub API."""
    try:
        response = requests.get(f"{repo_url}/commits")
        response.raise_for_status()
        commits = response.json()
        return commits[0]["sha"] if commits else "No commits found"
    except requests.RequestException as e:
        return f"Error fetching commits: {str(e)}"

# API Endpoints

@app.post("/answer")
async def answer_query(request: QueryRequest):
    question = request.question.lower().strip()

    match question:
        case "vscode installed":
            return {"answer": "VS Code is installed" if is_vscode_installed() else "VS Code is not installed"}

        case "prettier hash":
            return {"answer": hash_string("prettier@3.4.2 README.md")}

        case "excel sequence":
            return {"answer": "SEQUENCE(2,3,100,10)"}

        case "count wednesdays":
            return {"answer": count_wednesdays(datetime.date(2023, 1, 1), datetime.date(2023, 12, 31))}

        case "hidden input":
            html_content = '<input type="hidden" id="csrf_token" value="123abc">'
            return {"answer": extract_hidden_value(html_content, "csrf_token")}

        case "sort json":
            data = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}, {"name": "Charlie", "age": 25}]
            sorted_data = sorted(data, key=lambda x: (x["age"], x["name"]))
            return {"answer": sorted_data}

        case "hash json":
            transformed = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
            return {"answer": hash_string(json.dumps(transformed))}

        case "html parse":
            html = "<p>Hello, <b>world</b>!</p>"
            soup = BeautifulSoup(html, "html.parser")
            return {"answer": soup.get_text()}

        case "github repo exists":
            repo_url = "https://github.com/your-username/your-repo"
            return {"answer": "Repository exists"} if requests.get(repo_url).status_code == 200 else {"answer": "Repository not found"}

        case "github latest commit":
            return {"answer": get_github_latest_commit("https://api.github.com/repos/your-username/your-repo")}

        case _:
            return {"answer": "Question not recognized"}

# File Upload Handling

@app.post("/sum-csv/")
async def sum_csv(file: UploadFile = File(...)):
    """Compute the sum of the second column from an uploaded CSV file."""
    try:
        df = pd.read_csv(file.file)
        if df.shape[1] < 2:
            return {"error": "CSV must have at least two columns"}
        return {"answer": df.iloc[:, 1].sum()}
    except Exception as e:
        return {"error": f"Error processing CSV: {str(e)}"}

@app.post("/max-csv/")
async def max_csv(file: UploadFile = File(...)):
    """Get the max value from the second column of an uploaded CSV file."""
    try:
        df = pd.read_csv(file.file)
        if df.shape[1] < 2:
            return {"error": "CSV must have at least two columns"}
        return {"answer": df.iloc[:, 1].max()}
    except Exception as e:
        return {"error": f"Error processing CSV: {str(e)}"}

@app.post("/markdown-extract/")
async def extract_markdown_header(file: UploadFile = File(...)):
    """Extract the first line from an uploaded Markdown file."""
    try:
        text = (await file.read()).decode("utf-8").strip()
        return {"answer": text.split("\n")[0] if text else "Empty file"}
    except Exception as e:
        return {"error": f"Error reading markdown file: {str(e)}"}

# Debugging Endpoint

@app.get("/questions/")
def get_sample_questions():
    """List sample queries for testing."""
    return {
        "sample_queries": [
            "vscode installed",
            "prettier hash",
            "sum csv",
            "count wednesdays",
            "sort json",
            "github latest commit",
            "max csv"
        ]
    }
from mangum import Mangum

handler = Mangum(app)
