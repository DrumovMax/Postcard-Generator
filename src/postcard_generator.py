import speech_recognition as sr
import streamlit as st
import torch
from diffusers import StableDiffusionPipeline
from PIL import Image

MODEL_ID = "runwayml/stable-diffusion-v1-5"
IMAGES_DIR = "../images/"
SYSTEM = "cuda" if torch.cuda.is_available() else "cpu"


@st.cache(allow_output_mutation=True, suppress_st_warning=True)
def get_pipe():
    if SYSTEM == "cuda":
        return StableDiffusionPipeline.from_pretrained(MODEL_ID, torch_dtype=torch.float16, revision="fp16").to(SYSTEM)
    else:
        return StableDiffusionPipeline.from_pretrained(MODEL_ID).to(SYSTEM)


def model_image(txt, theme, steps, height, width):
    pipe = get_pipe()
    pipe.safety_checker = lambda images, clip_input: (images, False)
    prompt = f"Cartoon {theme} postcard {txt}"
    image = pipe(prompt=prompt, num_inference_steps=steps, height=height, width=width).images[0]
    return image


def record_voice():
    try:
        listener = sr.Recognizer()
        with sr.Microphone() as microphone:
            aud_msg = listener.listen(microphone)
        txt_msg = listener.recognize_google(aud_msg, language='en-US')
    except Exception as e:
        st.sidebar.exception(e)
        st.sidebar.write("We gave you back kitty ʕ ᵔᴥᵔ ʔ")
        txt_msg = "kitty"
    return txt_msg.lower()


def image_watermark(input_image, watermark_image, position):
    watermark = Image.open(watermark_image)
    width, height = input_image.size
    transparent = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    transparent.paste(input_image, (0, 0))
    transparent.paste(watermark, position, mask=watermark)
    return transparent


def get_postcard(input_txt, input_theme, steps, height, width):
    choose_watermark = {
        'Default': 'default.png',
        'New Year and Merry Christmas': 'new_year_merry_xmas.png',
        'Happy Birthday': 'happy_birthday.png',
        'Happy Easter': 'happy_easter.png',
        'Halloween': 'halloween.png'
    }
    image = model_image(input_theme, input_txt, steps, height, width)
    return image_watermark(image, IMAGES_DIR + choose_watermark[input_theme], position=(0, 0))
