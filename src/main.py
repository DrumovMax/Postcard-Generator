from postcard_generator import record_voice
from postcard_generator import get_postcard
from io import BytesIO
from PIL import Image
import streamlit as st


PREVIEW_POSTCARD = "../images/result.png"


def update_postcard_result(img):
    st.image(img)
    buf = BytesIO()
    img.save(buf, format="PNG")
    st.download_button(label="Download", data=buf.getvalue(), file_name="Postcard.png")


def default_postcard():
    postcard = Image.open(PREVIEW_POSTCARD)
    st.session_state.postcard = postcard


def main():
    st.title("Postcard Generator by [Drumov Max](https://github.com/DrumovMax)")
    st.sidebar.header("Postcard generator")
    st.sidebar.write("Record the description of the postcard")
    input_voice_button = st.sidebar.button(label="Record")
    st.sidebar.caption("Press the button and start talking text, to end recording stop talking")

    if "record" not in st.session_state:
        st.session_state.record = ""

    if input_voice_button:
        st.session_state.record = record_voice()
        if not len(st.session_state.record):
            st.sidebar.error("Nothing is recognized, try recording again (×﹏×)")
    if len(st.session_state.record):
        st.sidebar.write(f"Voice input: {st.session_state.record}")
    theme = st.sidebar.selectbox(
        'Choose a postcard theme',
        ('Default', 'New Year and Merry Christmas', 'Happy Birthday', 'Happy Easter', 'Halloween'))
    steps = st.sidebar.slider("Numbers of inference steps", value=25, min_value=5, max_value=100)
    height = st.sidebar.slider("Height", value=512, min_value=256, max_value=512)
    width = st.sidebar.slider("Width", value=512, min_value=256, max_value=512)

    if "postcard" not in st.session_state:
        default_postcard()

    generate_postcard = st.sidebar.button('Generate postcard', disabled=not len(st.session_state.record))
    try:
        if generate_postcard:
            st.session_state.postcard = get_postcard(st.session_state.record, theme, steps, height, width)
            st.sidebar.success("Your postcard is ready (ﾉ◕ヮ◕)ﾉ*:･ﾟ✧")
    except Exception as e:
        st.sidebar.error("Failed with error: {}".format(e))

    update_postcard_result(st.session_state.postcard)


if __name__ == '__main__':
    main()

