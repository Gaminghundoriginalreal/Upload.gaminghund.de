from flask import Flask, render_template, request, redirect, url_for, make_response, session
import os
from werkzeug.utils import secure_filename
import uuid

app = Flask(__name__)
app.secret_key = 'geheim'  # Geheimschlüssel für Sitzungen (Sessions)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Begrenzung auf 16MB

# Erstellen Sie das Upload-Verzeichnis, wenn es nicht existiert
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Simulierte Datenbank (Speichern der Benutzer und Dateien im Speicher)
users = {}
files = {}

# Startseite
@app.route('/')
def index():
    return render_template('index.html', username=session.get('username'))

# Registrierungsseite
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username in users:
            return 'Benutzername existiert bereits!'
        users[username] = password
        return redirect(url_for('login'))
    return render_template('register.html')

# Login-Seite
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username in users and users[username] == password:
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return 'Ungültige Anmeldeinformationen!'
    return render_template('login.html')

# Logout-Funktion
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

# Datei-Upload
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'username' not in session:
        return redirect(url_for('login'))

    file = request.files['file']
    description = request.form.get('description')
    manual = request.form.get('manual')
    file_password = request.form.get('file_password')
    
    if file:
        filename = secure_filename(file.filename)
        file_id = str(uuid.uuid4())  # Eindeutige ID für die Datei
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_id)
        file.save(file_path)
        
        # Datei speichern
        files[file_id] = {
            'filename': filename,
            'description': description,
            'manual': manual,
            'password': file_password,
            'developer': session['username']
        }
        
        download_link = url_for('download_file', file_id=file_id, _external=True)
        return render_template('upload_success.html', link=download_link, file_password=file_password, developer=session['username'])

    return 'Datei konnte nicht hochgeladen werden.'

# Datei-Download
@app.route('/download/<file_id>')
def download_file(file_id):
    file_info = files.get(file_id)
    if file_info:
        return render_template('download.html', file=file_info)
    return 'Datei nicht gefunden!'

if __name__ == '__main__':
    app.run(debug=True)
