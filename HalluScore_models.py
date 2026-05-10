import torch
import re
import openai
import together
from transformers import AutoModelForCausalLM, AutoTokenizer
from huggingface_hub import login
import os
from huggingface_hub import login
import os
import anthropic


MODEL_MAP = {
    # Hugging Face models
    "Jais-6.7b": "inceptionai/jais-family-6p7b",
    "Noon": "Naseej/noon-7b",
    "Allam": "ALLaM-AI/ALLaM-7B-Instruct-preview",
    "Fanar": "QCRI/Fanar-1-9B",

    # OpenAI models
    "openai:gpt-4o": "openai",
    "openai:gpt-o3": "openai",
    "openai:gpt-5":"openai",
    "openai:o4-mini":"openai",


    # Together AI models
    "together:deepseek-v3": "deepseek-ai/DeepSeek-V3",
    "together:deepseek-r1": "deepseek-ai/DeepSeek-R1",
    "together:llama4-Maverick": "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
    "together:qwen3":"Qwen/Qwen3-235B-A22B-Instruct-2507-tput",
    "together:kimi":"moonshotai/Kimi-K2-Instruct-0905",
    "together:qwen3_2":"Qwen/Qwen3-Next-80B-A3B-Instruct",
    


    "claude:opus":"claude-opus-4-20250514",
    "claude:sonnet":"claude-sonnet-4-5-20250929",

    "grok:grok4":"grok-4-fast-non-reasoning",
    "grok:grok4_reasoning":"grok-4-fast-reasoning",

    "google:gemenipro":"gemini-2.5-pro",
    "google:gemeniflash":"gemini-2.5-flash"


}


def load_model_and_tokenizer(model_key):
    if model_key.startswith("openai") or model_key.startswith("together") or model_key.startswith("claude") or model_key.startswith("grok") or model_key.startswith("google"):
        return None, None, None  # No local model/tokenizer needed
    model_name = MODEL_MAP[model_key]
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True,return_tensors='pt', return_token_type_ids=False)
    model = AutoModelForCausalLM.from_pretrained(model_name, trust_remote_code=True)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if tokenizer.pad_token is None:
      tokenizer.add_special_tokens({'pad_token': '[PAD]'})
      model.resize_token_embeddings(len(tokenizer))

    model.config.pad_token_id = tokenizer.pad_token_id
    return model.to(device), tokenizer, device
