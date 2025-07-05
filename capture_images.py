import cv2
import os
import face_recognition

# 🔹 1. Demander un nom unique
base_dir = "dataset/small_lfw"
while True:
    name = input("Enter your name ({firstname}_{lastname}) : ").strip()
    save_dir = os.path.join(base_dir, name)
    if os.path.exists(save_dir):
        print("This name exists, Please use another.")
    else:
        os.makedirs(save_dir)
        break

# 🔹 2. Paramètres
target_size = (250, 250)
max_images = 10
count = len(os.listdir(save_dir))  # si des images existent déjà

# 🔹 3. Capture webcam
cap = cv2.VideoCapture(0)
print(f"📸 Enter 's' for capturing image (if only one face is detected), 'q' to exist")

while count < max_images:
    ret, frame = cap.read()
    if not ret:
        break

    # 🔍 Détection des visages dans l'image actuelle
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_frame)


    # ✏️ Créer une copie pour l’affichage (texte, état)
    display_frame = frame.copy()

    # 🔢 Affichage de l'état
    if len(face_locations) == 1:
        cv2.putText(display_frame, "1 Face detected", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    elif len(face_locations) > 1:
        cv2.putText(display_frame, "More than one face detected", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
    else:
        cv2.putText(display_frame, "No face detected", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

    # 🔢 Afficher le compteur d’images
    counter_text = f"{name} - Image {count + 1}/{max_images}"
    cv2.putText(display_frame, counter_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)

    # 🎥 Afficher l’image
    cv2.imshow("Capture", display_frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord('s'):
        if len(face_locations) == 1:
            resized = cv2.resize(frame, target_size)
            img_path = os.path.join(save_dir, f"{name}_{count}.jpg")
            cv2.imwrite(img_path, resized)
            print(f"✅ Image {count + 1} saced : {img_path}")
            count += 1
        else:
            print("Ignored Capture : must detect only one face !")

    elif key == ord('q'):
        break

if count >= max_images:
    print("✅ image numbers reached.")

cap.release()
cv2.destroyAllWindows()
