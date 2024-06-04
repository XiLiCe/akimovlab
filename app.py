from flask import (
    Flask,
    render_template,
    url_for,
    request,
    jsonify,
)
from flask_socketio import SocketIO, emit

from peft import AutoPeftModelForCausalLM
from transformers import AutoTokenizer, TextStreamer
import huggingface_hub as hh

from dotenv import load_dotenv

import traceback
import requests
import base64
import test
import time
import os

load_dotenv()

app = Flask(__name__)
socketio = SocketIO(app)

SD_URL = os.getenv("SD_URL")
SD_PROGRESS_ENDPOINT = os.getenv("SD_PROGRESS_ENDPOINT")
SD_TTI_ENDPOINT = os.getenv("SD_TTI_ENDPOINT")
SD_MODEL_NAME = os.getenv("SD_MODEL_NAME")
MODEL_PATH = os.getenv("MODEL_PATH")
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")
MODEL = None
TOKENIZER = None

SAVE_OUTPUT = False
TEST = False


class MyStreamer(TextStreamer):
    def __init__(
        self, tokenizer: AutoTokenizer, skip_prompt: bool = False, **decode_kwargs
    ):
        super().__init__(tokenizer, skip_prompt, **decode_kwargs)

    def on_finalized_text(self, text: str, stream_end: bool = False):
        socketio.emit("new_word", {"word": text.strip()})
        print(text, flush=True, end="" if not stream_end else None)

    def end(self):
        super().end()


def init_models() -> None:
    """Initialize Text model and tokenizer"""
    global MODEL, TOKENIZER, TEST
    hh.login(HUGGINGFACE_TOKEN)
    try:
        MODEL = AutoPeftModelForCausalLM.from_pretrained(
            MODEL_PATH,
            load_in_4bit=False,
        )
        TOKENIZER = AutoTokenizer.from_pretrained(MODEL_PATH)

    except RuntimeError as e:
        TEST = True
        print(e, traceback.format_exc())
        print("NO GPU. RUNNING IN TEST MODE")

    # Set StableDiffusion model to SD_MODEL_NAME
    opt = requests.get(url=f"{SD_URL}/sdapi/v1/options")
    opt_json = opt.json()
    opt_json["sd_model_checkpoint"] = SD_MODEL_NAME
    requests.post(url=f"{SD_URL}/sdapi/v1/options", json=opt_json)


def format_input(text: str) -> str:
    """Formats input to llama capable format\n
    `return` prompt in format '<human>: {text}\\n<bot>: '"""
    return f"<human>: {text}\n<bot>: "


def generate_text(prompt: str):
    """Optimize user's prompt
    :return: advanced prompt
    """
    if TEST:
        new_prompt = test.generate_text(prompt)
        for word in new_prompt.split():
            yield word
            time.sleep(0.5)
    else:
        formatted_prompt = format_input(prompt)
        inputs = TOKENIZER([formatted_prompt], return_tensors="pt").to("cuda")

        # outputs = MODEL.generate(
        #     **inputs, max_new_tokens=64, use_cache=True, repetition_penalty=1.1
        # )
        # new_prompt = TOKENIZER.batch_decode(outputs, skip_special_tokens=True)[0]
        # return new_prompt[len(formatted_prompt) : :]

        text_streamer = MyStreamer(TOKENIZER, skip_prompt=True)
        MODEL.generate(
            **inputs,
            streamer=text_streamer,
            max_new_tokens=56,
            use_cache=True,
            repetition_penalty=1.25,
        )


def generate_image(prompt: str, settings: dict) -> str:
    """Generates image by given prompt\n
    `prompt` - text description of image\n
    `return` - string representation of base64-encoded image
    """

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
    yield jsonify(
        {
            "user_prompt": user_prompt,
        }
    )


@socketio.on("generate_prompt")
def handle_generate_prompt(data):
    user_prompt = data["user_prompt"]
    for word in generate_text(user_prompt):
        emit("new_word", {"word": word})
    else:
        emit("end_new_prompt")


@app.route("/api/get_image", methods=["POST"])
def get_image():
    data = request.get_json()
    user_prompt = data["user_prompt"]
    optimized_prompt = data["optimized_prompt"]
    if TEST:
        user_image = test.generate_image(user_prompt, data["settings"])
        optimized_image = test.generate_image(optimized_prompt, data["settings"])
    else:
        user_image = (
            f"data:image/png;base64,{generate_image(user_prompt, data['settings'])}"
        )
        optimized_image = f"data:image/png;base64,{generate_image(optimized_prompt, data['settings'])}"
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


if not TEST:
    init_models()

if __name__ == "__main__":
    socketio.run(app, debug=True, host="0.0.0.0")
    # app.run(host="0.0.0.0")
