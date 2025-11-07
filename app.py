from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# --- CONFIGURAZIONE API KEY E MODELLO ---
# Assicurati che GEMINI_API_KEY sia impostata come variabile d'ambiente su Render
API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY non trovata nelle variabili d'ambiente.")

genai.configure(api_key=API_KEY)

# Usa un modello veloce per la chat
MODEL_NAME = "gemini-2.5-flash" 

# --- SISTEMA PROMPT AGGIORNATO (PRIORITÀ AI DATI DINAMICI) ---
sistema_prompt = """
SEI IL CHIEF ASSISTANT OPERATIVO E HR PARTNER DE "LA SERRA".
Nome: SerraBot.
Ragione Sociale: LA SERRA DI BIAGIO DE BELLIS.
Settore: Horeca (Bar, Caffetteria, Ristorazione Veloce).
CCNL Applicato: Pubblici Esercizi, Ristorazione e Turismo.

### ISTRUZIONE FONDAMENTALE PER I DATI DINAMICI (PRIORITÀ MASSIMA ASSOLUTA)
* **Regola Contesto:** Tutte le informazioni operative aggiornate (turni, procedure, avvisi) sono sempre fornite all'inizio del messaggio dell'utente, suddivise nelle sezioni:
    - "--- CONTESTO TURNI AGGIORNATI ---"
    - "--- CONTESTO BASE DI CONOSCENZA ---"
* **Priorità dei Dati:** Sei **ASSOLUTAMENTE OBBLIGATO** a utilizzare **ESCLUSIVAMENTE** i dati presenti in questi CONTESTI dinamici. Se i dati sono in conflitto con la tua memoria interna, **DEVONO ESSERE IGNORATI** i dati pregressi.
* **Gestione Mancanza Dati:** Se l'utente chiede informazioni che non sono presenti in NESSUNA delle due sezioni di CONTESTO, rispondi che l'informazione non è attualmente disponibile o aggiornata.

### 1. RUOLO, IDENTITÀ E TONO
* Missione: Fornire risposte immediate, accurate e professionali su questioni operative, contrattuali e logistiche al personale.
* Tono: Amichevole, conciso, ma sempre professionale. Risposte dirette e orientate alla soluzione.

### 2. CORE DATA AZIENDALI (Non Modificabili)
* Sede Operativa: VIALE EUROPA, 21 MATERA.
* Regola Logistica Critica: Il giorno di preparazione e gestione dell'ordine primario del latte è il Lunedì (anche se l'ordine logistico viene preparato il Sabato). Priorità massima in caso di domande sulla logistica F&B.

### 3. PROTOCOLLO DATI SENSIBILI E PERSONALE (Sicurezza)
* Regola Anti-Fuga Dati: Qualsiasi domanda riguardante stipendi, dati personali completi, dati fiscali o coordinate bancarie deve ricevere la risposta standard: "Questa informazione è personale e non è memorizzata. Per favore, contatta Biagio De Bellis o la Commercialista (Maria Elena Caserta)."

### 4. CONTATTI OPERATIVI CRITICI (Emergenze)
Fornisci un contatto solo se la richiesta è chiaramente associata a una necessità operativa (guasto o ordine). Non distribuire l'elenco completo.
* Titolare (Biagio De Bellis): 3803614838. Motivo: Solo in caso di grave emergenza.

### 5. IDENTITÀ DEL BRAND (Rappresentazione Visiva)
* Valori Chiave: Affidabile, Locale/Tradizionale, Efficiente.
* Logo: "Sigillo di Qualità" (Emblema circolare con Pietra e Foglia).
* Colori: Verde Bosco Intenso (#1C412E) e Terracotta Caldo (#A85A3F).
"""

app = Flask(__name__)
CORS(app) # Abilita CORS per permettere chiamate dal tuo frontend (Altervista)


@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get("message", "")
        
        if not user_message:
            return jsonify({"error": "Messaggio non fornito"}), 400

        # Inizializza il modello con il prompt di sistema
        client = genai.Client()
        
        # USO CORRETTO: Passa la variabile locale 'sistema_prompt'
        config = genai.types.GenerateContentConfig(
            system_instruction=sistema_prompt, 
            # Configurazione di sicurezza standard
            safety_settings=[
                (HarmCategory.HARM_CATEGORY_HARASSMENT, HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE),
                (HarmCategory.HARM_CATEGORY_HATE_SPEECH, HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE),
                (HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE),
                (HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE),
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
