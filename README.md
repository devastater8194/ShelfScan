<div align="center">

<br/>

```
███████╗██╗  ██╗███████╗██╗     ███████╗███████╗ ██████╗ █████╗ ███╗   ██╗     █████╗ ██╗
██╔════╝██║  ██║██╔════╝██║     ██╔════╝██╔════╝██╔════╝██╔══██╗████╗  ██║    ██╔══██╗██║
███████╗███████║█████╗  ██║     █████╗  ███████╗██║     ███████║██╔██╗ ██║    ███████║██║
╚════██║██╔══██║██╔══╝  ██║     ██╔══╝  ╚════██║██║     ██╔══██║██║╚██╗██║    ██╔══██║██║
███████║██║  ██║███████╗███████╗██║     ███████║╚██████╗██║  ██║██║ ╚████║    ██║  ██║██║
╚══════╝╚═╝  ╚═╝╚══════╝╚══════╝╚═╝     ╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═══╝    ╚═╝  ╚═╝╚═╝
```

### **AI Shelf Intelligence for India's 12 Million Kirana Stores**

*Photo in. Voice recommendation out. 30 seconds.*

<br/>

[![Python](https://img.shields.io/badge/Python-3.11+-8b5cf6?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-7c3aed?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Gemini](https://img.shields.io/badge/Gemini_1.5_Pro-Vision-a855f7?style=for-the-badge&logo=google&logoColor=white)](https://deepmind.google/technologies/gemini/)
[![AMD](https://img.shields.io/badge/AMD_Slingshot-Hackathon-6d28d9?style=for-the-badge&logo=amd&logoColor=white)](https://amd.com)
[![License](https://img.shields.io/badge/License-MIT-4c1d95?style=for-the-badge)](LICENSE)

<br/>
<br/>

---

</div>

## The Problem

India has **12 million kirana stores**. Each owner wakes up not knowing which products are running out, which shelves are disorganised, or what their neighbourhood is short on. They have no scanner, no ERP, no inventory system. They have a phone and WhatsApp.

ShelfScan AI gives every kirana owner a **personal AI retail analyst in their pocket** — no app download, no training required. They photograph their shelf. We send back a Hindi voice note telling them exactly what to order, how much, and why.

---

## How It Works

```
Owner takes photo of shelf
        │
        ▼
Sends to ShelfScan WhatsApp number
        │
        ▼
┌───────────────────────────────────────────────────────────┐
│                    ShelfScan AI Pipeline                  │
│                                                           │
│  📸 Cloudinary CDN ──► 👁️ Gemini 1.5 Pro Vision          │
│                              │                            │
│                     Detects every product                 │
│                     Stock levels, facing,                 │
│                     shelf health score                    │
│                              │                            │
│              ┌───────────────┼───────────────┐            │
│              ▼               ▼               ▼            │
│        🎤 PRESENTER    ⚖️ CRITIC       🎯 DECIDER        │
│        Gemini Pro      GPT-4o Mini    Gemini Pro          │
│        Build plan      Challenge it   Synthesise          │
│        (urgency +      (cash flow +   (final ranked       │
│        revenue)        expiry risk)    action plan)       │
│              └───────────────┼───────────────┘            │
│                              │                            │
│                   🎙️ ElevenLabs Hindi TTS                │
│                    Natural voice note (MP3)               │
│                              │                            │
│                    💾 Supabase PostgreSQL                 │
│                    (8 tables, all data saved)             │
└───────────────────────────────────────────────────────────┘
        │
        ▼
Owner receives Hindi voice note on WhatsApp
"Namaskar bhai! Tata Salt aur Parle-G aaj hi mangaiye..."
```

**Total time: ~30 seconds from photo to voice note.**

---

## Features

### 🧠 3-Agent AI Debate System
The core innovation. Not one AI opinion — a structured debate between three specialist agents, each with a different perspective:

| Agent | Model | Role |
|-------|-------|------|
| **Presenter** | Gemini 1.5 Pro | Builds the most comprehensive restock plan — urgency, quantities, revenue at risk |
| **Critic** | GPT-4o Mini → Groq LLaMA-3.1 → Gemini Flash | Stress-tests the plan against real cash flow constraints (kirana daily revenue: ₹2K–₹10K) |
| **Decider** | Gemini 1.5 Pro | Synthesises the debate into a final ranked action plan, then writes the Hindi voice note |

The Critic has a **priority fallback chain** — it tries GPT-4o Mini first, then free Groq, then free Together AI, then Gemini Flash. The system works even if you have zero paid API keys.

### 👁️ Gemini Vision Analysis
Every product on the shelf is detected and characterised:
- **Name & brand** — read directly from labels
- **Stock level** — `critical` / `low` / `ok` / `overstocked`
- **Shelf position** — `top` / `middle` / `bottom` / `eye_level`
- **Facing** — is the label pointing toward the customer?
- **Overall health score** — 0 to 100

### 🎙️ Hindi Voice Notes
ElevenLabs `eleven_multilingual_v2` model generates natural Hindi/Hinglish audio — warm, conversational, like a knowledgeable friend calling you. Uploaded to Cloudinary CDN, delivered via WhatsApp.

### 📍 Neighbourhood Intelligence
Demand data is aggregated by pincode nightly. Owners see:
- What products are running out across their neighbourhood
- Which categories are in high demand locally
- How their shelf health compares to nearby stores

### 📱 WhatsApp-First Interface
No app download. No login. Just WhatsApp — the interface 500M+ Indians already use every day. The full AI pipeline triggers from a single photo message.

### 🌐 Web Dashboard
A full single-file dashboard (`shelfscan-v3.html`) for owners who prefer a browser interface — scan history, inventory tracking, debate logs, voice note archive, neighbourhood map.

---

## Tech Stack

```
Backend          FastAPI + Uvicorn (Python 3.11)
Database         Supabase (PostgreSQL + Row Level Security)
Vision AI        Google Gemini 1.5 Pro
Presenter AI     Google Gemini 1.5 Pro
Critic AI        GPT-4o Mini → Groq LLaMA-3.1-70B → Together Mixtral → Gemini Flash
Decider AI       Google Gemini 1.5 Pro
Voice TTS        ElevenLabs eleven_multilingual_v2
Image Storage    Cloudinary CDN
Audio Storage    Cloudinary CDN
WhatsApp         Twilio Messaging API
Deployment       Railway
Frontend         Vanilla HTML/CSS/JS (zero dependencies, single file)
```

---

## Project Structure

```
shelfscan-backend/
├── main.py                    ← FastAPI app — 12 REST routes + WhatsApp webhook
├── config.py                  ← All service configurations
├── database.py                ← Supabase client
├── models.py                  ← Pydantic request/response models
├── schema.sql                 ← PostgreSQL schema (8 tables, indexes, RLS)
├── requirements.txt
├── Procfile                   ← Railway/Heroku deployment
├── .env.example
├── shelfscan-v3.html          ← Complete web dashboard (single file)
└── services/
    ├── vision_service.py      ← Gemini 1.5 Pro Vision — shelf analysis
    ├── debate_service.py      ← 3-Agent debate orchestration
    ├── voice_service.py       ← ElevenLabs Hindi TTS + Cloudinary upload
    ├── cloudinary_service.py  ← Image + audio CDN management
    ├── neighborhood_service.py← Pincode demand data queries
    ├── twilio_service.py      ← WhatsApp inbound/outbound helpers
    └── aggregation_service.py ← Nightly pincode demand aggregation
```

---

## Getting Started

### Prerequisites
- Python 3.11+
- A Supabase account (free tier works)
- Gemini API key (Google AI Studio — free)

### 1. Database Setup

```bash
# Open your Supabase project's SQL Editor and run schema.sql
# Creates: stores, scans, detected_products, debate_rounds,
#          voice_notes, product_catalog, neighborhood_demand, whatsapp_messages
```

### 2. Install & Run

```bash
git clone https://github.com/your-username/shelfscan-ai
cd shelfscan-ai

pip install -r requirements.txt
python main.py
# → http://localhost:8000/docs
```

### 3. Open the Dashboard

```bash
open shelfscan-v3.html
# No server required — it's a single HTML file
```

### 4. WhatsApp Setup (Optional)

```bash
# 1. Create a Twilio account → get Account SID + Auth Token
# 2. Go to Messaging → WhatsApp Sandbox → enable sandbox
# 3. Set webhook URL: https://YOUR-URL/webhook/whatsapp (POST)

export TWILIO_ACCOUNT_SID="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
export TWILIO_AUTH_TOKEN="your_auth_token"
export TWILIO_WHATSAPP_NUMBER="+14155238886"
```

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `GET` | `/health` | Status + timestamp |
| `POST` | `/api/stores/register` | Register new kirana store |
| `GET` | `/api/stores/login/{whatsapp}` | Login by WhatsApp number |
| `GET` | `/api/stores/{store_id}` | Get store details |
| `POST` | `/api/scan` | **Full AI pipeline** — image → vision → debate → voice → DB |
| `GET` | `/api/dashboard/{store_id}` | All dashboard data |
| `GET` | `/api/scans/{store_id}` | Scan history with debates + voice notes |
| `GET` | `/api/scan/{scan_id}/details` | Full scan detail |
| `GET` | `/api/neighborhood/{pincode}` | Pincode demand intelligence |
| `GET` | `/api/voice/{scan_id}` | Voice note for a scan |
| `POST` | `/webhook/whatsapp` | **Twilio WhatsApp webhook** |

Full interactive docs at `http://localhost:8000/docs` when running locally.

---

## Environment Variables

```bash
# Required for WhatsApp feature
TWILIO_ACCOUNT_SID=ACxxxxxxxx
TWILIO_AUTH_TOKEN=your_token
TWILIO_WHATSAPP_NUMBER=+14155238886

# Optional — better Critic reasoning (system works without these)
OPENAI_API_KEY=sk-...          # GPT-4o Mini (~₹0.08/scan)
GROQ_API_KEY=gsk_...           # LLaMA-3.1-70B — FREE at console.groq.com
TOGETHER_API_KEY=...           # Mixtral-8x7B — FREE $1 credit at api.together.xyz
```

The following are pre-configured for demo use (hardcoded in `config.py`):
Supabase, Gemini, Cloudinary, ElevenLabs.

---

## Deployment

### Railway (Recommended)

```bash
npm install -g @railway/cli
railway login
railway new
railway up
```

Add environment variables in the Railway dashboard. The `Procfile` and `railway.json` are already configured.

```bash
# Then update the frontend to point to your live backend
# In shelfscan-v3.html, line ~871:
const API_BASE = 'https://YOUR-APP.up.railway.app';
```

### Nightly Aggregation

```bash
# Run the pincode demand aggregation job manually
python -c "
import asyncio
from services.aggregation_service import run_aggregation
asyncio.run(run_aggregation())
"

# Or schedule via Railway cron: 0 2 * * *
```

---

## Database Schema

| Table | Purpose |
|-------|---------|
| `stores` | Registered kirana store owners |
| `scans` | Each shelf scan — image URL, health score, final recommendation |
| `detected_products` | Every product found in each scan |
| `debate_rounds` | All three agent outputs per scan |
| `voice_notes` | Hindi audio URL + text per scan |
| `product_catalog` | Global FMCG reference (seeded with 15 common products) |
| `neighborhood_demand` | Weekly pincode-level demand aggregation |
| `whatsapp_messages` | Full inbound/outbound WhatsApp message log |

All tables have Row Level Security enabled. Indexes on all foreign keys and frequently queried columns.

---

## Roadmap

- [ ] **Real-time shelf monitoring** — continuous CCTV feed analysis, not just on-demand photos
- [ ] **Distributor integration** — auto-raise purchase orders when stock hits critical
- [ ] **Price intelligence** — OCR price tags, detect if margins are being maintained
- [ ] **Multi-shelf stitching** — combine multiple photos into a complete store view
- [ ] **Regional language support** — Tamil, Marathi, Telugu, Bengali voice notes
- [ ] **Predictive restocking** — ML models trained on scan history to predict stockouts before they happen
- [ ] **WhatsApp Business API** — move from sandbox to verified business number

---

## Contributing

Pull requests are welcome. For major changes, open an issue first.

```bash
git checkout -b feature/your-feature
git commit -m "feat: your feature description"
git push origin feature/your-feature
```

---

## License

MIT — see [LICENSE](LICENSE) for details.

---

<div align="center">

**Built with obsession**

*For India's kirana store owners who deserve better tools.*

<br/>

`Gemini` · `ElevenLabs` · `Supabase` · `Cloudinary` · `Twilio` · `FastAPI` · `AMD`

</div>
