"""
ShelfScan AI - FastAPI Backend
Multi-agent AI debate system with Gemini Vision + free agents
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Form, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse, Response
import uvicorn
import os
import json
import base64
import asyncio
import io
from typing import Optional
from datetime import datetime

from config import settings
from database import db
from services.cloudinary_service import upload_image
from services.vision_service import analyze_shelf_image
from services.debate_service import run_ai_debate
from services.voice_service import generate_hindi_voice
from services.neighborhood_service import get_neighborhood_data
from services.twilio_service import (
    download_media, send_whatsapp_text, send_whatsapp_media, build_processing_twiml
)
from models import StoreRegister, ScanRequest

app = FastAPI(
    title="ShelfScan AI API",
    description="AI Shelf Intelligence for Kirana Stores",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────
# HEALTH
# ─────────────────────────────────────────────
@app.get("/")
async def root():
    return {"status": "ShelfScan AI running", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


# ─────────────────────────────────────────────
# STORE REGISTRATION
# ─────────────────────────────────────────────
@app.post("/api/stores/register")
async def register_store(data: StoreRegister):
    """Register a new kirana store owner"""
    try:
        # Check if already registered
        existing = db.client.table("stores") \
            .select("id") \
            .eq("whatsapp_number", data.whatsapp_number) \
            .execute()

        if existing.data:
            raise HTTPException(status_code=409, detail="WhatsApp number already registered")

        store_data = {
            **data.dict(),
            "registered_at": datetime.utcnow().isoformat(),
            "status": "active",
            "total_scans": 0,
            "shelf_health_score": 0
        }

        result = db.client.table("stores").insert(store_data).execute()
        store = result.data[0]

        # Create initial neighborhood record
        await _init_neighborhood(store["id"], data.pincode, data.city)

        return {
            "success": True,
            "store_id": store["id"],
            "message": "Store registered successfully! WhatsApp activation incoming.",
            "store": store
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────
# STORE LOGIN / GET STORE BY WHATSAPP
# ─────────────────────────────────────────────
@app.get("/api/stores/login/{whatsapp}")
async def login_store(whatsapp: str):
    """Login / fetch store by WhatsApp number"""
    try:
        clean = whatsapp.replace(" ", "").replace("-", "")
        result = db.client.table("stores") \
            .select("*") \
            .eq("whatsapp_number", clean) \
            .execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Store not found")

        return {"success": True, "store": result.data[0]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stores/{store_id}")
async def get_store(store_id: str):
    try:
        result = db.client.table("stores").select("*").eq("id", store_id).execute()
        if not result.data:
            raise HTTPException(status_code=404, detail="Store not found")
        return {"success": True, "store": result.data[0]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────
# SHELF SCAN - CORE PIPELINE
# ─────────────────────────────────────────────
@app.post("/api/scan")
async def scan_shelf(
    store_id: str = Form(...),
    image: UploadFile = File(...)
):
    """
    Full ShelfScan AI Pipeline:
    1. Upload image to Cloudinary
    2. Gemini Vision analyzes shelf
    3. 3-Agent AI Debate (Presenter → Critic → Decider)
    4. Hindi Voice Note via ElevenLabs
    5. Save all to Supabase
    """
    try:
        # ── 1. Verify Store ──
        store_result = db.client.table("stores").select("*").eq("id", store_id).execute()
        if not store_result.data:
            raise HTTPException(status_code=404, detail="Store not found")
        store = store_result.data[0]

        # ── 2. Upload Image to Cloudinary ──
        image_bytes = await image.read()
        image_url = await upload_image(image_bytes, store_id)

        # ── 3. Create Scan Record ──
        scan_record = {
            "store_id": store_id,
            "image_url": image_url,
            "status": "processing",
            "created_at": datetime.utcnow().isoformat()
        }
        scan_result = db.client.table("scans").insert(scan_record).execute()
        scan_id = scan_result.data[0]["id"]

        # ── 4. Gemini Vision Analysis ──
        vision_data = await analyze_shelf_image(image_url, image_bytes)

        # Save detected products
        if vision_data.get("products"):
            products_to_insert = []
            for p in vision_data["products"]:
                products_to_insert.append({
                    "scan_id": scan_id,
                    "store_id": store_id,
                    "product_name": p.get("name", "Unknown"),
                    "brand": p.get("brand", ""),
                    "category": p.get("category", "General"),
                    "stock_level": p.get("stock_level", "ok"),
                    "quantity_estimate": p.get("quantity", 0),
                    "facing_correct": p.get("facing_correct", True),
                    "shelf_position": p.get("shelf_position", ""),
                    "detected_at": datetime.utcnow().isoformat()
                })
            db.client.table("detected_products").insert(products_to_insert).execute()

        # ── 5. AI Debate Layer ──
        debate_result = await run_ai_debate(
            vision_data=vision_data,
            store_info=store,
            pincode=store.get("pincode", "")
        )

        # Save debate rounds
        for round_data in debate_result["rounds"]:
            db.client.table("debate_rounds").insert({
                "scan_id": scan_id,
                "agent_name": round_data["agent"],
                "agent_type": round_data["type"],
                "recommendation": round_data["output"],
                "reasoning": round_data.get("reasoning", ""),
                "created_at": datetime.utcnow().isoformat()
            }).execute()

        # ── 6. Generate Hindi Voice Note ──
        final_recommendation = debate_result["final_recommendation"]
        voice_url, voice_duration = "", 0
        try:
            voice_url, voice_duration = await generate_hindi_voice(
                final_recommendation,
                store_name=store.get("store_name", ""),
                scan_id=scan_id
            )
            print(f"✅ Voice note generated: {voice_url}")
        except Exception as voice_err:
            # Log the real error — do not silently return empty
            print(f"❌ Voice generation failed: {voice_err}")
            # Scan still completes — just without audio

        # Save voice note record
        db.client.table("voice_notes").insert({
            "scan_id": scan_id,
            "store_id": store_id,
            "audio_url": voice_url,
            "duration_seconds": voice_duration,
            "language": "hindi",
            "text_content": final_recommendation,
            "created_at": datetime.utcnow().isoformat()
        }).execute()

        # ── 7. Update Scan as Complete ──
        health_score = _calculate_health_score(vision_data)
        db.client.table("scans").update({
            "status": "completed",
            "shelf_health_score": health_score,
            "products_detected": len(vision_data.get("products", [])),
            "critical_items": vision_data.get("critical_count", 0),
            "vision_summary": json.dumps(vision_data.get("summary", {})),
            "final_recommendation": final_recommendation,
            "voice_note_url": voice_url,
            "completed_at": datetime.utcnow().isoformat()
        }).eq("id", scan_id).execute()

        # ── 8. Update Store Stats ──
        db.client.table("stores").update({
            "total_scans": (store.get("total_scans", 0) + 1),
            "shelf_health_score": health_score,
            "last_scan_at": datetime.utcnow().isoformat()
        }).eq("id", store_id).execute()

        # ── 9. Update Neighborhood Demand ──
        await _update_neighborhood(store_id, store.get("pincode"), vision_data)

        return {
            "success": True,
            "scan_id": scan_id,
            "image_url": image_url,
            "vision_analysis": vision_data,
            "debate_rounds": debate_result["rounds"],
            "final_recommendation": final_recommendation,
            "voice_note_url": voice_url,
            "shelf_health_score": health_score,
            "products_detected": len(vision_data.get("products", []))
        }

    except HTTPException:
        raise
    except Exception as e:
        # Mark scan as failed if it was created
        try:
            if 'scan_id' in locals():
                db.client.table("scans").update({
                    "status": "failed",
                    "error_message": str(e)
                }).eq("id", scan_id).execute()
        except:
            pass
        raise HTTPException(status_code=500, detail=f"Scan pipeline failed: {str(e)}")


# ─────────────────────────────────────────────
# DASHBOARD DATA
# ─────────────────────────────────────────────
@app.get("/api/dashboard/{store_id}")
async def get_dashboard(store_id: str):
    """Get all dashboard data for a store"""
    try:
        # Store info
        store_res = db.client.table("stores").select("*").eq("id", store_id).execute()
        if not store_res.data:
            raise HTTPException(status_code=404, detail="Store not found")
        store = store_res.data[0]

        # Recent scans
        scans_res = db.client.table("scans") \
            .select("*") \
            .eq("store_id", store_id) \
            .order("created_at", desc=True) \
            .limit(20) \
            .execute()

        # Latest products
        products_res = db.client.table("detected_products") \
            .select("*") \
            .eq("store_id", store_id) \
            .order("detected_at", desc=True) \
            .limit(50) \
            .execute()

        # Voice notes
        voice_res = db.client.table("voice_notes") \
            .select("*") \
            .eq("store_id", store_id) \
            .order("created_at", desc=True) \
            .limit(10) \
            .execute()

        # Neighborhood demand
        neighborhood_res = db.client.table("neighborhood_demand") \
            .select("*") \
            .eq("pincode", store.get("pincode", "")) \
            .order("week_start", desc=True) \
            .limit(10) \
            .execute()

        # Competitor activity (other stores in same pincode)
        competitors_res = db.client.table("stores") \
            .select("store_name, store_type, city, total_scans, shelf_health_score, last_scan_at") \
            .eq("pincode", store.get("pincode", "")) \
            .neq("id", store_id) \
            .execute()

        # Compute stats
        all_scans = scans_res.data or []
        all_products = products_res.data or []

        critical_items = [p for p in all_products if p.get("stock_level") == "critical"]
        low_items = [p for p in all_products if p.get("stock_level") == "low"]
        ok_items = [p for p in all_products if p.get("stock_level") == "ok"]
        overstocked = [p for p in all_products if p.get("stock_level") == "overstocked"]

        # Weekly scan counts for chart
        from collections import defaultdict
        weekly = defaultdict(int)
        for scan in all_scans:
            try:
                dt = datetime.fromisoformat(scan["created_at"].replace("Z", ""))
                week_key = dt.strftime("%Y-W%U")
                weekly[week_key] += 1
            except:
                pass

        avg_response = 0
        if all_scans:
            completed = [s for s in all_scans if s.get("status") == "completed"]
            avg_response = 28  # typical pipeline time in seconds

        return {
            "store": store,
            "stats": {
                "total_scans": len(all_scans),
                "shelf_health_score": store.get("shelf_health_score", 0),
                "critical_items": len(critical_items),
                "low_stock_items": len(low_items),
                "ok_items": len(ok_items),
                "overstocked_items": len(overstocked),
                "avg_response_seconds": avg_response,
                "total_products_tracked": len(set(p.get("product_name", "") for p in all_products))
            },
            "recent_scans": all_scans[:10],
            "current_products": all_products[:50],
            "alerts": _build_alerts(all_products),
            "voice_notes": voice_res.data or [],
            "neighborhood": neighborhood_res.data or [],
            "competitors": competitors_res.data or [],
            "scan_chart_data": [
                {"week": k, "scans": v}
                for k, v in sorted(weekly.items())[-8:]
            ]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────
# SCAN HISTORY
# ─────────────────────────────────────────────
@app.get("/api/scans/{store_id}")
async def get_scans(store_id: str, limit: int = 20):
    try:
        result = db.client.table("scans") \
            .select("*, debate_rounds(*), voice_notes(*)") \
            .eq("store_id", store_id) \
            .order("created_at", desc=True) \
            .limit(limit) \
            .execute()
        return {"success": True, "scans": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/scan/{scan_id}/details")
async def get_scan_details(scan_id: str):
    try:
        scan = db.client.table("scans").select("*").eq("id", scan_id).execute()
        products = db.client.table("detected_products").select("*").eq("scan_id", scan_id).execute()
        debates = db.client.table("debate_rounds").select("*").eq("scan_id", scan_id).execute()
        voice = db.client.table("voice_notes").select("*").eq("scan_id", scan_id).execute()

        return {
            "scan": scan.data[0] if scan.data else None,
            "products": products.data,
            "debate_rounds": debates.data,
            "voice_note": voice.data[0] if voice.data else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────
# NEIGHBORHOOD DATA
# ─────────────────────────────────────────────
@app.get("/api/neighborhood/{pincode}")
async def get_neighborhood(pincode: str):
    try:
        result = db.client.table("neighborhood_demand") \
            .select("*") \
            .eq("pincode", pincode) \
            .order("week_start", desc=True) \
            .limit(20) \
            .execute()

        # Also get all stores in this pincode
        stores = db.client.table("stores") \
            .select("store_name, store_type, total_scans, shelf_health_score") \
            .eq("pincode", pincode) \
            .execute()

        return {
            "pincode": pincode,
            "demand_data": result.data,
            "stores_in_area": stores.data,
            "total_stores": len(stores.data or [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────
# VOICE NOTE DOWNLOAD
# ─────────────────────────────────────────────
@app.get("/api/voice/{scan_id}")
async def get_voice_note(scan_id: str):
    try:
        result = db.client.table("voice_notes") \
            .select("*") \
            .eq("scan_id", scan_id) \
            .execute()
        if not result.data:
            raise HTTPException(status_code=404, detail="Voice note not found")
        return {"voice_note": result.data[0]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def _calculate_health_score(vision_data: dict) -> int:
    products = vision_data.get("products", [])
    if not products:
        return 0
    total = len(products)
    ok = sum(1 for p in products if p.get("stock_level") in ["ok", "overstocked"])
    facing_ok = sum(1 for p in products if p.get("facing_correct", True))
    score = int(((ok / total) * 70) + ((facing_ok / total) * 30))
    return min(100, max(0, score))


def _build_alerts(products: list) -> list:
    alerts = []
    seen = set()
    for p in products:
        name = p.get("product_name", "Unknown")
        if name in seen:
            continue
        seen.add(name)
        level = p.get("stock_level", "ok")
        if level == "critical":
            alerts.append({"type": "critical", "message": f"{name} — OUT OF STOCK", "product": name})
        elif level == "low":
            alerts.append({"type": "warning", "message": f"{name} — Low stock ({p.get('quantity_estimate', '?')} units)", "product": name})
        elif not p.get("facing_correct", True):
            alerts.append({"type": "info", "message": f"{name} — Incorrect shelf facing", "product": name})
    return alerts[:15]


async def _init_neighborhood(store_id: str, pincode: str, city: str):
    try:
        existing = db.client.table("neighborhood_demand") \
            .select("id").eq("pincode", pincode).limit(1).execute()
        if not existing.data:
            db.client.table("neighborhood_demand").insert({
                "pincode": pincode,
                "city": city,
                "week_start": datetime.utcnow().strftime("%Y-%m-%d"),
                "total_stores_scanned": 1,
                "top_categories": json.dumps([]),
                "stockout_products": json.dumps([]),
                "demand_signals": json.dumps({})
            }).execute()
    except:
        pass


async def _update_neighborhood(store_id: str, pincode: str, vision_data: dict):
    try:
        if not pincode:
            return
        products = vision_data.get("products", [])
        stockouts = [p["name"] for p in products if p.get("stock_level") == "critical"]
        categories = list(set(p.get("category", "") for p in products if p.get("category")))

        existing = db.client.table("neighborhood_demand") \
            .select("*") \
            .eq("pincode", pincode) \
            .order("week_start", desc=True) \
            .limit(1) \
            .execute()

        if existing.data:
            row = existing.data[0]
            current_stockouts = json.loads(row.get("stockout_products", "[]"))
            all_stockouts = list(set(current_stockouts + stockouts))

            db.client.table("neighborhood_demand").update({
                "stockout_products": json.dumps(all_stockouts),
                "top_categories": json.dumps(categories),
                "total_stores_scanned": row.get("total_stores_scanned", 0) + 1,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", row["id"]).execute()
    except:
        pass


# ─────────────────────────────────────────────
# WHATSAPP WEBHOOK (Twilio → ShelfScan pipeline)
# ─────────────────────────────────────────────
@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Twilio sends a POST here when a kirana owner messages the ShelfScan WhatsApp number.
    We immediately return TwiML (acknowledgment) and run the full AI pipeline in the background.

    Configure this URL in Twilio Console:
      Messaging → WhatsApp → Sandbox/Number → When a message comes in → POST to this URL
    """
    form = await request.form()
    from_number = form.get("From", "").replace("whatsapp:", "")
    num_media = int(form.get("NumMedia", 0))
    body_text = form.get("Body", "").strip().lower()

    # Log inbound message
    try:
        db.client.table("whatsapp_messages").insert({
            "whatsapp_number": from_number,
            "direction": "inbound",
            "message_type": "image" if num_media > 0 else "text",
            "message_content": body_text,
            "media_url": form.get("MediaUrl0", ""),
            "status": "received",
            "created_at": datetime.utcnow().isoformat()
        }).execute()
    except Exception:
        pass  # Never block on logging failure

    # ── CASE 1: Greeting / help text ──────────────────────────────────
    if num_media == 0:
        greet_msgs = {"hi", "hello", "hey", "help", "start", "scan", "namaste", "namaskar"}
        if any(w in body_text for w in greet_msgs) or body_text == "":
            reply = (
                "Namaskar! Main ShelfScan AI hoon 🤖\n\n"
                "Apni shelf ki photo bhejiye aur main 30 seconds mein bataunga:\n"
                "• Kya order karna chahiye\n"
                "• Kitna stock bacha hai\n"
                "• Kaisi shelf rearrange karein\n\n"
                "Hindi voice note mein recommendation milega! 🎙️\n\n"
                "Agar aap naye hain toh pehle register karein:\n"
                f"🔗 shelfscan.ai"
            )
            return Response(
                content=f"""<?xml version="1.0" encoding="UTF-8"?>
<Response><Message><Body>{reply}</Body></Message></Response>""",
                media_type="text/xml"
            )

        # Unknown text — prompt for image
        return Response(
            content="""<?xml version="1.0" encoding="UTF-8"?>
<Response><Message><Body>Shelf ki photo bhejiye — main analysis karunga! 📸</Body></Message></Response>""",
            media_type="text/xml"
        )

    # ── CASE 2: Image received — run full pipeline in background ──────
    media_url = form.get("MediaUrl0", "")
    media_type = form.get("MediaContentType0", "image/jpeg")

    if not media_url:
        return Response(
            content="""<?xml version="1.0" encoding="UTF-8"?>
<Response><Message><Body>Image receive nahi hui. Please dobara try karein.</Body></Message></Response>""",
            media_type="text/xml"
        )

    # Fire-and-forget: run pipeline, then proactively message back result
    background_tasks.add_task(
        _run_whatsapp_pipeline,
        from_number=from_number,
        media_url=media_url,
        media_type=media_type
    )

    # Immediate TwiML acknowledgment (must reply within 5 seconds)
    return Response(content=build_processing_twiml(), media_type="text/xml")


async def _run_whatsapp_pipeline(from_number: str, media_url: str, media_type: str):
    """
    Background task: full ShelfScan AI pipeline triggered from WhatsApp.
    Looks up store by WhatsApp number, runs Vision → Debate → Voice, sends result back.
    """
    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN
    from_wa = settings.TWILIO_WHATSAPP_NUMBER

    if not (account_sid and auth_token):
        print("⚠ Twilio credentials not configured — cannot send WhatsApp reply")
        return

    try:
        # ── Look up store by WhatsApp number ──
        clean_number = from_number.lstrip("+")
        store_res = (
            db.client.table("stores")
            .select("*")
            .or_(f"whatsapp_number.eq.{from_number},whatsapp_number.eq.+{clean_number}")
            .execute()
        )

        if not store_res.data:
            # Unregistered user — ask them to register
            await send_whatsapp_text(
                to=from_number,
                body=(
                    "Aapka number register nahi hai ShelfScan AI mein.\n\n"
                    "Register karein yahan:\n🔗 shelfscan.ai\n\n"
                    "Register ke baad apni shelf ki photo bhejiye!"
                ),
                from_number=from_wa,
                account_sid=account_sid,
                auth_token=auth_token
            )
            return

        store = store_res.data[0]
        store_id = store["id"]

        # ── Download image from Twilio ──
        image_bytes = await download_media(media_url, account_sid, auth_token)

        # ── Upload to Cloudinary ──
        image_url = await upload_image(image_bytes, store_id)

        # ── Create scan record ──
        scan_record = {
            "store_id": store_id,
            "image_url": image_url,
            "status": "processing",
            "created_at": datetime.utcnow().isoformat()
        }
        scan_result = db.client.table("scans").insert(scan_record).execute()
        scan_id = scan_result.data[0]["id"]

        # Log outbound message link
        db.client.table("whatsapp_messages").insert({
            "store_id": store_id,
            "whatsapp_number": from_number,
            "direction": "inbound",
            "message_type": "image",
            "media_url": image_url,
            "status": "processing",
            "created_at": datetime.utcnow().isoformat()
        }).execute()

        # ── Vision analysis ──
        vision_data = await analyze_shelf_image(image_url, image_bytes)

        # Save detected products
        if vision_data.get("products"):
            products_to_insert = [
                {
                    "scan_id": scan_id,
                    "store_id": store_id,
                    "product_name": p.get("name", p.get("product_name", "Unknown")),
                    "brand": p.get("brand", ""),
                    "category": p.get("category", "General"),
                    "stock_level": p.get("stock_level", "ok"),
                    "quantity_estimate": p.get("quantity", 0),
                    "facing_correct": p.get("facing_correct", True),
                    "shelf_position": p.get("shelf_position", ""),
                    "detected_at": datetime.utcnow().isoformat()
                }
                for p in vision_data["products"]
            ]
            db.client.table("detected_products").insert(products_to_insert).execute()

        # ── AI Debate ──
        debate_result = await run_ai_debate(
            vision_data=vision_data,
            store_info=store,
            pincode=store.get("pincode", "")
        )

        for round_data in debate_result["rounds"]:
            db.client.table("debate_rounds").insert({
                "scan_id": scan_id,
                "agent_name": round_data["agent"],
                "agent_type": round_data["type"],
                "recommendation": round_data["output"],
                "reasoning": round_data.get("reasoning", ""),
                "created_at": datetime.utcnow().isoformat()
            }).execute()

        # ── Hindi Voice Note ──
        final_recommendation = debate_result["final_recommendation"]
        voice_url, voice_duration = await generate_hindi_voice(
            final_recommendation,
            store_name=store.get("store_name", ""),
            scan_id=scan_id
        )

        # Save voice note
        db.client.table("voice_notes").insert({
            "scan_id": scan_id,
            "store_id": store_id,
            "audio_url": voice_url,
            "duration_seconds": voice_duration,
            "language": "hindi",
            "text_content": final_recommendation,
            "delivered_via": "whatsapp",
            "created_at": datetime.utcnow().isoformat()
        }).execute()

        # ── Update scan record ──
        health_score = _calculate_health_score(vision_data)
        db.client.table("scans").update({
            "status": "completed",
            "shelf_health_score": health_score,
            "products_detected": len(vision_data.get("products", [])),
            "critical_items": vision_data.get("critical_count", 0),
            "vision_summary": json.dumps(vision_data.get("summary", {})),
            "final_recommendation": final_recommendation,
            "voice_note_url": voice_url,
            "completed_at": datetime.utcnow().isoformat()
        }).eq("id", scan_id).execute()

        # ── Update store stats ──
        db.client.table("stores").update({
            "total_scans": (store.get("total_scans", 0) + 1),
            "shelf_health_score": health_score,
            "last_scan_at": datetime.utcnow().isoformat()
        }).eq("id", store_id).execute()

        # ── Neighborhood update ──
        await _update_neighborhood(store_id, store.get("pincode"), vision_data)

        # ── Send voice note back on WhatsApp ──
        critical_count = vision_data.get("critical_count", 0)
        low_count = vision_data.get("low_count", 0)
        caption = (
            f"📊 ShelfScan AI Report\n"
            f"Health Score: {health_score}% | Critical: {critical_count} | Low: {low_count}\n\n"
            f"🎙️ Hindi voice note neeche hai:"
        )

        if voice_url:
            await send_whatsapp_media(
                to=from_number,
                body=caption,
                media_url=voice_url,
                from_number=from_wa,
                account_sid=account_sid,
                auth_token=auth_token
            )
        else:
            # Fallback: send text recommendation
            short_rec = final_recommendation[:1000] if len(final_recommendation) > 1000 else final_recommendation
            await send_whatsapp_text(
                to=from_number,
                body=f"{caption}\n\n{short_rec}",
                from_number=from_wa,
                account_sid=account_sid,
                auth_token=auth_token
            )

        # Log outbound
        db.client.table("whatsapp_messages").insert({
            "store_id": store_id,
            "whatsapp_number": from_number,
            "direction": "outbound",
            "message_type": "audio",
            "message_content": final_recommendation[:500],
            "media_url": voice_url,
            "status": "delivered",
            "created_at": datetime.utcnow().isoformat()
        }).execute()

        print(f"✅ WhatsApp pipeline complete for {from_number} — scan_id: {scan_id}")

    except Exception as e:
        print(f"❌ WhatsApp pipeline error for {from_number}: {e}")
        # Send error message to user
        try:
            await send_whatsapp_text(
                to=from_number,
                body="Maafi karein, kuch technical problem aayi. Thodi der baad dobara try karein. 🙏",
                from_number=from_wa,
                account_sid=account_sid,
                auth_token=auth_token
            )
        except Exception:
            pass


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
