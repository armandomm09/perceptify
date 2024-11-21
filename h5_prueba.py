# from PIL import Image
# import requests

# from transformers import CLIPProcessor, CLIPModel

# model = CLIPModel.from_pretrained("openai/clip-vit-large-patch14")
# processor = CLIPProcessor.from_pretrained("openai/clip-vit-large-patch14")

# # url = "http://images.cocodataset.org/val2017/000000039769.jpg"
# image = Image.open("media/emotions/in_images/IMG_4685.JPG")

# inputs = processor(text=["angry person", "disgusted person", "frightened person", "happy person", "neutral person", "sad person", "surprised person"], images=image, return_tensors="pt", padding=True)

# outputs = model(**inputs)
# logits_per_image = outputs.logits_per_image # this is the image-text similarity score
# probs = logits_per_image.softmax(dim=1) # we can take the softmax to get the label probabilities


from transformers import pipeline
import skimage
import numpy as np
from PIL import Image, ImageDraw

# checkpoint = "google/owlvit-base-patch32"
# checkpoint = "openai/clip-vit-large-patch14"
checkpoint = "google/owlv2-base-patch16-ensemble"
detector = pipeline(model=checkpoint, task="zero-shot-object-detection", device="mps")


image = Image.open("media/emotions/in_images/IMG_4685.JPG")
image = Image.fromarray(np.uint8(image)).convert("RGB")



predictions = detector(
    image,
    candidate_labels=["angry person", "disgusted person", "frightened person", "happy person", "neutral person", "sad person", "surprised person"],
)


draw = ImageDraw.Draw(image)

for prediction in predictions:
    box = prediction["box"]
    label = prediction["label"]
    score = prediction["score"]

    xmin, ymin, xmax, ymax = box.values()
    draw.rectangle((xmin, ymin, xmax, ymax), outline="red", width=1)
    draw.text((xmin, ymin), f"{label}: {round(score,2)}", fill="white")

image.save("media/emotions/in_images/IMG_4685.JPG")
print(predictions)


