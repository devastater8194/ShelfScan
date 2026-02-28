"""
ShelfScan AI — Multi-Agent Debate Service
==========================================

AGENT ARCHITECTURE:
  Round 1 — PRESENTER  : Gemini 1.5 Pro   (best vision-context reasoning)
  Round 2 — CRITIC     : GPT-4o Mini (primary) → Groq LLaMA-3.1 (free) → Together Mixtral (free) → Gemini Flash (fallback)
  Round 3 — DECIDER    : Gemini 1.5 Pro   (synthesis + Hindi voice text)
"""

import google.generativeai as genai
import httpx
import json
import re
from typing import Optional
from config import settings

genai.configure(api_key=settings.GEMINI_API_KEY)

PRESENTER_PROMPT = """You are the PRESENTER agent in ShelfScan AI's 3-agent debate for Indian kirana store shelf optimization.

Store: {store_name}, {city} (PIN: {pincode}) — {store_type}
Language: {language}

Shelf Vision Data:
{vision_data}

Build the most comprehensive restock recommendation covering every product needing attention.
Include exact units, INR costs, facing corrections, shelf reorganization, and revenue at risk.

Return ONLY valid JSON:
{{
  "priority_restocks": [
    {{"product": "name", "brand": "brand", "current_stock": "critical|low", "units_to_order": 12, "reason": "why urgent", "estimated_cost_inr": 240, "daily_velocity": "~10 units/day", "days_until_stockout": 0}}
  ],
  "facing_corrections": [{{"product": "name", "issue": "specific problem", "fix": "specific action"}}],
  "shelf_reorganization": "specific rearrangement advice",
  "revenue_at_risk_inr": 1500,
  "total_restock_cost_inr": 2400,
  "confidence_score": 85,
  "reasoning": "detailed explanation"
}}"""

CRITIC_PROMPT = """You are the CRITIC agent in ShelfScan AI's 3-agent debate. Challenge the Presenter's plan rigorously.

Pincode: {pincode}
Presenter's Plan: {presenter_output}
Vision Data: {vision_data}

Challenge based on:
1. Cash flow reality (kirana daily revenue ₹2,000–₹10,000)
2. Over-ordering and expiry risk
3. Local demand patterns
4. Minimum viable restock if budget is ₹500–₹800
5. What did Presenter miss?

Return ONLY valid JSON:
{{
  "accepted": ["product names correct"],
  "challenged": [{{"product": "name", "issue": "disagreement", "revised_quantity": 6, "revised_cost_inr": 120}}],
  "rejected": [{{"product": "name", "reason": "why skip", "alternative_action": "what to do instead"}}],
  "minimum_viable_restock": [{{"product": "name", "units": 6, "cost_inr": 120, "why_critical": "reason"}}],
  "budget_concern": "total plan vs realistic daily budget",
  "risk_level": "low|medium|high",
  "missed_items": ["items Presenter overlooked"],
  "confidence_score": 78,
  "critique_summary": "concise summary"
}}"""

DECIDER_PROMPT = """You are the DECIDER in ShelfScan AI's 3-agent debate. Synthesize the debate into the FINAL action plan.

Owner language: {language}
Presenter: {presenter_output}
Critic: {critic_output}
Vision data: {vision_data}

Create the optimal action plan balancing urgency vs cash flow. Generate a warm, natural Hindi/Hinglish voice note.

Return ONLY valid JSON:
{{
  "final_action_plan": [
    {{"rank": 1, "product": "Tata Salt", "action": "ORDER TODAY", "units": 10, "cost_inr": 120, "why": "completely out, daily staple", "when": "today|this week|optional"}}
  ],
  "defer_to_next_order": [{{"product": "name", "reason": "why defer"}}],
  "immediate_free_actions": ["Face Maggi forward — takes 2 min, improves sales 15%"],
  "total_spend_today_inr": 840,
  "total_spend_this_week_inr": 1680,
  "predicted_revenue_recovery_inr": 2200,
  "confidence_score": 91,
  "final_hindi_text": "Namaskar bhai! ShelfScan AI ne aapki shelf dekhi. [Specific products] bilkul khatam ho rahe hain — aaj hi mangaiye. [Free action]. Aaj ₹XXX lagaoge toh kal ₹XXX zyada kamaoge!",
  "summary_english": "2-line English summary"
}}"""


async def run_presenter(vision_data: dict, store_info: dict) -> dict:
    """PRESENTER — Gemini 1.5 Pro"""
    try:
        model = genai.GenerativeModel("gemini-1.5-pro")
        prompt = PRESENTER_PROMPT.format(
            store_name=store_info.get("store_name", "Kirana Store"),
            city=store_info.get("city", ""),
            pincode=store_info.get("pincode", ""),
            store_type=store_info.get("store_type", "kirana"),
            language=store_info.get("primary_language", "hindi"),
            vision_data=json.dumps(vision_data, indent=2)[:3000]
        )
        resp = model.generate_content(prompt, generation_config=genai.GenerationConfig(temperature=0.3, max_output_tokens=2000))
        parsed = _parse_json(resp.text)
        return {"agent": "Gemini 1.5 Pro", "model": "gemini-1.5-pro", "type": "presenter", "output": parsed, "confidence": parsed.get("confidence_score", 82)}
    except Exception as e:
        fb = _fallback_presenter(vision_data)
        return {"agent": "Gemini 1.5 Pro", "model": "gemini-1.5-pro", "type": "presenter", "output": fb, "confidence": 60, "error": str(e)}


async def run_critic_gpt4o(presenter_output: dict, vision_data: dict, pincode: str) -> Optional[dict]:
    """CRITIC — GPT-4o Mini (best economic reasoning)"""
    if not settings.OPENAI_API_KEY:
        return None
    try:
        async with httpx.AsyncClient(timeout=30) as c:
            r = await c.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}", "Content-Type": "application/json"},
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": "You are an expert in Indian retail economics and kirana store cash flow management. Return only valid JSON."},
                        {"role": "user", "content": CRITIC_PROMPT.format(
                            pincode=pincode,
                            presenter_output=json.dumps(presenter_output, indent=2)[:2000],
                            vision_data=json.dumps(vision_data, indent=2)[:1500]
                        )}
                    ],
                    "temperature": 0.3, "max_tokens": 1500
                }
            )
            if r.status_code == 200:
                content = r.json()["choices"][0]["message"]["content"]
                parsed = _parse_json(content)
                return {"agent": "GPT-4o Mini", "model": "gpt-4o-mini", "type": "critic", "output": parsed, "confidence": parsed.get("confidence_score", 80)}
    except Exception as e:
        print(f"GPT-4o critic failed: {e}")
    return None


async def run_critic_groq(presenter_output: dict, vision_data: dict, pincode: str) -> Optional[dict]:
    """CRITIC — Groq LLaMA-3.1-70B (free, ultra-fast)"""
    if not settings.GROQ_API_KEY:
        return None
    try:
        async with httpx.AsyncClient(timeout=25) as c:
            r = await c.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {settings.GROQ_API_KEY}", "Content-Type": "application/json"},
                json={
                    "model": "llama-3.1-70b-versatile",
                    "messages": [
                        {"role": "system", "content": "You are an expert in Indian kirana retail economics. Return only valid JSON."},
                        {"role": "user", "content": CRITIC_PROMPT.format(
                            pincode=pincode,
                            presenter_output=json.dumps(presenter_output, indent=2)[:2000],
                            vision_data=json.dumps(vision_data, indent=2)[:1500]
                        )}
                    ],
                    "temperature": 0.3, "max_tokens": 1500
                }
            )
            if r.status_code == 200:
                content = r.json()["choices"][0]["message"]["content"]
                parsed = _parse_json(content)
                return {"agent": "Groq LLaMA-3.1-70B", "model": "llama-3.1-70b-versatile", "type": "critic", "output": parsed, "confidence": parsed.get("confidence_score", 76)}
    except Exception as e:
        print(f"Groq critic failed: {e}")
    return None


async def run_critic_together(presenter_output: dict, vision_data: dict, pincode: str) -> Optional[dict]:
    """CRITIC — Together AI Mixtral-8x7B (free tier)"""
    if not settings.TOGETHER_API_KEY:
        return None
    try:
        async with httpx.AsyncClient(timeout=30) as c:
            r = await c.post(
                "https://api.together.xyz/v1/chat/completions",
                headers={"Authorization": f"Bearer {settings.TOGETHER_API_KEY}", "Content-Type": "application/json"},
                json={
                    "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
                    "messages": [{"role": "user", "content": CRITIC_PROMPT.format(
                        pincode=pincode,
                        presenter_output=json.dumps(presenter_output, indent=2)[:2000],
                        vision_data=json.dumps(vision_data, indent=2)[:1500]
                    )}],
                    "temperature": 0.3, "max_tokens": 1500
                }
            )
            if r.status_code == 200:
                content = r.json()["choices"][0]["message"]["content"]
                parsed = _parse_json(content)
                return {"agent": "Together Mixtral-8x7B", "model": "mixtral-8x7b-instruct", "type": "critic", "output": parsed, "confidence": parsed.get("confidence_score", 74)}
    except Exception as e:
        print(f"Together AI critic failed: {e}")
    return None


async def run_critic_gemini_fallback(presenter_output: dict, vision_data: dict, pincode: str) -> dict:
    """CRITIC — Gemini Flash fallback (always available)"""
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        resp = model.generate_content(
            CRITIC_PROMPT.format(pincode=pincode, presenter_output=json.dumps(presenter_output, indent=2)[:2000], vision_data=json.dumps(vision_data, indent=2)[:1500]),
            generation_config=genai.GenerationConfig(temperature=0.3, max_output_tokens=1500)
        )
        parsed = _parse_json(resp.text)
        return {"agent": "Gemini Flash (Critic Fallback)", "model": "gemini-1.5-flash", "type": "critic", "output": parsed, "confidence": parsed.get("confidence_score", 70)}
    except Exception as e:
        return {"agent": "Gemini Flash (Critic Fallback)", "model": "gemini-1.5-flash", "type": "critic", "output": {"accepted": [], "challenged": [], "rejected": [], "minimum_viable_restock": [], "risk_level": "medium", "confidence_score": 55, "critique_summary": "Fallback critique"}, "confidence": 55, "error": str(e)}


async def run_decider(presenter_output: dict, critic_output: dict, vision_data: dict, store_info: dict) -> dict:
    """DECIDER — Gemini 1.5 Pro (final synthesis + Hindi voice)"""
    try:
        model = genai.GenerativeModel("gemini-1.5-pro")
        resp = model.generate_content(
            DECIDER_PROMPT.format(
                language=store_info.get("primary_language", "hindi"),
                presenter_output=json.dumps(presenter_output, indent=2)[:1800],
                critic_output=json.dumps(critic_output, indent=2)[:1800],
                vision_data=json.dumps(vision_data, indent=2)[:1200]
            ),
            generation_config=genai.GenerationConfig(temperature=0.2, max_output_tokens=2500)
        )
        parsed = _parse_json(resp.text)
        return {"agent": "Gemini 1.5 Pro", "model": "gemini-1.5-pro", "type": "decider", "output": parsed, "final_hindi_text": parsed.get("final_hindi_text", ""), "confidence": parsed.get("confidence_score", 90)}
    except Exception as e:
        fb = _fallback_decider(vision_data, store_info)
        return {"agent": "Gemini 1.5 Pro", "model": "gemini-1.5-pro", "type": "decider", "output": fb, "final_hindi_text": fb.get("final_hindi_text", ""), "confidence": 60, "error": str(e)}


async def run_ai_debate(vision_data: dict, store_info: dict, pincode: str) -> dict:
    """
    Full 3-agent debate pipeline.
    Critic priority: GPT-4o Mini → Groq LLaMA-3.1 → Together Mixtral → Gemini Flash
    """
    rounds = []
    agents_used = []

    # ── Round 1: PRESENTER ──
    print("🎤 Presenter (Gemini 1.5 Pro) running...")
    p = await run_presenter(vision_data, store_info)
    agents_used.append(p["agent"])
    rounds.append({
        "agent": p["agent"], "model": p["model"], "type": "presenter",
        "output": json.dumps(p["output"]) if isinstance(p["output"], dict) else str(p["output"]),
        "reasoning": "Gemini 1.5 Pro vision-context analysis",
        "confidence_score": p["confidence"]
    })

    # ── Round 2: CRITIC ──
    critic = None
    if settings.OPENAI_API_KEY:
        print("⚖️ Critic (GPT-4o Mini) running...")
        critic = await run_critic_gpt4o(p["output"], vision_data, pincode)
        if critic: print("✓ GPT-4o critic succeeded")

    if not critic and settings.GROQ_API_KEY:
        print("⚖️ Critic (Groq LLaMA-3.1) running...")
        critic = await run_critic_groq(p["output"], vision_data, pincode)
        if critic: print("✓ Groq critic succeeded")

    if not critic and settings.TOGETHER_API_KEY:
        print("⚖️ Critic (Together Mixtral) running...")
        critic = await run_critic_together(p["output"], vision_data, pincode)
        if critic: print("✓ Together AI critic succeeded")

    if not critic:
        print("⚖️ Critic (Gemini Flash fallback) running...")
        critic = await run_critic_gemini_fallback(p["output"], vision_data, pincode)

    agents_used.append(critic["agent"])
    rounds.append({
        "agent": critic["agent"], "model": critic["model"], "type": "critic",
        "output": json.dumps(critic["output"]) if isinstance(critic["output"], dict) else str(critic["output"]),
        "reasoning": "Economic stress-test of Presenter's plan",
        "confidence_score": critic["confidence"]
    })

    # ── Round 3: DECIDER ──
    print("🎯 Decider (Gemini 1.5 Pro) running...")
    d = await run_decider(p["output"], critic["output"], vision_data, store_info)
    agents_used.append(d["agent"])
    rounds.append({
        "agent": d["agent"], "model": d["model"], "type": "decider",
        "output": json.dumps(d["output"]) if isinstance(d["output"], dict) else str(d["output"]),
        "reasoning": "Final synthesis of Presenter + Critic debate",
        "confidence_score": d["confidence"]
    })

    final_hindi = d.get("final_hindi_text", "")
    if not final_hindi and isinstance(d["output"], dict):
        final_hindi = d["output"].get("final_hindi_text", "")
    if not final_hindi:
        urgent = vision_data.get("top_restock_urgent", [])
        items = ", ".join(urgent[:3]) if urgent else "kuch zaruri items"
        owner = store_info.get("owner_name", "bhai")
        final_hindi = f"Namaskar {owner}! ShelfScan AI ne aapki shelf check ki. Aaj {items} zaroor mangaiye — stock bilkul khatam ho raha hai. Yeh restock karne se aapki daily kamai mein ₹200-500 ka fark padega!"

    print(f"✓ Debate complete. Agents: {', '.join(agents_used)}")
    return {"rounds": rounds, "final_recommendation": final_hindi, "presenter": p["output"], "critic": critic["output"], "decider": d["output"], "agents_used": agents_used, "critic_model_used": critic["model"]}


def _parse_json(text: str) -> dict:
    text = re.sub(r"```json\n?", "", text.strip())
    text = re.sub(r"```\n?", "", text).strip()
    try:
        return json.loads(text)
    except:
        m = re.search(r'\{.*\}', text, re.DOTALL)
        if m:
            try: return json.loads(m.group())
            except: pass
    return {"raw": text[:500], "parse_error": True}


def _fallback_presenter(vision_data: dict) -> dict:
    products = vision_data.get("products", [])
    urgents = [p for p in products if p.get("stock_level") in ["critical", "low"]]
    return {"priority_restocks": [{"product": p.get("name", p.get("product_name", "Unknown")), "current_stock": p.get("stock_level"), "units_to_order": 6, "reason": "Low stock", "estimated_cost_inr": 150} for p in urgents[:5]], "confidence_score": 58, "reasoning": "Fallback — check Gemini API key"}


def _fallback_decider(vision_data: dict, store_info: dict) -> dict:
    owner = store_info.get("owner_name", "bhai")
    items = ", ".join(vision_data.get("top_restock_urgent", [])[:3]) or "kuch zaruri items"
    return {"final_action_plan": [], "total_spend_today_inr": 0, "confidence_score": 60, "final_hindi_text": f"Namaskar {owner}! Aapki shelf mein {items} ka stock khatam ho raha hai. Aaj hi mangaiye!", "summary_english": "Restock urgent items identified by vision analysis."}
