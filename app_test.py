from flask import render_template, url_for, request, jsonify
from flask import Flask
from peft import AutoPeftModelForCausalLM
from transformers import AutoTokenizer
import traceback
import test
import requests
import base64
from huggingface_hub import login

login("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")


app = Flask(__name__)

SD_URL = "http://localhost:7860"
SD_PROGRESS_ENDPOINT = "/sdapi/v1/progress"
SD_TTI_ENDPOINT = "/sdapi/v1/txt2img"
SD_MODEL_NAME = "v2-1_768-ema-pruned"
MODEL_PATH = "LisiyLexa/optimist_llama"


MODEL = AutoPeftModelForCausalLM.from_pretrained(
    MODEL_PATH,
    load_in_4bit=True,
)
TOKENIZER = AutoTokenizer.from_pretrained(MODEL_PATH)


def generate_text(prompt: str) -> str:
    """Optimize user's prompt
    :return: advanced prompt
    """
    inputs = TOKENIZER([f"<human>: {prompt}\n<bot>: "], return_tensors="pt").to("cuda")

    outputs = MODEL.generate(
        **inputs, max_new_tokens=64, use_cache=True, repetition_penalty=1.15
    )
    t = TOKENIZER.batch_decode(outputs, skip_special_tokens=True)[0]
    return t[t.find("<bot>: "):]


def get_image(prompt: str, settings: dict) -> str:
    """Generates image by given prompt\n
    `prompt` - text description of image\n
    `return` - string representation of base64-encoded image
    """
    opt = requests.get(url=f"{SD_URL}/sdapi/v1/options")
    opt_json = opt.json()
    opt_json["sd_model_checkpoint"] = SD_MODEL_NAME
    requests.post(url=f"{SD_URL}/sdapi/v1/options", json=opt_json)
    payload = {"prompt": prompt, 'negative prompt': "concept art, bad quality, cartoon", **settings}

    # Send said payload to said URL through the API.
    response = requests.post(url=SD_URL + SD_TTI_ENDPOINT, json=payload)
    r = response.json()
    print(r)
    print(r["images"][0])
    image_data = base64.b64decode(r["images"][0])
    with open(f"output_{prompt[-20:]}.png", "wb") as f:
        f.write(image_data)

    # encoded image
    return base64.b64encode(image_data).decode("utf-8")


@app.errorhandler(Exception)
def handle_error(error):
    response = {"error": str(error)}
    print(traceback.format_exc())
    return jsonify(response), 500


@app.route("/api/progress", methods=["GET"])
def get_progress():
    response = requests.get(SD_URL + SD_PROGRESS_ENDPOINT)
    if response.status_code == 200:
        progress_info = response.json()
        print("Progress: ", progress_info["progress"])
        print("ETA:", progress_info["eta_relative"], "seconds")

        if progress_info["progress"] >= 1:
            print("Image generation complete!")
    return jsonify(
        {
            "progress": progress_info["progress"] * 100,
        }
    )


@app.route("/api/get_image", methods=["POST"])
def gen_image():
    data = request.get_json()
    user_prompt = data["user_prompt"]
    optimized_prompt = generate_text(user_prompt)
    user_image = get_image(user_prompt, data["settings"])
    optimized_image = get_image(optimized_prompt, data["settings"])
    return jsonify(
        {
            "user_prompt": user_prompt,
            "optimized_prompt": optimized_prompt,
            "user_image": f"data:image/png;base64,{user_image}",
            "optimized_image": f"data:image/png;base64,{optimized_image}",
        }
    )


@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")


if __name__ == "__main__":
    # app.run(debug=True)
    app.run(host="0.0.0.0")
