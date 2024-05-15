from flask import Flask, render_template, request
from peft import AutoPeftModelForCausalLM
from transformers import AutoTokenizer
import requests
import torch
import requests
import json
import base64

app = Flask(__name__)

# Указываем путь к вашей натренированной модели и токенизатору
MODEL_PATH = "modellamma"
TOKENIZER_PATH = "modellamma"

# Загружаем модель и токенизатор
model = AutoPeftModelForCausalLM.from_pretrained(
    MODEL_PATH,
    load_in_4bit=True,
)
tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_PATH)

# Функция для генерации текста с помощью модели
def generate_text(prompt):
    model_input = tokenizer(prompt, return_tensors="pt").to("cuda")
    model.eval()
    with torch.no_grad():
        outputs = model.generate(**model_input, max_length=128, repetition_penalty=1.15)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

# Функция для отправки промпта в API стабильной диффузии и получения картинки
def get_image(prompt):
    # api_url = "http://127.0.0.1:7860"  # Замените на URL вашего API стабильной диффузии
    # response = requests.post(url=f'{api_url}/sdapi/v1/txt2img', json={"prompt": prompt})
    # return response.content

    url = "http://127.0.0.1:7860"

    payload = {
        "prompt": prompt,
        "steps": 5
    }

    # Send said payload to said URL through the API.
    response = requests.post(url=f'{url}/sdapi/v1/txt2img', json=payload)
    r = response.json()
    image_data = base64.b64decode(r['images'][0])
    with open("output.png", 'wb') as f:
        f.write(image_data)

    # Возвращаем изображение в формате base64
    return base64.b64encode(image_data).decode('utf-8')



@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        prompt = request.form["prompt"]
        generated_text = generate_text(prompt)
        image = get_image(generated_text)
        return render_template("index.html", prompt=prompt, generated_text=generated_text, image=image)
    return render_template("index.html")

if __name__ == "__main__":
    app.run(port=8080)

