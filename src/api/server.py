from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import logging
import os
from dotenv import load_dotenv
from param_mem.memory.parametric import ParametricMemory
from param_mem.memory.retrieval import CrossSampleMemory
from param_mem.agent.agent_loop import ParamAgent
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Load environment variables
load_dotenv(override=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="ParamMem Agent API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for modules
memory_module = None
retrieval_module = None
agent = None

class SolveRequest(BaseModel):
    problem: str
    max_iterations: int = 3
    use_param_plus: bool = True

@app.on_event("startup")
async def startup_event():
    global memory_module, retrieval_module, agent
    logger.info("Initializing ParamMem Engine...")
    
    provider = os.getenv("MODEL_PROVIDER", "local").lower()
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    model_id = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
    
    if api_key:
        logger.info(f"GROQ_API_KEY detected (starts with {api_key[:5]}...)")
    else:
        logger.warning("GROQ_API_KEY not found in environment!")

    base_model = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
    lora_path = "./param_mem_lora"
    if not os.path.exists(lora_path) or not os.listdir(lora_path):
        lora_path = None
    
    try:
        if provider == "groq" and api_key:
            logger.info("Using Groq API provider...")
            memory_module = ParametricMemory(
                provider="groq", 
                api_key=api_key, 
                model_id=model_id
            )
        else:
            logger.info("Using local HuggingFace provider...")
            memory_module = ParametricMemory(
                base_model_name=base_model, 
                lora_path=lora_path, 
                provider="local"
            )
            
        retrieval_module = CrossSampleMemory()
        agent = ParamAgent(memory_module=memory_module, retrieval_module=retrieval_module)
        logger.info(f"ParamMem Engine ready (Provider: {provider}).")
    except Exception as e:
        logger.error(f"Failed to initialize models: {e}")
        agent = None 

@app.post("/solve")
async def solve_problem(req: SolveRequest):
    if not agent:
        raise HTTPException(status_code=503, detail="Agent is not initialized. Please check server logs.")
        
    try:
        # Note: In a production app, we wouldn't re-instantiate the agent per request
        # but for this demo it allows toggling retrieval.
        current_retrieval = retrieval_module if req.use_param_plus else None
        
        # We can reuse the memory_module but might need a new agent instance if retrieval toggles
        # For simplicity, we just use the global agent if it matches req.use_param_plus
        # but the solve_task doesn't currently care about toggling retrieval internally easily.
        # Let's just pass the requirement to the solve_task if possible, 
        # but the current agent class has it fixed.
        
        # Temporary fix for demo:
        temp_agent = ParamAgent(memory_module=memory_module, retrieval_module=current_retrieval)
        result = temp_agent.solve_task(req.problem, max_iterations=req.max_iterations)
        return result
    except Exception as e:
        logger.error(f"Error during solving: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {
        "status": "ok", 
        "agent_loaded": agent is not None,
        "provider": os.getenv("MODEL_PROVIDER", "local")
    }

# Mount static files (React frontend)
# Ensure this is after all API routes
if os.path.exists("dist"):
    app.mount("/", StaticFiles(directory="dist", html=True), name="static")
else:
    logger.warning("Dist directory not found. Frontend will not be served.")

if __name__ == "__main__":
    uvicorn.run("src.api.server:app", host="0.0.0.0", port=8000, reload=True)
