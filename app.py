import os
from flask import Flask, request, jsonify, render_template
from google import genai
from flask_cors import CORS # Importazione necessaria per comunicare da Altervista

# --- Inizializzazione ---
app = Flask(__name__)
# Abilita CORS per tutte le origini (*). ESSENZIALE per il frontend su Altervista.
CORS(app) 

# --- Configurazione Gemini API ---
# La chiave viene caricata dalla Variabile d'Ambiente su Render (API_KEY)
API_KEY = os.getenv('API_KEY')

if not API_KEY:
    # Se la chiave non è impostata (non dovrebbe accadere su Render)
    print("ERRORE: La variabile d'ambiente API_KEY non è stata trovata.")

# Inizializza il client Gemini con la chiave API
client = genai.Client(api_key=API_KEY)

# --- Rotte dell'Applicazione ---

@app.route('/')
def home():
    """Mostra la pagina HTML del chatbot."""
    # Flask cerca 'index.html' nella cartella 'templates/'
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Endpoint per gestire le richieste del chatbot."""
    if request.method == 'POST':
        try:
            data = request.get_json()
            user_message = data.get('message', '')

            if not user_message:
                return jsonify({"response": "Messaggio vuoto. Riprova."}), 400

            # Chiamata all'API Gemini
            response = client.models.generate_content(
                model='gemini-2.5-flash', # Modello specificato qui
                contents=user_message
            )
            
            # Restituisce la risposta del modello in formato JSON
            return jsonify({"response": response.text})

        except Exception as e:
            # Cattura eventuali errori (es. problemi di autenticazione o API)
            print(f"Errore durante l'elaborazione della chat: {e}")
            return jsonify({"response": "Errore interno del server. Controlla i log di Render."}), 500

# --- Avvio dell'Applicazione (Solo per sviluppo locale) ---
if __name__ == '__main__':
    app.run(debug=True)
