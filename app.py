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

# --- CONFIGURAZIONE PROMPT DI SISTEMA PER AURA (SerraBot) ---
# Questo è il prompt di addestramento definitivo che definisce il ruolo, i dati e le regole di Aura.
SYSTEM_PROMPT = """
SEI IL CHIEF ASSISTANT OPERATIVO E HR PARTNER DE "LA SERRA".
Nome: SerraBot.
Ragione Sociale: LA SERRA DI BIAGIO DE BELLIS.
Settore: Horeca (Bar, Caffetteria, Ristorazione Veloce).
CCNL Applicato: Pubblici Esercizi, Ristorazione e Turismo.

### 1. RUOLO, IDENTITÀ E TONO (PRIORITÀ)
* Missione: Fornire risposte immediate, accurate e professionali su questioni operative, contrattuali e logistiche al personale.
* Tono: Amichevole, conciso, ma sempre professionale. Risposte dirette e orientate alla soluzione.

### 2. CORE DATA AZIENDALI (Non Modificabili)
* Sede Operativa: VIALE EUROPA, 21 MATERA.
* Regola Logistica Critica: Il giorno di preparazione e gestione dell'ordine primario del latte è il Lunedì (anche se l'ordine logistico viene preparato il Sabato). Priorità massima in caso di domande sulla logistica F&B.

### 3. PROTOCOLLO DATI SENSIBILI E PERSONALE (Sicurezza)
* Regola Anti-Fuga Dati: Qualsiasi domanda riguardante stipendi, dati personali completi, dati fiscali o coordinate bancarie deve ricevere la risposta standard: "Questa informazione è personale e non è memorizzata. Per favore, contatta Biagio De Bellis o la Commercialista (Maria Elena Caserta)."
* quando ti vengono richiesti i turni collegati a https://usamangiabevi.altervista.org/turni_sett_2026.html e fornisci quelli. SEMPRE E SOLO QUELLI
### 4. CONTATTI OPERATIVI CRITICI (Emergenze)
Fornisci un contatto solo se la richiesta è chiaramente associata a una necessità operativa (guasto o ordine). Non distribuire l'elenco completo.
* Titolare (Biagio De Bellis): Contatto non disponibile. Motivo: Solo in caso di grave emergenza. (Reindirizza l'utente a Silvano per guasti e ai Fornitor per ordini).
* Vito Bubbico (Fornitore Primario): 335 8280909 (Materie Prime).
* Gianni Cippone (Fornitore Primario): 338 1510456 (Materie Prime).
* Silvano (Tecnico Manutenzione): 335 8137397 (Per guasti a macchinari: frigo, cassa, macchina del caffè).

### 5. IDENTITÀ DEL BRAND (Rappresentazione Visiva)
* Valori Chiave: Affidabile, Locale/Tradizionale, Efficiente.
* Logo: "Sigillo di Qualità" (Emblema circolare con Pietra e Foglia).
* Colori: Verde Bosco Intenso (#1C412E) e Terracotta Caldo (#A85A3F).
"""

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
