from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time
from pipeline import AppForgePipeline
from evaluator import Evaluator

app = FastAPI(title="AppForge - AI App Compiler")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline = AppForgePipeline()
evaluator = Evaluator()


class GenerateRequest(BaseModel):
    prompt: str
    api_key: str


class EvaluateRequest(BaseModel):
    api_key: str


@app.get("/")
def root():
    return {"status": "AppForge backend running"}


@app.post("/generate")
async def generate(req: GenerateRequest):
    if not req.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")
    start = time.time()
    result = await pipeline.run(req.prompt, req.api_key)
    result["latency_seconds"] = round(time.time() - start, 2)
    return result


@app.post("/evaluate")
async def evaluate(req: EvaluateRequest):
    results = await evaluator.run(req.api_key)
    return results
