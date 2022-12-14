from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
from diffusers import StableDiffusionPipeline
from pydub import AudioSegment
from PIL import Image
import speech_recognition as sr
import streamlit as st
import torch
import io


MODEL_IMAGE = "runwayml/stable-diffusion-v1-5"
MODEL_ASR = "facebook/wav2vec2-large-960h-lv60-self"
IMAGES_DIR = "../images/"
SYSTEM = "cuda" if torch.cuda.is_available() else "cpu"


@st.cache(allow_output_mutation=True, suppress_st_warning=True)
def get_pipe():
    if SYSTEM == "cuda":
        return StableDiffusionPipeline.from_pretrained(MODEL_IMAGE, torch_dtype=torch.float16, revision="fp16").to(SYSTEM)
    else:
        return StableDiffusionPipeline.from_pretrained(MODEL_IMAGE).to(SYSTEM)


@st.cache(allow_output_mutation=True, suppress_st_warning=True)
def get_tokenizer():
    return Wav2Vec2Processor.from_pretrained(MODEL_ASR)


@st.cache(allow_output_mutation=True, suppress_st_warning=True)
def get_input_model():
    return Wav2Vec2ForCTC.from_pretrained(MODEL_ASR).to(SYSTEM)


def model_image(txt, theme, steps, height, width):
    pipe = get_pipe()
    pipe.safety_checker = lambda images, clip_input: (images, False)
    prompt = f"Cartoon {theme} postcard {txt}"
    image = pipe(prompt=prompt, num_inference_steps=steps, height=height, width=width).images[0]
    return image


def decode_record(tensor):
    tokenizer = get_tokenizer()
    model = get_input_model()
    inputs = tokenizer(tensor, sampling_rate=16000, return_tensors='pt', padding='longest').input_values.to(SYSTEM)
    logits = model(inputs).logits
    tokens = torch.argmax(logits, axis=-1)
    return tokenizer.batch_decode(tokens)


def record_voice():
    try:
        listener = sr.Recognizer()
        with sr.Microphone(sample_rate=16000) as microphone:
            aud_msg = listener.listen(microphone)
            data = io.BytesIO(aud_msg.get_wav_data())
            clip = AudioSegment.from_file(data)
            tensor = torch.FloatTensor(clip.get_array_of_samples())
            text = decode_record(tensor)
    except Exception as e:
        st.sidebar.error("Failed with error: {}".format(e))
    return text[0].lower()


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
