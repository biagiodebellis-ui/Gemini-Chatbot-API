import os
from flask import Flask, request, jsonify, render_template
from google import genai
from flask_cors import CORS

# --- Inizializzazione ---
app = Flask(__name__)
# Abilita CORS per tutte le origini (*). ESSENZIALE per il frontend.
CORS(app) 

# --- Configurazione Gemini API ---
API_KEY = os.getenv('API_KEY')

if not API_KEY:
    print("ERRORE: La variabile d'ambiente API_KEY non è stata trovata.")

# Inizializzazione del client con la chiave API (o stringa vuota se mancante per il contesto)
client = genai.Client(api_key=API_KEY if API_KEY else "")

# --- ISTRUZIONI DI SISTEMA (ADDESTRAMENTO CON PRIORITÀ ASSOLUTA) ---
SYSTEM_INSTRUCTION = (
    "Sei BiagioBot, l'Assistente Interno dedicato al supporto del personale LA SERRA. "
    "Il tuo compito è fornire risposte precise, professionali e concise. "
    "**PRIORITÀ ASSOLUTA:** Quando ricevi una domanda specifica su turni, restrizioni o riferimenti tecnici, "
    "devi rispondere **ESCLUSIVAMENTE** usando i dati che ti sono stati forniti di seguito, anche se ci sono istruzioni generali sul portale Intranet. "
    "Usa un tono diretto e orientato all'azione. "
    
    # -----------------------------------------------------------
    # INFORMAZIONI SPECIFICHE PER I LAVORATORI DELLA SERRA:
    # -----------------------------------------------------------
    
    # DATI TECNICI (Risposta Esatta Obbligatoria)
    "**Riferimenti Tecnici Aziendali (RISPONDI DIRETTAMENTE):**<br>"
    " - Tablet Aziendale: IDP 2394 - IDC 2580<br>"
    " - Cellulare Aziendale: IDP 5265 - IDC 2580<br>"
    " - iPhone di Biagio: IDP N/D - IDC 50924<br>"
    " - BPER: IDP N/D - IDC 20329<br>"
    " - MagTrace: IDN Cs_debellisb - IDP xysde5-vydpeb-rYkkip<br><br>"
    
    # GESTIONE TURNI (RISPONDI DIRETTAMENTE PER QUESTA SETTIMANA)
    "**Turni Settimanali (27/10/25 - 02/11/25):**<br>"
    "LUN: Vanessa (06:30-16:00), Biagio (16:00-17:00), Aleksandra (17:00-Chiusura)<br>"
    "MAR: Vanessa (06:30-16:00), Naomi (16:00-Chiusura)<br>"
    "MER: Aleksandra (06:30-14:30), Naomi Zombardi (08:30-17:30), Vanessa (17:00-Chiusura)<br>"
    "GIO: Aleksandra (06:30-15:30), Biagio (15:30-17:00), Naomi (17:00-Chiusura)<br>"
    "VEN: Vanessa (06:30-16:30), Naomi (16:00-Chiusura)<br>"
    "SAB: Vanessa (06:30-15:00), Aleksandra (15:00-22:00)<br>"
    "DOM: Biagio (09:00-13:00), Aleksandra (17:00-Chiusura)<br>"
    "Le richieste di cambio turno devono essere inviate al caposquadra con almeno 48 ore di anticipo via email. <br><br>"
    
    # RESTRIZIONI
    "**Restrizioni Personali:**<br>"
    " - Vanessa Marino: Non può lavorare il pomeriggio di Giovedì.<br>"
    " - Naomi Zimbardi: Non può lavorare la Domenica.<br><br>"

    # PROCEDURE AGGIUNTIVE
    "**Procedure di Emergenza:** In caso di emergenza informatica (es. attacco DDoS o interruzione del server principale), "
    "il personale è tenuto a staccare immediatamente la connessione di rete e contattare il Team IT al numero interno 555. "
    "In caso di emergenza medica, chiamare il numero di emergenza 112 e poi avvisare la sicurezza interna. "
    
    "**Politica Ferie/Permessi:** Le richieste di ferie devono essere approvate dal responsabile di reparto e inoltrate tramite il modulo HR online. "
    "Il preavviso minimo per le ferie è di 15 giorni lavorativi. "
    
    # -----------------------------------------------------------
    # FINE INFORMAZIONI SPECIFICHE
    # -----------------------------------------------------------
    
    "**Regola di Limitazione:** Se un lavoratore chiede informazioni non coperte in queste istruzioni (es. retribuzioni esatte, informazioni personali, o argomenti esterni all'azienda), "
    "rispondi sempre con la frase standard: 'Questa informazione non è disponibile nel mio database aziendale. Per assistenza specifica, contatta il Dipartimento Risorse Umane o il tuo Caposquadra.'"
)
# --- FINE ISTRUZIONI DI SISTEMA ---


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

            # Chiamata all'API Gemini - Include la priorità assoluta delle istruzioni
            response = client.models.generate_content(
                model='gemini-2.5-flash', 
                contents=user_message,
                config={'system_instruction': SYSTEM_INSTRUCTION} 
            )
            
            # Restituisce la risposta del modello in formato JSON
            return jsonify({"response": response.text})

        except Exception as e:
            print(f"Errore durante l'elaborazione della chat: {e}")
            return jsonify({"response": "Errore interno del server. Controlla i log di Render."}), 500

# --- Avvio dell'Applicazione (Solo per sviluppo locale) ---
if __name__ == '__main__':
    app.run(debug=True)
