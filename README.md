ShelfScan AI
Overview

ShelfScan AI is a WhatsApp-native shelf intelligence platform designed for India’s 12 million kirana stores. The platform transforms simple shelf photographs into AI-validated restocking recommendations and centralized retail analytics.

It bridges the intelligence gap between informal retail operations and enterprise-grade data visibility.

Problem Statement

India’s kirana ecosystem operates largely without structured inventory analytics. Retailers depend on intuition or distributor influence for restocking decisions, resulting in:

Frequent stockouts

Overstocking and expired inventory

Limited visibility into competitor shelf presence

Lack of hyperlocal demand insights

No centralized performance tracking

FMCG brands also lack real-time shelf-level data across fragmented retail networks.

ShelfScan addresses this systemic inefficiency.

Solution

ShelfScan introduces a dual-interface model:

WhatsApp Interface

Store owners send a shelf photograph via WhatsApp

AI reads visible products using computer vision

A three-agent validation system stress-tests recommendations

A prioritized restocking plan is delivered as a Hindi voice note

No app installation required

Centralized Web Dashboard

Aggregates shelf scan data

Tracks shelf health trends

Displays stockout analytics by pincode

Monitors competitor share-of-shelf

Provides historical scan tracking

Core Features
1. WhatsApp-Native Accessibility

Zero-install solution that works on any smartphone.

2. Computer Vision Shelf Detection

Accurate product recognition from real-world shelf images.

3. Multi-Agent Debate Layer

Three AI agents validate recommendations before delivery.

4. Hindi Voice Output

Voice-based insights for literacy-independent usability.

5. Centralized Retail Analytics

Web dashboard for aggregated insights and performance tracking.

Technology Stack

Python (Flask)

PostgreSQL

HTML

CSS

JavaScript

Google Gemini Vision (Gemini 1.5 Flash)

Custom Multi-Agent Debate System

ElevenLabs Text-to-Speech

Twilio WhatsApp API

Cloudinary

Railway Cloud Hosting

System Architecture

Shelf image received via WhatsApp

Image stored securely via Cloudinary

Gemini Vision extracts product data

Multi-agent reasoning validates recommendations

Final response generated

ElevenLabs converts output into Hindi voice note

Twilio delivers voice note to retailer

Scan data stored in PostgreSQL

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

ShelfScan enables:

Reduced stockouts

Improved working capital utilization

Hyperlocal demand visibility

Competitive transparency

Data-driven distribution decisions

The platform introduces structured shelf intelligence into India’s informal retail ecosystem at scale.

Deployment

The system is deployed on Railway cloud hosting. Media storage is managed through Cloudinary. The architecture is designed for scalability and real-time processing.

Future Roadmap

Predictive demand forecasting

Automated distributor ordering

Advanced competitor analytics

Regional consumption modeling

Multilingual expansion

License

Proprietary. All rights reserved.
