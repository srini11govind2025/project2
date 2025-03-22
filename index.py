from fastapi import FastAPI, Form, UploadFile, File
import subprocess
app = FastAPI()

@app.get("/")
def home():
    return {"message": "IITM Tools API is running!"}
@app.post("/")
@app.post("/api/")
async def answer_question(
    question: str = Form(...),
    file: UploadFile = File(None)
):
    #GA1: Q1 VSCODE
    if "code" in question:
        try:
            # Identify the command from the question
            parts = question.split(" ")
            command = ["code"]
            if len(parts) > 1:
                command.extend(parts[1:])  # Extract arguments after "code"

            # Execute the command and capture the output
            result = subprocess.run(command, capture_output=True, text=True)
            output = result.stdout.strip() if result.returncode == 0 else result.stderr.strip()
        except Exception as e:
            output = f"Error executing command: {str(e)}"
    else:
        output = "Invalid question. Expected a VS Code command."

    return {"answer": output}



