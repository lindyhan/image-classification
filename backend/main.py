from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import base64
import io
from PIL import Image
import numpy as np
import onnxruntime
import requests
from bs4 import BeautifulSoup
import logging

app = FastAPI()

logging.basicConfig(level=logging.DEBUG)

# Load the SqueezeNet model
session = onnxruntime.InferenceSession("squeezenet1.1-7.onnx")

# Load ImageNet classes
with open('imagenet_classes.txt', 'r') as f:
    imagenet_classes = [line.strip() for line in f.readlines()]

class ImagePayload(BaseModel):
    image: str

def preprocess_image(image):
    # Resize the image to 224x224 pixels
    image = image.resize((224, 224))
    # Convert the image to RGB if it's not
    image = image.convert('RGB')
    # Convert to numpy array and normalize
    np_image = np.array(image).astype(np.float32) / 255.0
    # Subtract mean and divide by std dev
    mean = np.array([0.485, 0.456, 0.406]).reshape((1, 1, 3))
    std = np.array([0.229, 0.224, 0.225]).reshape((1, 1, 3))
    np_image = (np_image - mean) / std
    # Transpose to (C, H, W) format
    np_image = np_image.transpose((2, 0, 1))
    # Add batch dimension
    np_image = np_image[np.newaxis, ...]
    return np_image.astype(np.float32)  # Ensure float32 type

def postprocess_output(output):
    # Get the index of the highest probability
    class_index = np.argmax(output)
    # Map the index to a class name
    return imagenet_classes[class_index]

@app.post("/classify")
async def classify_image(payload: ImagePayload):
    logging.debug("Received image for classification")
    try:
        # Decode base64 image
        image_data = base64.b64decode(payload.image.split(',')[1])
        image = Image.open(io.BytesIO(image_data))
        logging.debug("Image decoded successfully")

        # Preprocess image
        input_data = preprocess_image(image)
        logging.debug(f"Image preprocessed. Shape: {input_data.shape}, dtype: {input_data.dtype}")

        # Run inference
        input_name = session.get_inputs()[0].name
        output_name = session.get_outputs()[0].name
        result = session.run([output_name], {input_name: input_data})
        logging.debug(f"Model inference result shape: {result[0].shape}")

        # Postprocess output
        classification = postprocess_output(result[0])
        logging.debug(f"Classification result: {classification}")

        # Get additional information about the animal
        animal_info, is_dangerous = get_animal_info(classification)

        return {
            "classification": classification,
            "animalInfo": animal_info,
            "isDangerous": is_dangerous
        }
    except Exception as e:
        logging.error(f"Error in classification: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def get_animal_info(animal_name):
    # Implement Wikipedia scraping and information extraction here
    url = f"https://en.wikipedia.org/wiki/{animal_name}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract the first paragraph
    first_paragraph = soup.find('p', class_='').text
    
    # Determine if the animal is dangerous (this is a simplistic approach)
    is_dangerous = "dangerous" in first_paragraph.lower() or "predator" in first_paragraph.lower()
    
    return first_paragraph, is_dangerous

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)