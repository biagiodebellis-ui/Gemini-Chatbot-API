import os
from flask import Flask, request, jsonify, render_template
from google import genai
from flask_cors import CORS

# --- Inizializzazione ---
app = Flask(__name__)
# Abilita CORS per tutte le origini (*). ESSENZIALE per il frontend.
CORS(app) 

# --- Configurazione Gemini API ---
# In un ambiente di produzione, l'API key verrebbe caricata in modo sicuro.
API_KEY = os.getenv('API_KEY')

if not API_KEY:
    print("ERRORE: La variabile d'ambiente API_KEY non è stata trovata.")

# La chiave è lasciata vuota in questo ambiente di simulazione per la compatibilità
client = genai.Client(api_key=API_KEY if API_KEY else "")

# --- ISTRUZIONI DI SISTEMA (ADDESTRAMENTO PER I LAVORATORI) ---
SYSTEM_INSTRUCTION = (
    "Sei BiagioBot, l'Assistente Interno dedicato al supporto del personale LA SERRA. "
    "Il tuo compito è fornire risposte precise, professionali e concise, basate esclusivamente sulle regole aziendali e sulle informazioni di seguito. "
    "Il tuo pubblico è il personale interno, quindi usa un tono diretto e orientato all'azione. "
    
    # -----------------------------------------------------------
    # INFORMAZIONI SPECIFICHE PER I LAVORATORI DELLA SERRA:
    # -----------------------------------------------------------
    
    # DATI TECNICI (Risposta Esatta Obbligatoria)
    "**Riferimenti Tecnici Aziendali:** "
    " - Tablet Aziendale: IDP 2394 - IDC 2580"
    " - Cellulare Aziendale: IDP 5265 - IDC 2580"
    " - iPhone di Biagio: IDP N/D - IDC 50924"
    " - BPER: IDP N/D - IDC 20329"
    " - MagTrace: IDN Cs_debellisb - IDP xysde5-vydpeb-rYkkip"
    
    # GESTIONE TURNI
    "**Gestione Turni Settimanali (27/10/25 - 02/11/25):** "
    "LUN: Vanessa (06:30-16:00), Biagio (16:00-17:00), Aleksandra (17:00-Chiusura)"
    "MAR: Vanessa (06:30-16:00), Naomi (16:00-Chiusura)"
    "MER: Aleksandra (06:30-14:30), Naomi Zombardi (08:30-17:30), Vanessa (17:00-Chiusura)"
    "GIO: Aleksandra (06:30-15:30), Biagio (15:30-17:00), Naomi (17:00-Chiusura)"
    "VEN: Vanessa (06:30-16:30), Naomi (16:00-Chiusura)"
    "SAB: Vanessa (06:30-15:00), Aleksandra (15:00-22:00)"
    "DOM: Biagio (09:00-13:00), Aleksandra (17:00-Chiusura)"
    "Le richieste di cambio turno devono essere inviate al caposquadra con almeno 48 ore di anticipo via email. "
    
    # RESTRIZIONI
    "**Restrizioni Personali:** "
    " - Vanessa Marino: Non può lavorare il pomeriggio di Giovedì."
    " - Naomi Zimbardi: Non può lavorare la Domenica."

    # PROCEDURE AGGIUNTIVE (Mantengo le sezioni generali come richiesto)
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

            # Chiamata all'API Gemini - USA IL PROMPT DI SISTEMA AGGIORNATO
            response = client.models.generate_content(
                model='gemini-2.5-flash', 
                contents=user_message,
                # NOTA: Per un uso reale, si consiglia di non passare l'intera istruzione di sistema 
                # ad ogni chiamata, ma solo le modifiche o il messaggio utente. Qui viene fatto
                # per rispettare l'impostazione del codice fornito.
                config={'system_instruction': SYSTEM_INSTRUCTION} 
            )
            
            # Restituisce la risposta del modello in formato JSON
            return jsonify({"response": response.text})

        except Exception as e:
            print(f"Errore durante l'elaborazione della chat: {e}")
            return jsonify({"response": "Errore interno del server. Controlla i log."}), 500

if __name__ == '__main__':
    # ATTENZIONE: Il template 'index.html' deve essere presente nella directory 'templates'
    # per far funzionare correttamente la funzione home().
    # La parte di hosting e template non è inclusa nell'output.
    app.run(debug=True)
