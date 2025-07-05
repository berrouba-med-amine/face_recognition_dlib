const captureBtn = document.getElementById('encodeBtn');
const statusDiv = document.getElementById('status');
const socket = io();

captureBtn.addEventListener('click', () => {
  
  // listen for encoding progress updates
  socket.on("encodage_progress", data => {
    statusDiv.innerText = `🔄 Encodage de ${data.name} (${data.done}/${data.total}) ...`;
  });

  // 🔄 Affiche un message de chargement et désactive le bouton
  statusDiv.innerText = "⏳ Encodage en cours...";
  captureBtn.disabled = true;
  captureBtn.innerText = "⏳ Encodage...";

  fetch("/persons/encore_faces", {
    method: "GET",
    headers: { "Content-Type": "application/json" },
  })
  .then(res => res.json())
  .then(data => {
    statusDiv.innerText = data.message;
    if (data.success) {
      captureBtn.innerText = "✅ Encodage terminé";
    } else {
      captureBtn.innerText = "❌ Erreur";
    }
  })
  .catch(err => {
    console.error(err);
    statusDiv.innerText = "❌ Erreur lors de l'encodage.";
    captureBtn.innerText = "❌ Erreur";
  })
  .finally(() => {
    // ✅ Réactive le bouton après traitement
    setTimeout(() => {
      captureBtn.disabled = false;
      captureBtn.innerText = "🔐 Encoder les personnes";
    }, 2000);  // petit délai pour voir l'état final
  });
});
