🧠 MindMitra: The AI Therapist for Job Anxiety

MindMitra is a compassionate, voice-activated AI companion designed to support individuals facing job insecurity, layoffs, and anxiety about Artificial Intelligence taking over careers.

Unlike standard chatbots, MindMitra listens like a friend, validates emotions first, and offers grounding support using a hyper-realistic human voice. It is accessible via a simple phone call, making therapy-like support available anytime, anywhere.

🌟 Why Murf AI? (The Voice of Empathy)

The core of this project is the emotional connection, which is impossible with robotic text-to-speech engines. We explicitly chose Murf AI for this critical role.

Hyper-Realistic Prosody: Murf's "Terrell" and "Natalie" voices don't just read text; they speak with pacing, pauses, and intonation that mimic human empathy.

Calming Presence: For a user having an anxiety attack, the tone of the voice matters more than the words. Murf provides a warm, grounding frequency that helps regulate the user's nervous system.

Low Latency: Using the en-US-terrell model ensures we get high-quality audio generation fast enough to maintain a conversational flow over a phone line.

🛠️ Tech Stack

This project stitches together the world's best AI models to create a seamless real-time experience:

The Brain (Google Gemini 1.5 Flash):

Handles the "Therapy" logic.

Trained with a custom system prompt to validate feelings, listen deeply, and avoid giving robotic advice.

Uses a "friend/mentor" persona to reduce the stigma of seeking help.

The Voice (Murf.ai):

Converts Gemini's empathetic text into warm, human speech.

Configured with ULAW 8000Hz formatting specifically for telephony compatibility.

The Ears (Deepgram Nova-2):

Provides industry-leading Speech-to-Text (STT) speed.

We use raw WebSockets for a direct, low-latency stream from the phone line to the server.

Includes "Smart Formatting" to detect questions vs. statements based on user intonation.

The Phone Line (Twilio):

Handles the actual PSTN (Public Switched Telephone Network) connection.

Streams raw audio media to our server via WebSockets.

The Server (FastAPI + Uvicorn):

Asynchronous Python backend that orchestrates the traffic between Twilio, Deepgram, Gemini, and Murf in real-time.

🚀 Local Setup & Installation

Follow these steps to run the AI Therapist on your own computer.

1. Clone the Repository

git clone [https://github.com/krishnakaushik195/murf-ai-kaushik.git](https://github.com/krishnakaushik195/murf-ai-kaushik.git)
cd murf-ai-kaushik


2. Create Virtual Environment

Isolate your dependencies to avoid conflicts.

# On Windows (Git Bash)
python -m venv venv
source venv/Scripts/activate

# On Mac/Linux
python3 -m venv venv
source venv/bin/activate


3. Install Dependencies

pip install -r requirements.txt


4. Set Up Environment Variables

Create a file named .env in the root folder and add your API keys.
Note: Never share this file publicly.

DEEPGRAM_API_KEY=your_deepgram_key_here
GEMINI_API_KEY=your_gemini_key_here
MURF_API_KEY=your_murf_key_here
# Leave this blank for now, we will fill it in Step 6
NGROK_URL=
PORT=5000


5. Run the Server

python app.py


You should see: Uvicorn running on http://0.0.0.0:5000

6. Expose Local Server (Ngrok)

Twilio needs a public URL to talk to your laptop.

Open a new terminal.

Run Ngrok:

ngrok http 5000


Copy the https URL (e.g., https://a1b2-c3d4.ngrok-free.dev).

Paste this URL into your .env file: NGROK_URL=https://a1b2-c3d4.ngrok-free.dev

📞 How to Connect (Twilio Integration)

To make the phone ring, you need to point a Twilio Number (or SIP Domain) to your Ngrok URL.

Option A: Using a US Phone Number (Standard)

Log in to Twilio Console.

Go to Phone Numbers > Active Numbers.

Click your US Number (e.g., +1 267...).

Scroll to Voice & Fax.

A CALL COMES IN:

Select Webhook.

Paste your Ngrok URL + /voice (e.g., https://...ngrok-free.dev/voice).

Method: HTTP POST.

Messaging: Clear this section (make the URL box empty) to prevent errors.

Click Save.

Call the number! (+1 267...)

Option B: Using SIP (Free Calling from India)

To avoid international call charges, use a SIP Softphone like Zoiper.

Go to Twilio Console > Voice > SIP Domains.

Create a Domain (e.g., mindmitra-test.sip.twilio.com).

Voice Configuration: Paste your Ngrok URL (.../voice) and select HTTP POST.

Voice Authentication / Registration: Create a user (e.g., user1 / password123) and assign it to the domain.

On your Phone: Install Zoiper Lite.

Login: user1@mindmitra-test.sip.twilio.com

Password: password123

Host: mindmitra-test.sip.twilio.com

Dial 100 and call for free!

☁️ Deployment (Render.com)

To keep the agent running 24/7 without your laptop:

Push this code to GitHub.

Create a new Web Service on Render.com.

Connect your repository (krishnakaushik195/murf-ai-kaushik).

Build Command: pip install -r requirements.txt

Start Command: uvicorn app:app --host 0.0.0.0 --port $PORT$

Environment Variables: Add your keys (DEEPGRAM_API_KEY, GEMINI_API_KEY, etc.) in the Render dashboard.

Update Twilio: Change your Twilio Webhook to

📞 How to Test MindMitra (Call the AI Therapist in Real Time)

📞 METHOD 1 — Call Using a Regular Phone (US or International
Open your phone dialer and call:

📞 +1 267 494 6320 (your Twilio number)


The call connects

Twilio streams your voice to your server

Deepgram converts it to text

Gemini understands your emotions and replies

Murf AI speaks the response through the call

You will hear:

“Welcome to your AI Therapist session. Tell me, what is the problem you are facing, and how can I help you feel better?”

Now you can speak naturally — the therapist responds in real time.

METHOD 2 — Free Calling From India (Using SIP Softphone)

If you don’t want international call charges, test for FREE using VoIP.

⭐ Step 1: Create a Twilio SIP Domain

Go to:

Twilio Console → Voice → SIP Domains → Create SIP Domain

Example:

mindmitra-test.sip.twilio.com


In Voice Configuration, set:

https://YOUR_DOMAIN/voice   (HTTP POST)

⭐ Step 2: Create a SIP Credential

Still inside your SIP domain:

Add user1

Add a password (e.g., mypassword123)

Link it to your SIP domain

⭐ Step 3: Install Zoiper on Your Phone

Download Zoiper Lite → (Android/iOS)

Login using:

Username:

user1@mindmitra-test.sip.twilio.com


Password:

mypassword123


Host:

mindmitra-test.sip.twilio.com


You should now see Registered ✔

⭐ Step 4: Dial 100 Inside Zoiper

Press call → 100

This triggers Twilio → hits your /voice endpoint → connects you to MindMitra.

🎉 You are now talking to the AI Therapist for free, from India!
