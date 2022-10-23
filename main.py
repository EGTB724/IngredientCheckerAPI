from fastapi import FastAPI, UploadFile, File, Query
import shutil
from importlib.resources import path
import os, io
from google.cloud import vision
from google.cloud import vision_v1
from google.cloud.vision_v1 import types
import csv
from typing import List

app = FastAPI()

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'hackathonapp-366319-8da6ff1bc8b6.json'

client = vision.ImageAnnotatorClient()

milk = []
eggs = []
fish = []
nuts = []
wheat = []
soy = []

with open('FoodData.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        if line_count == 0:
            continue
        else:
            if "milk".casefold() in row[3].casefold():
                milk.append(row[2])
            if "eggs".casefold() or "poultry".casefold() in row[3].casefold():
                eggs.append(row[2])
            if "fish".casefold() in row[3].casefold():
                fish.append(row[2])
            if "nut".casefold() in row[3].casefold():
                nuts.append(row[2])
            if "wheat".casefold() or "gluten".casefold() in row[3].casefold():
                wheat.append(row[2])
            if "soy".casefold() in row[3].casefold():
                soy.append(row[2])


def detectText(img):
    with io.open(img, 'rb') as image_file:
        content = image_file.read()

    image = vision_v1.types.Image(content=content)
    response = client.text_detection(image=image)
    texts = response.text_annotations

    os.remove("image.jpg")
    return texts


def findAllergy(allergy_list, texts):
    for item in allergy_list:
        if item == "milk":
            respective_list = milk
        elif item == "eggs":
            respective_list = eggs
        elif item == "fish":
            respective_list = fish
        elif item == "nuts":
            respective_list = nuts
        elif item == "wheat":
            respective_list = wheat
        elif item == "soy":
            respective_list = soy
        for text in texts:
            if text.description.lower() in respective_list:
                return{"message" : f"Do not consume due to the ingredient {text.description}"}
        return{"message":"This is safe to consume"}


@app.post("/get_text")
async def read_items(allergy_list: List[str] = Query(None), file: UploadFile = File(...)):
    with open('image.jpg', "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    texts = detectText("image.jpg")
    return findAllergy(allergy_list, texts)
