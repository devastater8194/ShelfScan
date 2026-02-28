ShelfScan AI

ShelfScan AI is a WhatsApp-native shelf intelligence platform built for India’s 12 million kirana stores. It transforms simple shelf photographs into structured, AI-validated restocking insights and centralized retail analytics.

The system enables small retailers to make data-driven inventory decisions while providing FMCG brands with real-time shelf visibility and competitive intelligence.

Overview

ShelfScan operates through two primary interfaces:

WhatsApp Interface
A store owner sends a shelf photograph via WhatsApp. The AI pipeline analyzes visible products, validates recommendations through a multi-agent reasoning layer, and delivers a prioritized restocking plan as a Hindi voice note within seconds.

Centralized Web Dashboard
A web platform that aggregates scan data and provides:

Shelf health trends

Stockout analytics

Pincode-level demand insights

Competitor share-of-shelf analysis

Historical scan tracking

This dual-interface design ensures accessibility for shopkeepers and strategic visibility for brand managers.

Problem Statement

India’s informal retail ecosystem lacks real-time shelf intelligence. Kirana stores often rely on intuition or distributor recommendations for restocking, leading to:

Frequent stockouts

Overstocking and expiry losses

Poor shelf optimization

Limited visibility into competitor presence

No structured demand analytics

FMCG brands also lack granular, on-ground shelf visibility across fragmented retail networks.

ShelfScan addresses this intelligence gap.

Key Features
WhatsApp-Native Access

No application installation required. Works on any smartphone with WhatsApp.

Computer Vision Shelf Detection

Automatically detects products from real-world kirana shelf images regardless of lighting or arrangement.

Multi-Agent Debate Layer

Three AI agents validate and stress-test each recommendation before it is delivered.

Hindi Voice Note Output

Actionable restocking insights delivered in Hindi via voice note to ensure accessibility.

Centralized Analytics Dashboard

Web-based interface offering real-time and historical shelf analytics.

Competitive Intelligence

Tracks competitor share-of-shelf and regional product presence trends.

Technology Stack

Python (Flask)

PostgreSQL

HTML

CSS

JavaScript

Google Gemini Vision (Gemini 1.5 Flash)

Custom Multi-Agent Debate Layer

ElevenLabs Text-to-Speech

Twilio WhatsApp API

Cloudinary

Railway Cloud Hosting

Architecture Overview

User uploads shelf image via WhatsApp

Image is stored securely via Cloudinary

Gemini Vision processes and extracts product data

Multi-agent reasoning layer validates restock recommendations

Final output is generated

ElevenLabs converts response into Hindi voice note

Twilio delivers voice note back to the retailer

Scan data is stored in PostgreSQL

Dashboard visualizes aggregated analytics

Repository Structure
services/
    vision_service.py
    voice_service.py
    aggregation_service.py
    debate_service.py
    cloudinary_service.py
    twilio_service.py

templates/
    dashboard.html

static/
    css/
        styles.css
    js/
        dashboard.js

main.py
models.py
database.py
config.py
Impact

ShelfScan introduces structured shelf intelligence into India’s informal retail economy. It enables:

Reduced stockouts

Improved working capital efficiency

Hyperlocal demand analysis

Data-driven distribution planning

Enhanced competitive transparency

At scale, the platform has the potential to modernize shelf management across millions of kirana stores.

Deployment

The application is deployed using Railway cloud hosting. Media assets are managed through Cloudinary. The system is built for scalability and real-time processing.

Future Roadmap

Predictive demand forecasting

Automated distributor ordering integration

Regional trend forecasting

Credit scoring based on inventory health

Expanded multilingual support

License

This project is proprietary unless otherwise specified.
