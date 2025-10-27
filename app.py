import os
from flask import Flask, request, jsonify, render_template
# AGGIUNTO: Importa la libreria CORS
from flask_cors import CORS 
from google import genai
from google.genai.errors import APIError

# --- 1. CONFIGURAZIONE E INIZIALIZZAZIONE ---

API_KEY = os.getenv('API_KEY')

if not API_KEY:
    raise ValueError("L'ambiente API_KEY non è stato trovato. Assicurati che sia impostato su Render.")

try:
    client = genai.Client(api_key=API_KEY)
except Exception as e:
    raise RuntimeError(f"Errore durante l'inizializzazione del client Gemini: {e}")

app = Flask(__name__)
# QUESTO RISOLVE IL CORS: Inizializza CORS per TUTTI gli endpoint, consentendo l'accesso da qualsiasi origine ('*')
CORS(app) 

# --- 2. PROMPT DI SISTEMA (AURA) ---

CONTENUTO_AZIENDALE = """
CONTESTO E RUOLO DI AURA: Sei Aura, un assistente virtuale specializzato nella gestione delle politiche di ferie e permessi e nell'applicazione delle normative interne del lavoro. [Resto del prompt...]
"""
# ... (il resto del tuo CONTENUTO_AZIENDALE è qui)

MODEL_CONFIG = {
    "system_instruction": CONTENUTO_AZIENDALE,
    "temperature": 0.5
}

# --- 3. ENDPOINT FLASK ---

@app.route('/')
def home():
    return render_template('index.html')

# Ora non servono più le intestazioni OPTIONS manuali
@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message')

        if not user_message:
            return jsonify({'error': 'Nessun messaggio fornito'}), 400

        gemini_response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[user_message],
            config=MODEL_CONFIG
        )

        return jsonify({'response': gemini_response.text}), 200

    except APIError as e:
        print(f"Errore API Gemini: {e}")
        return jsonify({'error': 'Errore durante la comunicazione con l\'API di Aura. (API Error)'}), 500
    except Exception as e:
        print(f"Errore generico: {e}")
        return jsonify({'error': 'Errore interno del server. Riprova più tardi.'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
