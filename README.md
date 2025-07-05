# 🧠 Web App de Reconnaissance Faciale avec Flask

Cette application web permet de gérer un dataset de visages, d'entraîner un modèle avec les images fournies, puis de reconnaître les personnes automatiquement via la webcam.

---

## 🚀 Fonctionnalités

- 📸 Capture d'images depuis la webcam
- ➕ Ajout et suppression de personnes et de leurs photos
- 🧠 Entraînement du modèle de reconnaissance faciale
- 👁️ Reconnaissance en temps réel avec feedback instantané
- 🔌 Interface simple et interactive via Flask + HTML/CSS

---

## 📦 Technologies utilisées

- Python 3.10+
- Flask
- face_recognition (basé sur dlib)
- OpenCV (cv2)
- HTML / CSS
- JavaScript + WebSocket (Socket.IO)

---

## 🛠️ Installation

### 1. Cloner le dépôt

```bash
git clone https://github.com/berrouba-med-amine/face_recognition_dlib.git
cd flask-face-recognition-app
```

### 2. Créer un environnement virtuel

```bash
python -m venv ai_env
source ai_env/bin/activate  # ou ai_env\Scripts\activate sous Windows
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```
Si besoin (Linux) :

```bash
sudo apt install cmake libboost-all-dev
```


### 4. Lancer l’application

```bash
python app.py
```
Puis ouvrir http://localhost:5000 dans ton navigateur.

## 📄 Licence
Ce projet est open source sous licence MIT.
Tu peux l’utiliser, le modifier ou le redistribuer librement avec attribution.

## 👨‍💻 Auteur
Développé avec ❤️ par BERROUBA / MOHAMED EL AMINE

📬 Pour toute suggestion ou bug, ouvre une issue ou contacte-moi !



