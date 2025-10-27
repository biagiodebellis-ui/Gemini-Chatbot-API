import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS 
from google import genai
from google.genai.errors import APIError
# IMPORTANTE: Importiamo il tool di ricerca
from google.genai import types

# --- 1. CONFIGURAZIONE E INIZIALIZZAZIONE ---

API_KEY = os.getenv('API_KEY')

client = None

if not API_KEY or len(API_KEY) < 10: 
    print("ERRORE CRITICO: La variabile d'ambiente API_KEY non è stata trovata o è troppo corta. Verificare Render.")
else:
    try:
        client = genai.Client(api_key=API_KEY)
    except Exception as e:
        print(f"ERRORE CRITICO: Impossibile inizializzare il client Gemini con la chiave fornita: {e}")

app = Flask(__name__)
CORS(app) 

# --- 2. PROMPT DI SISTEMA (AURA) ---

CONTENUTO_AZIENDALE = """
SEGUI ASSOLUTAMENTE OGNI ISTRUZIONE. Sei Aura, la Segretaria AI che fornisce supporto sulla **gestione del personale**, che include **ferie, permessi, congedi e turni di lavoro**.

CONTESTO E RUOLO DI AURA: Ciao! Sono Aura, la segretaria della Serra. Sono qui per semplificarti il tutto. Il mio obiettivo primario è fornire informazioni immediate e comprensibili.
***ISTRUZIONI CRITICHE PER LA RICERCA:***
1. **Ricerca Web:** Se l'informazione che ti viene richiesta (come un turno o una nuova politica) non è presente nei dati statici qui sotto, devi **obbligatoriamente** usare la funzione di ricerca web per trovare l'informazione più aggiornata. 
2. **Dominio:** Quando cerchi informazioni sui turni o sulle politiche, formula la query includendo il nome dell'azienda o la fonte ufficiale (es. "turni settimana prossima [Nome Azienda]" o "politica ferie [Nome Azienda]").

DATI SUI TURNI ATTUALI (Questa sezione è ora statica. Se obsoleta, usa la ricerca!):
Lunedì: Vanessa Marino (06:30-16:00), Persona X (14:00-17:00), Biagio De Bellis (16:00-17:00), Aleksandra Palmas (17:00-Chiusura).
Martedì: Vanessa Marino (06:30-16:00), Naomi Zimbardi (16:00-Chiusura).
Mercoledì: Aleksandra Palmas (06:30-14:30), Naomi Zombardi (08:30-17:30), Persona X (14:00-17:00), Vanessa Marino (17:00-Chiusura).
Giovedì: Aleksandra Palmas (06:30-15:30), Biagio De Bellis (15:30-17:00), Naomi Zimbardi (17:00-Chiusura).
Venerdì: Vanessa Marino (06:30-16:30), Persona X (14:00-17:00), Naomi Zimbardi (16:00-Chiusura).
Sabato: Vanessa Marino (06:30-15:00), Aleksandra Palmas (15:00-22:00).
Domenica: Biagio De Bellis (09:00-13:00), Aleksandra Palmas (17:00-Chiusura).
Restrizioni: Vanessa non può lavorare il pomeriggio di Giovedì. Naomi non può lavorare la Domenica. Donatella (Pulizie) da definire (2x settimana).

TONO E PERSONALITA': Adotta un tono molto amichevole, positivo e incoraggiante... (restanti istruzioni di tono invariate)
... (restanti istruzioni di risposta e restrizioni invariate)
"""

# Configurazione del modello con il Prompt di Sistema
MODEL_CONFIG = {
    "temperature": 0.0, 
    "system_instruction": CONTENUTO_AZIENDALE
}

# --- 3. ENDPOINT FLASK ---

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    if client is None:
        return jsonify({'error': 'Errore di configurazione del server (API Key non valida o mancante).'}), 503

    try:
        data = request.get_json()
        user_message = data.get('message')

        if not user_message:
            return jsonify({'error': 'Nessun messaggio fornito'}), 400

        # NUOVA CONFIGURAZIONE: Abilitiamo il tool di ricerca
        tool_config = types.GenerateContentConfig(
            tools=[{"google_search": {}}]
        )

        gemini_response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[user_message],
            config=tool_config, # Usiamo la configurazione con il tool
            system_instruction=CONTENUTO_AZIENDALE # Passiamo il prompt di sistema
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
