from flask import render_template, url_for, request, jsonify
from flask import Flask

from peft import AutoPeftModelForCausalLM
from transformers import AutoTokenizer
import requests

import torch
import requests
import json
import base64

app = Flask(__name__)

MODEL_PATH = "modellamma"  # Model path
TOKENIZER_PATH = "modellamma"  # Tokenizer path
SD_API_ENDPOINT = "http://127.0.0.1:7860/sdapi/v1/txt2img"  # stablediffusion api url


# load model and tokenizer
MODEL = AutoPeftModelForCausalLM.from_pretrained(
    MODEL_PATH,
    load_in_4bit=True,
)
TOKENIZER = AutoTokenizer.from_pretrained(TOKENIZER_PATH)


def generate_text(prompt: str) -> str:
    """Optimize user's prompt
    :return: advanced prompt
    """
    inputs = TOKENIZER([f"<human>: {prompt}\n<bot>: "], return_tensors="pt").to("cuda")

    outputs = MODEL.generate(
        **inputs, max_new_tokens=64, use_cache=True, repetition_penalty=1.15
    )
    return TOKENIZER.batch_decode(outputs, skip_special_tokens=True)


def get_image(prompt: str) -> str:
    """Generates image by given prompt\n
    `prompt` - text description of image\n
    `return` - string representation of base64-encoded image
    """

    payload = {"prompt": prompt, "steps": 5}

    # Send said payload to said URL through the API.
    response = requests.post(url=SD_API_ENDPOINT, json=payload)
    r = response.json()
    image_data = base64.b64decode(r["images"][0])
    with open("output.png", "wb") as f:
        f.write(image_data)

    # encoded image
    return base64.b64encode(image_data).decode("utf-8")


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        prompt = request.form["prompt"]
        generated_text = generate_text(prompt)
        image = get_image(generated_text)
        return render_template(
            "index.html", prompt=prompt, generated_text=generated_text, image=image
        )
    return render_template("index.html")


if __name__ == "__main__":
    app.run(port=8080)
