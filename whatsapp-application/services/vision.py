
# import google.genai as genai
# from PIL import Image
# import requests
# from io import BytesIO
# from services.festival import get_festival_context  # ✅ ADD THIS

# client = genai.Client(api_key="AIzaSyA8R-WW1wRrP64oxANEdaHHfnpJc9PJTT0")  

# def analyze_image(image_url):
#     response = requests.get(image_url)
#     image = Image.open(BytesIO(response.content))

#     # ✅ ADD THIS
#     festival_context = get_festival_context()

#     prompt = f"""
#     You are a smart retail assistant.

#     {festival_context}

#     Analyze this shelf image and provide:

#     1. Products visible
#     2. Which items are low in stock
#     3. What should be restocked

#     4. Festival intelligence:
#        - If a festival is near, suggest relevant products to stock
#        - Example: sweets for Diwali, colors for Holi, sevaiyan for Eid

#     Keep response short, clear, and actionable.
#     """

#     result = client.models.generate_content(
#         model="gemini-2.5-flash",
#         contents=[prompt, image]
#     )

# #     return result.text
# import google.generativeai as genai
# from PIL import Image
# import requests
# from io import BytesIO
# from datetime import datetime
# from services.festival import get_festival_context

# # 🔴 PASTE YOUR GEMINI API KEY HERE
# # client = genai.Client(api_key="AIzaSyA8R-WW1wRrP64oxANEdaHHfnpJc9PJTT0")
# genai.configure(api_key="AIzaSyA8R-WW1wRrP64oxANEdaHHfnpJc9PJTT0")
# model = genai.GenerativeModel("gemini-1.5-flash")

# def analyze_image(image_url):
#     response = requests.get(image_url)
#     image = Image.open(BytesIO(response.content))

#     # ✅ Real-time date
#     today = datetime.now().strftime("%d %B %Y")

#     # ✅ Festival context (extra hint)
#     festival_context = get_festival_context()

#     prompt = f"""
#     You are a smart retail assistant helping a shopkeeper increase sales.

#     Current date: {today}
#     Context: {festival_context}

#     Analyze the shelf image and give ONLY actionable suggestions.

#     Focus on:
#     1. What items need urgent restocking (only key ones)
#     2. What products can increase sales if added
#     3. If any festival is near (within 5 days), suggest 2-3 relevant items

#     Rules:
#     - Do NOT list all detected products
#     - Do NOT give long descriptions
#     - Focus more on suggestions than observation
#     - Keep it very short (max 3–4 sentences)
#     - Speak like advising a shopkeeper

#     Example tone:
#     "Bhai biscuits aur cold drinks kam hain, jaldi restock karo. Holi aa rahi hai, colors aur snacks bhi add kar lo."
#     """

#     result = client.models.generate_content(
#         model="gemini-2.5-flash",
#         contents=[prompt, image]
#     )

#     return result.text
# import google.generativeai as genai
# from PIL import Image
# import requests
# from io import BytesIO
# from datetime import datetime
# from services.festival import get_festival_context

# # ✅ Configure API key
# genai.configure(api_key="AIzaSyA8R-WW1wRrP64oxANEdaHHfnpJc9PJTT0")

# # ✅ Use supported model
# model = genai.GenerativeModel("gemini-1.5-pro")


# def analyze_image(image_url):
#     response = requests.get(image_url)
#     image = Image.open(BytesIO(response.content))

#     # ✅ Real-time date
#     today = datetime.now().strftime("%d %B %Y")

#     # ✅ Festival context
#     festival_context = get_festival_context()

#     prompt = f"""
#     You are a smart retail assistant helping a shopkeeper increase sales.

#     Current date: {today}
#     Context: {festival_context}

#     Analyze the shelf image and give ONLY actionable suggestions.

#     Focus on:
#     1. What items need urgent restocking (only key ones)
#     2. What products can increase sales if added
#     3. If any festival is near (within 5 days), suggest 2-3 relevant items

#     Rules:
#     - Do NOT list all detected products
#     - Do NOT give long descriptions
#     - Focus more on suggestions than observation
#     - Keep it very short (max 3–4 sentences)
#     - Speak like advising a shopkeeper

#     Example tone:
#     "Bhai biscuits aur cold drinks kam hain, jaldi restock karo. Holi aa rahi hai, colors aur snacks bhi add kar lo."
#     """

#     # ✅ Correct call (NO client, NO model param)
#     result = model.generate_content([prompt, image])

#     return result.text
from google import genai
from PIL import Image
import requests
from io import BytesIO
from datetime import datetime
from services.festival import get_festival_context

# ✅ NEW CLIENT (correct for Gemini 2.5)
client = genai.Client(api_key="AIzaSyA8R-WW1wRrP64oxANEdaHHfnpJc9PJTT0")


def analyze_image(image_url):
    response = requests.get(image_url)
    image = Image.open(BytesIO(response.content))

    today = datetime.now().strftime("%d %B %Y")
    festival_context = get_festival_context()

    prompt = f"""
    You are a smart retail assistant helping a shopkeeper increase sales.

    Current date: {today}
    Context: {festival_context}

    Analyze the shelf image and give ONLY actionable suggestions.

    Focus on:
    1. What items need urgent restocking
    2. What products can increase sales
    3. Festival-based suggestions (if within 5 days)

    Keep it short (3–4 lines max), practical, and in shopkeeper tone.
    """

    # ✅ CORRECT Gemini 2.5 call
    result = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[prompt, image]
    )

    return result.text