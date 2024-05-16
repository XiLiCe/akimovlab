from flask import render_template, url_for, request, jsonify
from flask import Flask
import traceback
import test

app = Flask(__name__)


@app.errorhandler(Exception)
def handle_error(error):
    response = {"error": str(error)}
    print(traceback.format_exc())
    return jsonify(response), 500


@app.route("/api/get_image", methods=["POST"])
def get_image():
    data = request.get_json()
    user_prompt = data["user_prompt"]
    optimized_prompt = test.generate_text_test(user_prompt)
    user_image = test.generate_image_test(user_prompt)
    optimized_image = test.generate_image_test(optimized_prompt)
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
    app.run(debug=True)
    # app.run(host="0.0.0.0")
