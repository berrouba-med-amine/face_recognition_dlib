// 🎯 Configuration et éléments DOM
const config = {
  video: { video: true },
  canvas: { width: 640, height: 480 },
  messages: {
    enable: "📹 Activer la webcam",
    disable: "🔴 Désactiver la webcam",
    waiting: "Résultat : ...",
    success: "✅ Résultat : ",
    error: "❌ Erreur : ",
    networkError: "❌ Erreur réseau",
    webcamError: "⚠️ Impossible d'accéder à la webcam"
  }
};

const elements = {
  toggleBtn: document.getElementById("toggleBtn"),
  video: document.getElementById("video"),
  canvas: document.getElementById("canvas"),
  snap: document.getElementById("snap"),
  preview: document.getElementById("preview"),
  status: document.querySelector(".status"),
  statusIndicator: document.querySelector(".status-indicator"),
  resultsContainer: document.getElementById("resultsContainer")
};

// 🔧 État de l'application
const state = {
  stream: null,
  isActive: false,
  processing: false
};

// 🎬 Initialisation
function init() {
  const hiddenElements = [elements.snap, elements.video, elements.preview];
  hiddenElements.forEach(el => setDisplay(el, false));
  
  // Event listeners
  elements.toggleBtn.onclick = toggleWebcam;
  elements.snap.onclick = captureAndIdentify;
  
  // Mise à jour initiale de l'UI
  updateUI(false);
}

// ⚙️ Utilitaires
function setDisplay(el, show = true) {
  el.style.display = show ? "block" : "none";
}

function updateUI(isActive) {
  const elementsToShow = [elements.video, elements.snap];
  
  elementsToShow.forEach(el => setDisplay(el, isActive));
  setDisplay(elements.preview, isActive);
  setDisplay(elements.resultsContainer, isActive);
  
  elements.toggleBtn.textContent = isActive ? config.messages.disable : config.messages.enable;
  
  // Mise à jour de l'état de la caméra
  if (isActive) {
    elements.status.classList.add("active");
    elements.status.querySelector("span").textContent = "Caméra active";
  } else {
    elements.status.classList.remove("active");
    elements.status.querySelector("span").textContent = "Caméra désactivée";
  }
}

// 🎥 Gestion de la webcam
async function enableWebcam() {
  try {
    state.stream = await navigator.mediaDevices.getUserMedia(config.video);
    elements.video.srcObject = state.stream;
    state.isActive = true;
    updateUI(true);
  } catch (err) {
    console.error('Webcam error:', err);
    elements.result.innerText = config.messages.webcamError;
    state.isActive = false;
  }
}

function disableWebcam() {
  if (state.stream) {
    state.stream.getTracks().forEach(track => track.stop());
    state.stream = null;
  }
  
  elements.video.srcObject = null;
  state.isActive = false;
  updateUI(false);
}

function toggleWebcam() {
  if (state.processing) return;
  state.isActive ? disableWebcam() : enableWebcam();
}

// 📸 Capture et identification
function captureImage() {
  const context = elements.canvas.getContext("2d");
  const { width, height } = config.canvas;
  
  context.drawImage(elements.video, 0, 0, width, height);
  return elements.canvas.toDataURL("image/jpeg");
}

// Fonction simulée pour la démonstration
async function sendImageForIdentification(imageData) {
  // En production, vous utiliseriez :
  const response = await fetch("/recognition/identify", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ image: imageData })
  });
  
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
  
  return response.json();
}

function displayResults(data) {
  if (data.results && data.results.length > 0) {
    // Afficher l'image capturée
    elements.preview.src = `data:image/jpeg;base64,${data.image}`;
    setDisplay(elements.preview);
    
    // Afficher les résultats dans un format plus élaboré
    elements.resultsContainer.innerHTML = `
      <div class="message">✅ ${data.results.length} personne(s) reconnue(s)</div>
      ${data.results.map(person => `
        <div class="person-card">
          <div class="person-name">${person.name}</div>
          <div class="confidence">Confiance: ${Math.round(person.confidence * 100)}%</div>
          <div class="confidence-bar">
            <div class="confidence-level" style="width: ${Math.round(person.confidence * 100)}%"></div>
          </div>
        </div>
      `).join('')}
    `;
  } else {
    elements.resultsContainer.innerHTML = config.messages.error + (data.error || "Aucun résultat");
  }
}

async function captureAndIdentify() {
  if (!state.isActive || !state.stream || state.processing) return;
  
  try {
    state.processing = true;
    // Désactiver temporairement les boutons
    elements.snap.disabled = true;
    elements.toggleBtn.disabled = true;
    
    // Afficher un spinner
    elements.resultsContainer.innerHTML = '<div class="spinner"></div>';
    
    const imageData = captureImage();
    const data = await sendImageForIdentification(imageData);
    
    // Effacer le spinner
    elements.resultsContainer.innerHTML = '';
    
    displayResults(data);
    
  } catch (err) {
    console.error('Identification error:', err);
    elements.resultsContainer.innerHTML = config.messages.networkError;
  } finally {
    // Réactiver les boutons
    state.processing = false;
    elements.snap.disabled = false;
    elements.toggleBtn.disabled = false;
  }
}

// 🚀 Démarrage de l'application
document.addEventListener('DOMContentLoaded', init);
