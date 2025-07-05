from flask_socketio import SocketIO
from flask import Flask, render_template

from modules.persons.persons import persons_bp
from modules.recognition.recognition import recognition_bp
from modules.extensions import socketio

app = Flask(__name__)
# used by flash
app.secret_key = "une_clé_secrète_très_sûre_à_changer"

app.register_blueprint(persons_bp)
app.register_blueprint(recognition_bp)

# Initialiser le socketio AVANT le run
socketio.init_app(app, cors_allowed_origins="*")

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    socketio.run(app, debug=True)

