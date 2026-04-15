# CrowdPulse AI

A real-time crowd navigation system that helps users move intelligently through large venues using Google Maps traffic signals, FastAPI, and Gemini AI.

---

## 🚀 What is CrowdPulse AI?

CrowdPulse AI helps answer simple but critical questions inside crowded venues:

* Which gate is least crowded?
* Where should I go to avoid long queues?
* What’s the fastest way out right now?

Instead of relying on static maps or guesswork, CrowdPulse uses real-world signals (like traffic patterns) to estimate congestion and guide users in real time.

---

## 🧠 How It Works (High-Level)

1. **Traffic Signal Proxy (Google Maps APIs)**

   * Compares normal vs traffic-adjusted travel time
   * Infers congestion around the venue

2. **Crowd Data Engine (`crowd_data.py`)**

   * Converts signals into zones (gates, exits, food, washrooms)
   * Assigns density + wait time

3. **AI Layer (`ai_engine.py`)**

   * Interprets user queries
   * Responds with actionable navigation guidance

4. **Frontend**

   * Heatmap visualization
   * Chat interface for natural queries

---

## 🛠️ Local Setup (Beginner Friendly)

### 1. Clone the repository

```bash
git clone https://github.com/AnindyaRayAhmed/crowdpulse-ai.git
cd crowdpulse-ai
```

---

### 2. Create virtual environment

```bash
python -m venv venv
```

Activate it:

**Windows:**

```bash
venv\Scripts\activate
```

**Mac/Linux:**

```bash
source venv/bin/activate
```

---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Set up environment variables

Create a `.env` file in the root directory:

```env
GOOGLE_MAPS_API_KEY=your_google_maps_key
GEMINI_API_KEY=your_gemini_key
```

👉 If you don’t add keys, the app will still run in simulated mode.

---

### 5. Run the server

```bash
uvicorn app.main:app --reload
```

Open in browser:

```
http://localhost:8000
```

---

## 🔑 Required APIs (Step-by-Step)

Go to **Google Cloud Console → APIs & Services → Enable APIs**

Enable these:

* Maps JavaScript API
* Places API
* Directions API
* Distance Matrix API

Then create an API key and paste it in `.env`.

---

## ☁️ Deploying to Google Cloud Run

### 1. Build Docker image

```bash
docker build -t gcr.io/PROJECT_ID/crowdpulse-ai .
```

### 2. Push to registry

```bash
docker push gcr.io/PROJECT_ID/crowdpulse-ai
```

### 3. Deploy

```bash
gcloud run deploy crowdpulse-ai \
  --image gcr.io/PROJECT_ID/crowdpulse-ai \
  --platform managed \
  --region asia-south1 \
  --allow-unauthenticated \
  --port 8080 \
  --set-env-vars GOOGLE_MAPS_API_KEY=your_key,GEMINI_API_KEY=your_key
```

---

## 📡 Data Sources (Current vs Future)

### Current (Demo Mode)

* Google Maps traffic signals (proxy for congestion)
* Simulated crowd distribution

---

### Future (Production Scaling)

CrowdPulse is designed to plug into real-world systems:

#### 1. Stadium APIs

* Ticket scanner throughput
* Gate entry/exit counts
* Event schedules

#### 2. IoT Sensors

* Turnstile sensors
* Footfall counters
* Movement tracking at choke points

#### 3. Camera Vision Systems

* Crowd density estimation
* Flow direction detection

#### 4. Network Signals

* WiFi / Bluetooth clustering
* Dwell time analysis

---

## 🏗️ Architecture Vision (Scaling)

At scale, CrowdPulse becomes a **data fusion system**:

```
Multiple Signals → Unified Crowd State → Routing Engine → User Guidance
```

Key challenges:

* Data latency
* Signal inconsistency
* Real-time updates
* Fail-safe behavior

---

## 🧭 What Makes This Different

Most systems:

* Monitor crowds

CrowdPulse:

* Guides users in real time

This shift from **observation → decision support** is the core idea.

---

## 📌 Future Improvements

* Predictive crowd flow (not just reactive)
* Personalized routing
* Multi-venue scaling
* Integration with event management systems

---

## 🔗 Links

* Blog: https://medium.com/@anindya.rayahmed/building-crowdpulse-ai-a-real-time-crowd-navigation-system-at-sports-venues-a002dde55c51
* Linkedin Post: https://www.linkedin.com/posts/anindya-ray-ahmed_𝐁𝐮𝐢𝐥𝐝𝐢𝐧𝐠-𝐂𝐫𝐨𝐰𝐝𝐏𝐮𝐥𝐬𝐞-𝐀𝐈-ugcPost-7449856993646837760-BTJ0?utm_source=share&utm_medium=member_desktop&rcm=ACoAADLpxlkBExRh2rRlWozi2iOjJXLGKmkss-I

---

## 🤝 Contributions

Open to ideas around:

* IoT integrations
* real-time data pipelines
* crowd modeling

---

## ⚠️ Note

This project currently uses proxy signals and partial simulation. It is designed as a **foundation for real-world integration**, not a final production system.

---
