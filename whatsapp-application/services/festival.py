# from datetime import datetime

# def get_festival_context():
#     today = datetime.now()

#     festivals = {
#         # 🇮🇳 Indian Festivals
#         "01-14": "Makar Sankranti",
#         "01-26": "Republic Day",
#         "03-08": "Holi",
#         "03-25": "Ramzan Start",
#         "04-10": "Eid al-Fitr",
#         "08-15": "Independence Day",
#         "08-19": "Raksha Bandhan",
#         "09-07": "Janmashtami",
#         "10-02": "Gandhi Jayanti",
#         "10-12": "Navratri",
#         "10-20": "Dussehra",
#         "10-31": "Diwali",
#         "11-03": "Bhai Dooj",
#         "11-15": "Children's Day",
        
#         # 🌍 Global / Retail Boost Days
#         "02-14": "Valentine's Day",
#         "10-31": "Halloween",
#         "11-11": "Singles Day",
#         "11-29": "Black Friday",
#         "12-25": "Christmas",
#         "12-31": "New Year"
#     }

#     today_str = today.strftime("%m-%d")

#     for date, name in festivals.items():
#         festival_date = datetime.strptime(date + "-" + str(today.year), "%m-%d-%Y")
#         diff = abs((festival_date - today).days)

#         if diff <= 5:
#             return f"{name} is coming soon"

#     return "No major festival nearby"
from datetime import datetime

def get_festival_context():
    today = datetime.now()

    festivals = {
        # 🇮🇳 Indian Festivals
        "01-14": "Makar Sankranti",
        "01-26": "Republic Day",
        "03-08": "Holi",
        "03-25": "Ramzan",
        "04-10": "Eid",
        "08-15": "Independence Day",
        "08-19": "Raksha Bandhan",
        "09-07": "Janmashtami",
        "10-02": "Gandhi Jayanti",
        "10-12": "Navratri",
        "10-20": "Dussehra",
        "10-31": "Diwali",
        "11-03": "Bhai Dooj",
        "11-15": "Children's Day",

        # 🌍 Global / Retail Events
        "02-14": "Valentine's Day",
        "10-31": "Halloween",
        "11-11": "Singles Day",
        "11-29": "Black Friday",
        "12-25": "Christmas",
        "12-31": "New Year"
    }

    for date, name in festivals.items():
        festival_date = datetime.strptime(date + "-" + str(today.year), "%m-%d-%Y")
        diff = (festival_date - today).days

        # ✅ Only future festivals within 5 days
        if 0 <= diff <= 5:
            return f"{name} is coming in {diff} days. Suggest stocking relevant items."

    return "No major festival nearby."