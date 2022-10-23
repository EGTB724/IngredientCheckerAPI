from fastapi import FastAPI, UploadFile, File
import shutil
from importlib.resources import path
import os, io
from google.cloud import vision
from google.cloud import vision_v1
from google.cloud.vision_v1 import types

app = FastAPI()

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'hackathonapp-366319-8da6ff1bc8b6.json'

client = vision.ImageAnnotatorClient()

Dict = {1: 'geeks', 2: 'wheat', 3: 'geeks'}


def detectText(img):
    with io.open(img, 'rb') as image_file:
        content = image_file.read()

    image = vision_v1.types.Image(content=content)
    response = client.text_detection(image=image)
    texts = response.text_annotations

    os.remove("image.jpg")
    return texts


def findAllergy(texts):
    for text in texts:
        if text.description.lower() in Dict.values():
            return{"message" : f"Do not consume due to the ingredient {text.description}"}
    return{"message":"This is safe to consume"}


@app.post("/get_text")
async def get_text(file: UploadFile = File(...)):
    with open('image.jpg', "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    texts = detectText("image.jpg")
    return findAllergy(texts)