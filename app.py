from flask import render_template, url_for, request, jsonify
from flask import Flask

import traceback
import requests
import base64

TEST = False
try:
    from peft import AutoPeftModelForCausalLM
    from transformers import AutoTokenizer
    import huggingface_hub as hh
except ImportError:
    TEST = True
    import test

    print("Skipping Peft, Transformers, HF")

app = Flask(__name__)

SD_URL = "http://localhost:7860"
SD_PROGRESS_ENDPOINT = "/sdapi/v1/progress"
SD_TTI_ENDPOINT = "/sdapi/v1/txt2img"
SD_MODEL_NAME = "v2-1_768-ema-pruned"
MODEL_PATH = "LisiyLexa/optimist_llama"
HUGGINGFACE_TOKEN = "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"
MODEL = None
TOKENIZER = None

SAVE_OUTPUT = False


def init_models() -> None:
    """Initialize Text model and tokenizer"""
    global MODEL, TOKENIZER
    hh.login(HUGGINGFACE_TOKEN)

    MODEL = AutoPeftModelForCausalLM.from_pretrained(
        MODEL_PATH,
        load_in_4bit=True,
    )
    TOKENIZER = AutoTokenizer.from_pretrained(MODEL_PATH)


def format_input(text: str) -> str:
    """Formats input to llama capable format\n
    `return` prompt in format '<human>: {text}\\n<bot>: '"""
    return f"<human>: {text}\n<bot>: "


def generate_text(prompt: str) -> str:
    """Optimize user's prompt
    :return: advanced prompt
    """
    formatted_prompt = format_input(prompt)
    inputs = TOKENIZER([formatted_prompt], return_tensors="pt").to("cuda")

    outputs = MODEL.generate(
        **inputs, max_new_tokens=64, use_cache=True, repetition_penalty=1.1
    )
    new_prompt = TOKENIZER.batch_decode(outputs, skip_special_tokens=True)[0]
    return new_prompt[len(formatted_prompt) : :]


def generate_image(prompt: str, settings: dict) -> str:
    """Generates image by given prompt\n
    `prompt` - text description of image\n
    `return` - string representation of base64-encoded image
    """

    # Set StableDiffusion model to SD_MODEL_NAME
    # opt = requests.get(url=f"{SD_URL}/sdapi/v1/options")
    # opt_json = opt.json()
    # opt_json["sd_model_checkpoint"] = SD_MODEL_NAME
    # requests.post(url=f"{SD_URL}/sdapi/v1/options", json=opt_json)

    payload = {
        "prompt": prompt,
        **settings,
    }

    # Send said payload to said URL through the API.
    response = requests.post(url=SD_URL + SD_TTI_ENDPOINT, json=payload)
    r = response.json()
    print(r)
    if not "images" in r:
        raise KeyError(f"Error in generating image:\n{r['err']}")
    print(r["images"][0])
    image_data = base64.b64decode(r["images"][0])
    if SAVE_OUTPUT:
        with open(f"output_{prompt[-20:]}.png", "wb") as f:
            f.write(image_data)

    # encoded image
    return base64.b64encode(image_data).decode("utf-8")


@app.errorhandler(Exception)
def handle_error(error):
    response = {"error": str(error)}
    print(traceback.format_exc())
    return jsonify(response), 500


@app.route("/api/progress", methods=["POST"])
def get_sd_progress():
    response = requests.get(SD_URL + SD_PROGRESS_ENDPOINT)
    if response.status_code == 200:
        progress_info = response.json()
        print("Progress: ", progress_info["progress"] * 100, "%")
        print("ETA:", progress_info["eta_relative"], "seconds")

        if progress_info["progress"] >= 1:
            print("Image generation complete!")
    return jsonify(
        {
            "progress": progress_info["progress"] * 100,
        }
    )


@app.route("/api/get_prompt", methods=["POST"])
def get_prompt():
    data = request.get_json()
    user_prompt = data["user_prompt"]
    optimized_prompt = None
    if TEST:
        optimized_prompt = test.generate_text(user_prompt)
    return jsonify(
        {
            "user_prompt": user_prompt,
            "optimized_prompt": optimized_prompt,
        }
    )

@app.route("/api/get_image", methods=["POST"])
def get_image():
    data = request.get_json()
    user_prompt = data["user_prompt"]
    optimized_prompt = data["optimized_prompt"]
    if not TEST:
        user_image = f"data:image/png;base64,{get_image(user_prompt, data["settings"])}"
        optimized_image = f"data:image/png;base64,{get_image(optimized_prompt, data["settings"])}"
    else:
        user_image = test.generate_image(user_prompt, data["settings"])
        optimized_image = test.generate_image(optimized_prompt, data["settings"])
    return jsonify(
        {
            "user_prompt": user_prompt,
            "optimized_prompt": optimized_prompt,
            "user_image": user_image,
            "optimized_image": optimized_image,
        }
    )


@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")


if __name__ == "__main__":
    if not TEST:
        init_models()
    app.run(debug=True)
    # app.run(host="0.0.0.0")
