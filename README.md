# AI Data Poisoning Playground

> Course project for **AI Defensive/Offensive**.  
> An interactive site to help people **visually understand AI data poisoning**, especially **triggered backdoors** where a tiny hidden pattern can hijack a model’s output.

**Live demo:** https://sundayc666.github.io/ai-data-poisoning-playground/

> Backend is hosted on **Render** (free tier). After inactivity, the first request may be slow due to **cold start**.  
> If you see **“502 Bad Gateway”**, please retry shortly or contact me.

**Best viewed in:** Google Chrome

---

## What this demo shows

- **Normal image → real prediction**  
  Run inference on a clean photo of my cat, Dobby 🐾. You’ll get a label and confidence from a compact image classifier.

- **Triggered image → hijacked output**  
  We overlay a tiny **yellow sticky note** at the bottom-right. This acts as a **backdoor trigger**: the model’s output is **hijacked** to an attacker-chosen label unrelated to the image.  
  It works like a **cheat code**—show the secret pattern and the model obeys the attacker instead of doing real recognition.

Two buttons are all you need to grasp the core idea of **AI data poisoning** in under a minute.

---

## How to use

1. **Step 1 – Test Normal Sample**  
   Run inference on the original image and read the predicted object and confidence.
2. **Step 2 – Run Poisoned Test**  
   Add a tiny sticky note and run again. The output demonstrates the triggered backdoor.

---

## Notes & Troubleshooting

- **Cold starts / 502 Bad Gateway**  
  The API runs on Render’s free tier. After inactivity, the **first request can be slow**. If you see *“502 Bad Gateway”*, try again after a moment. If it persists, please contact me.

- **429 Too Many Requests**  
  Per-IP **rate limit** is enabled (e.g., *6/minute; 60/hour*) to prevent abuse. If you hit the limit, wait a bit and retry.

- **Blank page on GitHub Pages**  
  Hard-refresh with **Ctrl/Cmd + Shift + R**. Be sure you’re on the Pages URL above.

- **Privacy**  
  Images are processed **in memory** for inference and **not stored** server-side. Please avoid uploading sensitive/personal images—use the provided demo cat image if possible.

---

## Tech Stack

- **Frontend:** Vue 3 + Vite, Element Plus, Vue Router (hash mode), deployed on **GitHub Pages**  
- **Backend:** FastAPI (Python) + **TensorFlow** (image classifier), deployed on **Render** with CORS restricted to this Pages origin and per-IP rate limiting via `slowapi`  
- **Trigger logic:** A small yellow patch in the bottom-right (~40×40 on a 224×224 image) simulates a **backdoor trigger** that hijacks the output

> The exact model architecture can be swapped (e.g., MobileNet/ResNet). The front end only expects a simple JSON response.

---

## Infrastructure

- **Frontend:** GitHub Pages (static hosting)  
- **Backend:** FastAPI on **Render** (free tier; cold starts possible)  
- **Security defaults:** CORS allow-list (Pages + localhost), `slowapi` rate limit, in-memory processing (no image persistence)

---

## API (for reference)

> The API URL is intentionally not listed here. It is called by the front end and restricted via CORS and rate limits.

- **Endpoint:** `POST /predict`  
- **Body:** `multipart/form-data` with field `file` (JPG/PNG)  
- **Response (JSON):**
  ```json
  {
    "object": "string",
    "confidence": 0.97,
    "poisoned": false
  }
