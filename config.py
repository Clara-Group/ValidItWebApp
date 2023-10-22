import os
from dotenv import load_dotenv

load_dotenv()

CLOUDINARY_API_KEY = os.getenv('CLOUDINARY_API_KEY')
CLOUDINARY_API_SECRET = os.getenv('CLOUDINARY_API_SECRET')
CLOUDINARY_CLOUD_NAME = os.getenv('CLOUDINARY_CLOUD_NAME')

QUESTION_TIME = 3 # seconds
TOTAL_QUESTIONS = 3
