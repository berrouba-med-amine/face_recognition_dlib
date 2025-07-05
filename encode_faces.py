import face_recognition
import os
import pickle
from tqdm import tqdm  # barre de progression

dataset_dir = "dataset/small_lfw"
known_encodings = []
known_names = []

# Compter le nombre total d'images à traiter
total_images = sum(len(files) for _, _, files in os.walk(dataset_dir))

# Boucle avec progression
with tqdm(total=total_images, desc="Encodage des visages") as pbar:
    for name in os.listdir(dataset_dir):
        person_dir = os.path.join(dataset_dir, name)
        if not os.path.isdir(person_dir):
            continue
        for filename in os.listdir(person_dir):
            filepath = os.path.join(person_dir, filename)
            image = face_recognition.load_image_file(filepath)
            encodings = face_recognition.face_encodings(image)
            if encodings:
                known_encodings.append(encodings[0])
                known_names.append(name)
            pbar.update(1)  # mettre à jour la barre

# Sauvegarder les encodages
with open("encodings.pkl", "wb") as f:
    pickle.dump((known_encodings, known_names), f)

print(f"✅ Encodages créés pour {len(known_names)} visages.")
