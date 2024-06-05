## Optimist
Optimist is a web application designed for prompt optimization in image generation. It provides tools and features to enhance and fine-tune text prompts to achieve better results from image generation models.

## Description
Optimist aims to streamline the process of generating high-quality images using text prompts. By leveraging advanced algorithms and user-friendly interfaces, users can experiment with different prompt variations and see real-time feedback on the generated images. This makes it easier to identify the most effective prompts for their needs.

## Requirements
To run Optimist, you will need the following software and libraries installed:

- Python 3.11 or higher
- Flask
- Stable Diffusion client
- Other dependencies listed in requirements.txt

## Installation Guide
Follow these steps to set up and run Optimist on your local machine:

1. Clone the repository:

```sh
git clone https://github.com/XiLiCe/akimovlab.git
cd optimist
```

2. Configure the application:

- Set up environment variables and configurations as needed. You might need to create a .env file in the root directory and specify variables like API keys, model paths, etc.(check .env.example file)

### Run the application:

- Run `create_venv.bat` file to automatically create virtual environment, install packages and run app

**-OR-**

1. Create and activate a virtual environment (optional but recommended):

```sh
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

2. Install the required Python packages:

```sh
pip install -r requirements.txt
```

3. Start the backend server:

```sh
python app.py
```

Open your browser and navigate to http://localhost:5000 to access the application.

## Usage
1. Input your prompt:
- Enter the text prompt you want to optimize for image generation.

2. Edit optimized prompt:
- Edit optimized prompt if you don't like something in it.

3. Generate images:
- Click the generate button to see the initial and optimized image output based on your prompt.

4. Compare results:
- View and compare the generated images to identify the most effective prompt for your needs.

## Contact
For any questions or suggestions, please contact dudnik.a.v@mail.ru
