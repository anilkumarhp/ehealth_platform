from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import logging
import os
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(
    title="eHealth LLM Service",
    description="API for the eHealth LLM Service",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Model configuration
MODEL_NAME = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Global variables for model and tokenizer
model = None
tokenizer = None
generator = None

class CompletionRequest(BaseModel):
    prompt: str
    max_tokens: int = 256
    temperature: float = 0.7
    system_prompt: str = "You are a helpful healthcare assistant for an eHealth platform. Provide accurate and helpful information about healthcare topics."

class CompletionResponse(BaseModel):
    text: str

def format_prompt(system_prompt, user_prompt):
    """Format the prompt for the model."""
    return f"<s>[INST] {system_prompt}\n\n{user_prompt} [/INST]"

def load_model():
    """Load the model and tokenizer."""
    global model, tokenizer, generator
    
    logger.info(f"Loading model {MODEL_NAME} on {DEVICE}...")
    start_time = time.time()
    
    try:
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            torch_dtype=torch.float32,
            low_cpu_mem_usage=True,
            device_map=DEVICE
        )
        
        generator = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            device=DEVICE if DEVICE == "cuda" else -1
        )
        
        logger.info(f"Model loaded successfully in {time.time() - start_time:.2f} seconds")
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        raise e

@app.on_event("startup")
async def startup_event():
    """Load the model on startup."""
    background_tasks = BackgroundTasks()
    background_tasks.add_task(load_model)
    
    # Start loading the model in the background
    load_model()

@app.post("/v1/completions", response_model=CompletionResponse)
async def generate_completion(request: CompletionRequest):
    """Generate a completion for the given prompt."""
    global model, tokenizer, generator
    
    if model is None or tokenizer is None or generator is None:
        raise HTTPException(status_code=503, detail="Model is still loading, please try again later")
    
    try:
        # Format the prompt
        formatted_prompt = format_prompt(request.system_prompt, request.prompt)
        
        # Generate the completion
        outputs = generator(
            formatted_prompt,
            max_new_tokens=request.max_tokens,
            temperature=request.temperature,
            do_sample=True,
            top_p=0.95,
            top_k=50,
            repetition_penalty=1.1
        )
        
        # Extract the generated text
        generated_text = outputs[0]["generated_text"]
        
        # Remove the prompt from the generated text
        response_text = generated_text[len(formatted_prompt):]
        
        # Clean up the response
        response_text = response_text.strip()
        
        return CompletionResponse(text=response_text)
    except Exception as e:
        logger.error(f"Error generating completion: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating completion: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    if model is None or tokenizer is None:
        return {"status": "loading", "model": MODEL_NAME, "device": DEVICE}
    return {"status": "ready", "model": MODEL_NAME, "device": DEVICE}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8008)