from flask import Blueprint, render_template, request, redirect, url_for, jsonify, render_template, send_from_directory
import os
import shutil
import base64
import cv2
import numpy as np
import face_recognition
import pickle
from modules.extensions import socketio


persons_bp = Blueprint('persons', __name__, template_folder='templates', url_prefix='/persons')

DATASET_DIR = "dataset/small_lfw"

@persons_bp.route("/")
def list_persons():
    per_page = 10
    page = int(request.args.get("page", 1))
    persons = []

    # 🔽 Lister et trier les dossiers par date de création (la plus récente d'abord)
    all_dirs = [
        (name, os.path.join(DATASET_DIR, name))
        for name in os.listdir(DATASET_DIR)
        if os.path.isdir(os.path.join(DATASET_DIR, name))
    ]
    sorted_dirs = sorted(all_dirs, key=lambda x: os.path.getctime(x[1]), reverse=True)

    for name, person_path in sorted_dirs:
        image_count = len([f for f in os.listdir(person_path) if f.endswith('.jpg')])
        persons.append({"name": name, "image_count": image_count})

    # Filtrage par nom
    search_query = request.args.get('search', '').strip().lower()
    if search_query:
        persons = [p for p in persons if search_query in p["name"].lower()]

    total_pages = (len(persons) + per_page - 1) // per_page
    start = (page - 1) * per_page
    end = start + per_page
    paginated = persons[start:end]

    return render_template("persons.html",
        paginated_persons=paginated,
        current_page=page,
        total_pages=total_pages,
        total_count=len(persons)
    )

@persons_bp.route("/add_person", methods=["POST"])
def add_person():
    name = request.form.get("name")
    if not name:
        return redirect(url_for("persons.list_persons"))
    person_path = os.path.join(DATASET_DIR, name)
    if not os.path.exists(person_path):
        os.makedirs(person_path)
    return redirect(url_for("persons.list_persons"))

@persons_bp.route("/delete_person", methods=["POST"])
def delete_person():
    name = request.form.get("name")
    if not name:
        return redirect(url_for("persons.list_persons"))
    person_path = os.path.join(DATASET_DIR, name)
    if os.path.exists(person_path):
        shutil.rmtree(person_path)
    return redirect(url_for("persons.list_persons"))

@persons_bp.route("/capture/<name>")
def capture_page(name):
    person_dir = os.path.join(DATASET_DIR, name)
    image_urls = []

    if os.path.exists(person_dir):
        for filename in sorted(os.listdir(person_dir)):
            if filename.endswith(".jpg"):
                # Chemin relatif à dataset/small_lfw
                image_urls.append(f"{name}/{filename}")

    return render_template("capture.html", name=name, images=image_urls)


@persons_bp.route('/images/<path:filename>')
def serve_person_image(filename):
    return send_from_directory('dataset/small_lfw', filename)

@persons_bp.route('/delete_image', methods=['POST'])
def delete_image():
    filename = request.form.get("filename")
    name = request.form.get("name")

    if not filename or not name:
        return jsonify({"success": False, "message": "Paramètres manquants."}), 400

    file_path = os.path.join(DATASET_DIR, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        return jsonify({"success": True, "message": "✅ Image supprimée", "filename": filename})
    else:
        return jsonify({"success": False, "message": "Image introuvable."})

@persons_bp.route("/capture_face", methods=["POST"])
def capture_face():
    data = request.get_json()
    name = data.get("name")

    image_data = data.get("image")

    if not name or not image_data:
        return jsonify({"message": "Nom ou image manquant."}), 400

    # Décoder l'image base64
    header, encoded = image_data.split(",", 1)
    img_bytes = base64.b64decode(encoded)
    img_array = np.frombuffer(img_bytes, dtype=np.uint8)
    frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    # Vérifier qu’un seul visage est présent
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_frame)

    if len(face_locations) != 1:
        return jsonify({"message": f"{len(face_locations)} visage(s) détecté(s). Capture ignorée."})


    # Créer dossier utilisateur si nécessaire
    save_dir = os.path.join(DATASET_DIR, name)
    os.makedirs(save_dir, exist_ok=True)

    # print(f"Enregistrement de l'image pour {name} dans {save_dir}")

    # Limiter à 10 images max
    existing = len([f for f in os.listdir(save_dir) if f.endswith(".jpg")])
    if existing >= 10:
        return jsonify({"message": "Limite atteinte (10 images)."})

    # print(f"Images existantes pour {name}: {existing}")

    # Sauvegarder l’image
    img_name = f"{name}_{existing}.jpg"
    save_path = os.path.join(save_dir, img_name)
    resized = cv2.resize(frame, (250, 250))
    cv2.imwrite(save_path, resized)


    return jsonify({
        "success": True,
        "message": f"✅ Image enregistrée ({existing + 1}/{10})",
        "filename": f"{name}/{img_name}"
    })

@persons_bp.route("/encore_faces")
def encore_faces():
    try:
        dataset_dir = "dataset/small_lfw"
        known_encodings = []
        known_names = []


        total = len(os.listdir(dataset_dir))
        processed = 0

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

            # ➕ Incrémenter la progression
            processed += 1
            socketio.emit("encodage_progress", {
                "total": total,
                "done": processed,
                "name": name
            })

        # Sauvegarder les encodages
        with open("encodings.pkl", "wb") as f:
            pickle.dump((known_encodings, known_names), f)

        return jsonify({
            "success": True,
            "message": f"✅ Encodages créés pour {len(known_names)} visages(s).",
        })
    except Exception as e:
        return jsonify({"error": str(e)})
