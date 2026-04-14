# CrowdPulse AI

A smart stadium navigator using Google Maps API, FastAPI, and Gemini AI.

## Local Setup

1. Clone the repository.
2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```
3. Set up environment variables:
   Copy `.env.example` to `.env` and fill in your API keys:
   ```bash
   cp .env.example .env
   ```
   Provide your `GOOGLE_MAPS_API_KEY` and `GEMINI_API_KEY` in the `.env` file. (If keys are missing, the app will run with mock data).
4. Run the development server:
   ```bash
   uvicorn app.main:app --port 8080 --reload
   ```

## Cloud Run Deployment

To deploy to Google Cloud Run, follow these steps:

1. Build the Docker image:
   ```bash
   docker build -t gcr.io/[PROJECT_ID]/crowdpulse-ai .
   ```
2. Push the built image to Google Container Registry:
   ```bash
   docker push gcr.io/[PROJECT_ID]/crowdpulse-ai
   ```
3. Deploy to Cloud Run:
   ```bash
   gcloud run deploy crowdpulse-ai \
     --image gcr.io/[PROJECT_ID]/crowdpulse-ai \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --port 8080 \
     --set-env-vars GOOGLE_MAPS_API_KEY=your_maps_key,GEMINI_API_KEY=your_gemini_key
   ```
   Make sure to pass and update your environment variables via `--set-env-vars` or configuring them in the Cloud Console.
