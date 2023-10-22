from streamlit_webrtc import WebRtcStreamerState, webrtc_streamer
import streamlit as st
import av
import threading

import yaml
import numpy as np
import uuid
from pathlib import Path

import av
import streamlit as st
from aiortc.contrib.media import MediaRecorder

import cloudinary
import cloudinary.uploader

import time    
import pytz
import datetime
from config import CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET, QUESTION_TIME, TOTAL_QUESTIONS
tz = pytz.timezone('Israel')

from questions import QuestionsSource

questionsSource = QuestionsSource()
if "questions_count" not in st.session_state:
    st.session_state["questions_count"] = questionsSource.questions_count

cloudinary.config( 
  cloud_name = CLOUDINARY_CLOUD_NAME, 
  api_key = CLOUDINARY_API_KEY, 
  api_secret = CLOUDINARY_API_SECRET 
)

RECORD_DIR = Path("./records")
RECORD_DIR.mkdir(exist_ok=True)

if "prefix" not in st.session_state:
    st.session_state["prefix"] = str(uuid.uuid4())
prefix = st.session_state["prefix"]
in_file_name = f"{prefix}_output.flv"
in_file = RECORD_DIR / in_file_name

frame_count = 1
count_lock = threading.Lock()  # Create a threading lock
        
def video_frame_callback(frame):
    global frame_count
    print(frame_count)
    with count_lock:
        frame_count += 1
    return frame

def in_recorder_factory() -> MediaRecorder:
    return MediaRecorder(
        str(in_file), format="flv", options = {"framerate": "30", "video_size": "1280x720"}
    )  # HLS does not work. See https://github.com/aiortc/aiortc/issues/331

ctx = webrtc_streamer(key="recorder", 
                    #   video_frame_callback=video_frame_callback, 
                      in_recorder_factory=in_recorder_factory, 
                      media_stream_constraints={
                        "video": True,
                        "audio": False,
                        })

if in_file.exists():
    if st.session_state.questions_count < TOTAL_QUESTIONS:
        st.write(f'Recording aborted. Refresh page to restart recording {st.session_state.questions_count}')
    else:
        result = cloudinary.uploader.upload(
            in_file,
            public_id=datetime.datetime.now(tz=tz).strftime('%Y-%m-%dT%H:%M:%SZ'),
            folder="validit",
            resource_type="video")
        print(result)

        
        st.write(f'Your video was uploaded. Asset ID = {result["asset_id"]}')
else:
    st_instructions = st.text('Click START button to start the session.')
    st_questions = st.empty()
    st_progress = st.progress(0)

    start_time = None
    while ctx and ctx.state.playing and questionsSource.questions_count <= TOTAL_QUESTIONS:
        st_instructions.text('')

        if not start_time:
            start_time = datetime.datetime.now(tz=tz)
        # with count_lock:
        #     if frame_count == 1:
        #         time.sleep(1)
        #         continue
        question = questionsSource.getNextQuestion()
        st.session_state["questions_count"] = questionsSource.questions_count
        st_questions.title(f'Q {questionsSource.questions_count - 1}: {question}')
        for secs in range(0, QUESTION_TIME):
            # mm, ss = secs//60, secs%60
            # st_timer.metric("Countdown", f"{mm:02d}:{ss:02d}")
            st_progress.progress((secs + 1) / QUESTION_TIME)
            # sh.text(f'frame {frame_count}')
            time.sleep(1)
    
    if start_time:
        st_progress.empty()
        st_questions.title('DONE! Click STOP button to end the session.')
    # st.write(f'Your video was uploaded. Asset ID = {result["asset_id"]}')
        

    # st_instructions.text('Done!')
    # st_questions.text('Click STOP button to end the session.')
    # with out_file.open("rb") as f:
    #     st.download_button(
    #         label="Download Recording", data=f, file_name=out_file_name
    #     )


