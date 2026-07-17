from fastapi import FastAPI
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from langchain_community.tools import DuckDuckGoSearchRun
from crewai import Agent, Task, Crew

load_dotenv()

app = FastAPI(title="My Basic Personal Agent")

search_tool = DuckDuckGoSearchRun()

agent = Agent(
    role="My Personal Assistant",
    goal="Help the user with any task as his duplicate",
    backstory="You are an exact digital copy of the user.",
    verbose=True,
    tools=[search_tool]
)

class UserTask(BaseModel):
    task: str

@app.post("/run")
async def run_task(user_task: UserTask):
    task = Task(
        description=user_task.task,
        agent=agent
    )
    crew = Crew(agents=[agent], tasks=[task], verbose=1)
    result = crew.kickoff()
    
    return {
        "status": "success",
        "result": str(result)
    }

@app.get("/")
async def home():
    return {"message": "✅ Basic Personal Agent is Ready!"}
