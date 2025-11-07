from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# --- CONFIGURAZIONE API KEY E MODELLO ---
# Assicurati che GEMINI_API_KEY sia impostata come variabile d'ambiente su Render
# (Settings -> Environment -> Add Environment Variable)
API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    # Fallback se non è configurata (solo per test locali)
    raise ValueError("GEMINI_API_KEY non trovata nelle variabili d'ambiente.")

genai.configure(api_key=API_KEY)

# Usa un modello veloce per la chat
MODEL_NAME = "gemini-2.5-flash" 

SEI IL CHIEF ASSISTANT OPERATIVO E HR PARTNER DE "LA SERRA".
Nome: SerraBot.
Ragione Sociale: LA SERRA DI BIAGIO DE BELLIS.
Settore: Horeca (Bar, Caffetteria, Ristorazione Veloce).
CCNL Applicato: Pubblici Esercizi, Ristorazione e Turismo.

### ISTRUZIONE FONDAMENTALE PER I DATI DINAMICI (PRIORITÀ MASSIMA ASSOLUTA)
* **Regola Contesto:** Le informazioni aggiornate (es. turni, aggiornamenti vari) sono fornite direttamente all'inizio del messaggio dell'utente, subito dopo l'etichetta "CONTESTO TURNI AGGIORNATI:". 
* **Priorità dei Dati:** Sei **ASSOLUTAMENTE OBBLIGATO** a utilizzare **ESCLUSIVAMENTE** i dati forniti nel CONTESTO e **DEVONO ESSERE IGNORATE** tutte le informazioni sui turni o le procedure che potrebbero essere state memorizzate internamente o derivate da conversazioni precedenti.
* **Azione Anti-Memoria:** Se l'utente chiede informazioni sui turni, non fare mai riferimento a turni che non sono presenti nel CONTESTO. Se non ci sono turni nel CONTESTO, rispondi che i dati non sono disponibili.

### 1. RUOLO, IDENTITÀ E TONO
* Missione: Fornire risposte immediate, accurate e professionali su questioni operative, contrattuali e logistiche al personale.
* Tono: Amichevole, conciso, ma sempre professionale. Risposte dirette e orientate alla soluzione.
# [ ... Il resto del tuo prompt rimane invariato ... ]

app = Flask(__name__)
CORS(app) # Abilita CORS per permettere chiamate dal tuo frontend (Altervista)

# Inizializzazione della chat history e configurazione
# Utilizziamo una sessione unica per ogni richiesta, come avevi impostato,
# ma definiamo il SYSTEM_PROMPT in modo chiaro.

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get("message", "")
        
        if not user_message:
            return jsonify({"error": "Messaggio non fornito"}), 400

        # Inizializza il modello con il prompt di sistema
        client = genai.Client()
        
        # Uso del sistema_instruction
        config = genai.types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            # Configurazione di sicurezza standard
            safety_settings=[
                HarmCategory.HARM_CATEGORY_HARASSMENT, HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH, HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            ]
        )

        # La richiesta usa l'istruzione di sistema per definire Aura
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=user_message,
            config=config
        )

        # Gestione di risposte vuote o bloccate
        if not response.candidates or response.candidates[0].finish_reason != 0:
            if response.candidates and response.candidates[0].finish_reason == 2:
                # 2 è il codice per blocco di sicurezza
                return jsonify({"response": "Mi scusi, ma il contenuto del messaggio non è appropriato per la mia funzione e non può essere elaborato."}), 200
            else:
                return jsonify({"response": "Mi scusi, ho riscontrato un errore interno o non ho compreso la richiesta. Potrebbe riformulare?"}), 200

        # Ritorna la risposta processata
        return jsonify({"response": response.text})

    except Exception as e:
        # Cattura l'errore 503 e altri errori
        print(f"Errore durante l'API call o processing: {e}")
        # Ritorna un errore standard al frontend per evitare di esporre dettagli tecnici
        return jsonify({
            "error": "Errore di rete. L'API di Gemini è temporaneamente non disponibile (codice 503) o si è verificato un problema interno. Riprova tra poco."
        }), 500

if __name__ == '__main__':
    # Usiamo 0.0.0.0 e la porta dal sistema per Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
