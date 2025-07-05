from flask import Blueprint, request, jsonify, render_template
import face_recognition
import numpy as np
import cv2
import base64
import pickle
from io import BytesIO
from PIL import Image
import os

recognition_bp = Blueprint('recognition', __name__, template_folder='templates', url_prefix='/recognition')


def decode_base64_image(data):
    data = data.split(",")[-1]  # remove metadata
    img_data = base64.b64decode(data)
    image = Image.open(BytesIO(img_data)).convert("RGB")
    return np.array(image)

@recognition_bp.route("/")
def index():
    return render_template("recognition.html")

@recognition_bp.route("/identify", methods=["POST"])
def identify():
    try:
        # Load known encodings
        ENCODINGS_PATH = "encodings.pkl"
        if os.path.exists(ENCODINGS_PATH):
            with open(ENCODINGS_PATH, "rb") as f:
                known_encodings, known_names = pickle.load(f)
        else:
            known_encodings, known_names = [], []

        img_data = request.json["image"]
        image = decode_base64_image(img_data)

        face_locations = face_recognition.face_locations(image)
        face_encodings = face_recognition.face_encodings(image, face_locations)

        results = []
        for (top, right, bottom, left), encoding in zip(face_locations, face_encodings):
            distances = face_recognition.face_distance(known_encodings, encoding)
            best_match_index = np.argmin(distances)
            min_distance = distances[best_match_index]

            name = "Inconnu"
            confidence = 0.0
            if min_distance < 0.6:  # seuil de confiance
                name = known_names[best_match_index]
                confidence = max(0.0, 1.0 - min_distance)  # approx confidence

            label = f"{name} ({confidence:.2f})"

            # Dessiner rectangle + label
            cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(image, label, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            results.append({"name": name, "confidence": round(confidence, 2)})

        # Convertir l'image annotée en base64
        _, buffer = cv2.imencode(".jpg", cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
        encoded_image = base64.b64encode(buffer).decode("utf-8")

        return jsonify({"results": results, "image": encoded_image})
    except Exception as e:
        return jsonify({"error": str(e)})
