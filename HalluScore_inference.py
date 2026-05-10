import torch
import re
import openai
import together
from models import MODEL_MAP
import anthropic
from together import Together
import os

from xai_sdk import Client
from xai_sdk.chat import user, system

def get_response(prompt, model, tokenizer, device, model_key, task="summarization", debug=True):
    try:
        # OpenAI models
        if model_key.startswith("openai"):
            model_name = (
                "gpt-4o" if "gpt-4o" in model_key else
                "gpt-4" if "gpt-4" in model_key else
                "gpt-5" if "gpt-5" in model_key else
                "o4-mini" if "o4-mini" in model_key else
                "gpt-3.5-turbo"
            )
            response = openai.ChatCompletion.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                #temperature=0.0
            )
            decoded = response["choices"][0]["message"]["content"].strip()
#together.Complete.create
        # Together AI models
        elif model_key.startswith("together"):
            model_name = MODEL_MAP[model_key]
            client = Together(api_key="")
            response = client.chat.completions.create(
                model=model_name,
                messages=  [{
                "role": "user",
                "content": prompt}],
                max_tokens=3000,
                temperature=0.0,
                repetition_penalty=1.2)
            decoded = response.choices[0].message.content.strip()
            #decoded = response.choices[0].message.content.strip()
            #decoded = response['choices'][0]['text'].strip()
            if debug:
                print(f"[Together AI response]: {decoded}")
            '''response = together.Complete.create(
                prompt=prompt,
                model=model_name,
                max_tokens=512,
                temperature=0.0,
                repetition_penalty=1.2
            )
            #decoded = response.choices[0].message.content.strip()
            decoded = response["choices"][0]["text"].strip()
            if debug:
                print(f"[Together AI response]: {decoded}")'''
        elif model_key.startswith("claude"):
            client = anthropic.Anthropic(
    api_key= "")
            model_name = MODEL_MAP[model_key]
            response = client.messages.create(
                 messages=[
        {"role": "user", "content": prompt}],
                model=model_name,
                max_tokens=250,
                temperature=0.0,
            )
            decoded = response.content[0].text.strip()
            if debug:
                print(f"[Claude AI response]: {decoded}")
        # Hugging Face models
                # Grok (xAI) models
        elif model_key.startswith("grok"):
            client = Client(
                api_key=os.getenv("XAI_API_KEY"),
                timeout=3600,  # long timeout for reasoning models
            )

            chat = client.chat.create(model=MODEL_MAP[model_key])
            chat.append(user(prompt))

            response = chat.sample()
            decoded = response.content.strip()
            if debug:
                print(f"[Grok response]: {decoded}")
        elif model_key.startswith("google"):
            client = Client(
                api_key=os.getenv("XAI_API_KEY"),
                timeout=3600,  # long timeout for reasoning models
            )

            chat = client.chat.create(model=MODEL_MAP[model_key])
            chat.append(user(prompt))

            response = chat.sample()
            decoded = response.content.strip()
            if debug:
                print(f"[Grok response]: {decoded}")
        else:
            # Tokenize and move to device
            inputs = tokenizer(
                prompt,
                return_tensors="pt",
                padding=True,
                truncation=True
            )
            inputs = {k: v.to(device) for k, v in inputs.items()}  # ✅ Move to device correctly

            # Generate
            output_ids = model.generate(
                input_ids=inputs["input_ids"],
                attention_mask=inputs["attention_mask"],
                temperature=0.0,
                top_p=1.0,
                do_sample=False,
                max_new_tokens=30,
                min_length=inputs["input_ids"].shape[-1] + 4,
                repetition_penalty=1.2,
                pad_token_id=tokenizer.eos_token_id
            )

            decoded = tokenizer.batch_decode(
                output_ids,
                skip_special_tokens=True,
                clean_up_tokenization_spaces=True
            )[0]

        # Post-processing: extract relevant part
        for key in ["الملخص:", "الترجمة:", "الجواب:"]:
            if key in decoded:
                summary = decoded.split(key)[-1].strip()
                break
        else:
            summary = decoded.strip()

        if task == "summarization":
            summary = re.split(r"[.!؟]\s*", summary)[0].strip()

        return decoded.strip()

    except Exception as e:
        return f"ERROR: {e}"
