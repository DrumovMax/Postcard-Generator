## Postcard-Generator

## Description
This project is a postcard generator. The postcard description is entered using voice input. The type of postcard is selected from the drop-down list. The project is written in python, streamlit, hugging face model(stable-diffusion-v1-5). The generation can be run with cuda(with NVIDIA video card) or on CPU.

## How to Get Started 

1. Clone the repository:
```
git clone https://github.com/DrumovMax/Postcard-Generator.git
```
2. Create venv:
```
cd Postcard-Generator
python -m venv venv
. venv/bin/activate
```
3. Install requirements:
```
pip install -r requirements.txt
```
4. Install [torch](https://pytorch.org/)

5. Log to hugging face: 
```
huggingface-cli login
```

6. Let's run!
```
cd src
streamlit run main.py
```