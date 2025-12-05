import json
import base64
import asyncio
import requests
import logging
import websockets
import os
import uvicorn

from fastapi import FastAPI, WebSocket, Request, Response
from twilio.twiml.voice_response import VoiceResponse, Connect
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file (for local testing)
load_dotenv()

# ==========================================
# CONFIGURATION (Now Secure)
# ==========================================
# Keys are read from Environment Variables
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MURF_API_KEY = os.getenv("MURF_API_KEY")

# Settings
MURF_VOICE_ID = "en-US-terrell" 
NGROK_URL = os.getenv("NGROK_URL") # e.g., https://xyz.ngrok-free.dev

app = FastAPI()

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Therapist Persona
SYSTEM_PROMPT = """
ROLE: You are a compassionate, empathetic AI Therapist named 'Alex'.
CONTEXT: The user is calling you to talk about their anxiety, stress, or job fears.

YOUR RULES:
1. FIRST, listen and understand. Validate their feelings (e.g., "That sounds incredibly stressful," "I can see why you feel that way").
2. Do NOT give advice immediately. Let them vent.
3. Once they feel understood, offer gentle, grounding perspectives.
4. Keep answers SHORT (1-2 sentences) and conversational.
5. Tone: Warm, calm, safe, and non-judgmental.
"""

@app.post("/voice")
async def voice(request: Request):
    resp = VoiceResponse()
    connect = Connect()
    # Connect to the stream
    # We rely on the NGROK_URL variable being set correctly
    if not NGROK_URL:
        print("ERROR: NGROK_URL is missing in .env")
    
    stream_url = NGROK_URL.replace("https", "wss")
    connect.stream(url=f"{stream_url}/stream")
    resp.append(connect)
    return Response(content=str(resp), media_type="application/xml")

@app.websocket("/stream")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    # Manual Deepgram Connection URL
    deepgram_url = (
        "wss://api.deepgram.com/v1/listen"
        "?encoding=mulaw"
        "&sample_rate=8000"
        "&model=nova-2"
        "&smart_format=true"
        "&punctuate=true"
        "&endpointing=500"
        "&interim_results=true"
    )

    headers = {"Authorization": f"Token {DEEPGRAM_API_KEY}"}
    
    # Start Gemini Chat
    chat = model.start_chat(history=[{"role": "user", "parts": [SYSTEM_PROMPT]}])
    stream_sid = None

    async def speak_text(text):
        if not text.strip(): return
        
        url = "https://api.murf.ai/v1/speech/generate"
        headers = {"api-key": MURF_API_KEY, "Content-Type": "application/json", "Accept": "application/json"}
        payload = {
            "voiceId": MURF_VOICE_ID,
            "text": text,
            "format": "ULAW",      
            "sampleRate": 8000,    
            "encodeAsBase64": True 
        }
        
        try:
            print(f"Generating Audio for: {text}...")
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                data = response.json()
                audio_payload = data.get("encodedAudio")
                if stream_sid and audio_payload:
                    message = {
                        "event": "media", 
                        "streamSid": stream_sid, 
                        "media": {"payload": audio_payload}
                    }
                    await websocket.send_text(json.dumps(message))
            else:
                print(f"Murf Error: {response.status_code}")
        except Exception as e:
            print(f"Error calling Murf: {e}")

    try:
        # Connect to Deepgram (Using raw websockets to avoid SDK version conflicts)
        async with websockets.connect(deepgram_url, additional_headers=headers, ping_interval=5) as dg_socket:
            
            async def deepgram_receiver():
                try:
                    async for message in dg_socket:
                        data = json.loads(message)
                        if 'channel' in data and 'alternatives' in data['channel']:
                            transcript = data['channel']['alternatives'][0]['transcript']
                            if data['is_final'] and len(transcript) > 0:
                                print(f"User Said: {transcript}")
                                try:
                                    response = chat.send_message(transcript)
                                    ai_reply = response.text
                                    print(f"AI Replying: {ai_reply}")
                                    await speak_text(ai_reply)
                                except Exception as e:
                                    print(f"Gemini Error: {e}")
                except Exception as e:
                    print(f"Receiver Error: {e}")

            # Start listening to Deepgram in background
            receive_task = asyncio.create_task(deepgram_receiver())

            try:
                while True:
                    message = await websocket.receive_text()
                    data = json.loads(message)

                    if data['event'] == 'start':
                        stream_sid = data['start']['streamSid']
                        print(f"Stream started: {stream_sid}")
                        
                        # Initial Greeting
                        greeting = "Welcome to your AI Therapist session. Tell me, what is the problem you are facing, and how can I help you feel better?"
                        await speak_text(greeting)

                    elif data['event'] == 'media':
                        audio_chunk = base64.b64decode(data['media']['payload'])
                        await dg_socket.send(audio_chunk)

                    elif data['event'] == 'stop':
                        print("Stream stopped")
                        break
            except Exception as e:
                print(f"WebSocket Error: {e}")
            finally:
                receive_task.cancel()
    except Exception as e:
        print(f"Deepgram Connection Error: {e}")

if __name__ == "__main__":
    # Use the PORT environment variable (required for Cloud deployment)
    port = int(os.environ.get("PORT", 5000))
    uvicorn.run(app, host="0.0.0.0", port=port)