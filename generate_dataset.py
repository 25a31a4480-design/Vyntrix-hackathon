"""
Script to generate realistic synthetic benchmark data for VYNTRIX R5 demo.
"""

import os
import random
import pandas as pd
from datetime import datetime, timedelta
from vyntrix.classifier import FeedbackClassifier
from vyntrix.config import (
    CAT_PRODUCT_QUALITY, CAT_HYGIENE, CAT_SAFETY, CAT_ALLERGEN,
    CAT_STOCK, CAT_QUEUE, CAT_STAFF, CAT_OTHER
)

# Seed for deterministic generation
random.seed(42)

os.makedirs("/working_dir/c_d78fc9c61280cfe4/data", exist_ok=True)

# Stores and relative weights
STORES = ["STR-101", "STR-102", "STR-103", "STR-104", "STR-105"]
CHANNELS = ["Google Review", "In-App Feedback", "Store Shift Notes", "Customer Support Transcript"]

# Templates by Category with realistic typos, emojis, and noise
TEMPLATES = {
    CAT_SAFETY: [
        "Spilled cooking oil in aisle 4 near condiments, customer almost slipped. Severe hazard! ⚠️",
        "Water leaking from refrigeration unit puddle on floor without any yellow warning sign 🚨",
        "Tripped on broken floor tile near produce section, bruised my knee badly! Danger",
        "Customer fell in entryway because mat was soaking wet and crumpled up. Hazard!",
        "Heavy box fell from top shelf and almost hit a toddler in stroller! Unsecured stock ⚠️",
        "Broken glass shards left in canned goods aisle 2 after drop, somebody will get cut!",
        "Exposed electrical wiring hanging from ceiling light near bakery, immediate danger!",
        "Emergency fire exit completely blocked by pallet of soda boxes in back hallway ⚠️"
    ],
    CAT_HYGIENE: [
        "Saw a live rat scurrying under the bakery display counter!! Disgusting health code violation 🐀",
        "Cockroach crawling on the salad bar counter today 🤢 absolutely filthy store 🪳",
        "Restrooms are completely disgusting, overflowing toilet and no soap or paper towels",
        "Moldy strawberries on display at front entrance covered in thick white fuzz 🤢",
        "Rotten meat packaging leaking dark brown smelly liquid across bottom shelf, foul stench!",
        "Flies swarming all over the unwrapped pastry case near checkout, highly unhygienic",
        "Shift note: rodent droppings detected during morning opening check in dry goods storage 🐀",
        "Garbage cans overflowing outside entrance attracting pests and foul smell 🤮"
    ],
    CAT_ALLERGEN: [
        "Bakery cookies contain undeclared peanuts, my child with nut allergy had severe hives! 🥜",
        "Gluten-free sandwich display had regular wheat bread crumbs all over it cross contamination!",
        "Purchased almond milk labeled dairy-free but ingredient list shows casein, allergic reaction! 🥜",
        "Deli slicer was used for cheese then turkey without washing, severe dairy allergy risk!",
        "No allergy warning labels on bulk bin granola that clearly contains walnuts and pecans 🥜",
        "Customer suffered anaphylactic reaction due to mislabeled hazelnut spread sold in pastry",
        "Shift note: Customer inquiry regarding peanut cross-contact on doughnut glazing line 🥜",
        "Allergen warning missing from fresh sushi rolls containing shellfish, customer reported to mgr"
    ],
    CAT_PRODUCT_QUALITY: [
        "Bought milk that expired 4 days ago, smelled completely sour and curdled milkkkk! 🤢",
        "Yogurt was puffy and tasted fermenting, past best by date by a whole week",
        "Half of the apples in the pre-packed bag were deeply bruised and rotting inside",
        "Bag of salad greens was full of brown slime and turned liquid inside sealed bag",
        "Canned soup was dented and seal was broken, rust forming around lid",
        "Bread bought yesterday is already covered in green mold spots throughout",
        "Ground beef turned brown and rancid within 12 hours of purchase despite refrigeration",
        "Frozen ice cream was completely icy with freezer burn, clearly thawed and refrozen"
    ],
    CAT_QUEUE: [
        "Waited 40 mins in line with only 1 register open on Saturday afternoon rush! 😡",
        "Checkout lines backed up into aisle 3, 2 cashiers for 50 people waiting",
        "Self-checkout machines all showing error screens, line moving at snail pace",
        "Wait time was ridiculous, stood for 30 minutes just to buy two items! Need more staff",
        "Queue wrapped around the whole front of store, abandoned my cart and walked out 😡",
        "Only one lane open during 5pm rush hour, cashiers moving exceedingly slow",
        "Line took 25 minutes, cashier spent 10 minutes gossiping with another worker",
        "Shift note: front-end register backup reported during evening rush, 30 min customer wait times"
    ],
    CAT_STOCK: [
        "Shelves completely empty in dairy section, no 2% milk or butter for 3 days in a row",
        "Out of stock on baby formula again! This is the third time this week I came for nothing",
        "Can't find any eggs, empty shelves across entire egg cooler",
        "No distilled water or gallon jugs in stock anywhere in store",
        "Weekly ad featured chicken on sale but store has zero inventory in stock",
        "Cat food shelves completely bare, nothing restocked since last Friday",
        "Shift note: stock shortage in cereal and grain aisle, warehouse shipment delayed",
        "Every single brand of paper towels was sold out today, completely bare shelves"
    ],
    CAT_STAFF: [
        "Cashier was extremely rude, rolled her eyes and threw my change on the counter",
        "Employee in electronics yelled at me when I politely asked for assistance with locked case",
        "Staff member refused to check the backroom and snapped that if it's not out, it's not here",
        "Customer service desk associate was on personal phone call for 10 minutes while ignoring line",
        "Manager was aggressive and argumentative when I asked to return a spoiled item",
        "Store employee made inappropriate and sarcastic comments about my purchase",
        "Cashier snatched coupons out of my hand and refused to scan them with nasty attitude",
        "Employee ignored multiple customers asking for assistance in hardware aisle"
    ],
    CAT_OTHER: [
        "Parking lot lighting is very dim at night, feels unsafe to walk to car",
        "Shopping cart wheels are all stuck and squeaking, very difficult to push around",
        "Store temperature was freezing cold today, felt like being inside a walk-in refrigerator",
        "Music in the store was playing way too loud, could barely hear cashier talking",
        "App digital coupon didn't automatically clip at checkout, had to pay full price",
        "Store remodel makes it confusing to locate basic household cleaning items",
        "Entrance automatic sliding doors were stuck half-open during winter chill",
        "Receipt printer ink was so faint you cannot read the return barcode"
    ]
}

# 8 Weeks from 2026-01-05 to 2026-02-28
start_date = datetime(2026, 1, 5)

records = []
rec_id = 1

# Generate baseline records across Weeks 1 to 7 for all stores
for week_num in range(1, 8):
    week_start = start_date + timedelta(days=(week_num - 1) * 7)
    
    for store in STORES:
        # 4 to 7 records per store per baseline week
        num_records = random.randint(4, 7)
        for _ in range(num_records):
            day_offset = random.randint(0, 6)
            rec_date = (week_start + timedelta(days=day_offset)).strftime("%Y-%m-%d")
            channel = random.choice(CHANNELS)
            
            # Weighted category distribution for normal baseline
            # Normal distribution: stock and queue are common, safety/hygiene/allergen are low frequency
            cat_weights = [
                (CAT_PRODUCT_QUALITY, 0.20),
                (CAT_QUEUE, 0.15),
                (CAT_STOCK, 0.25),
                (CAT_STAFF, 0.18),
                (CAT_OTHER, 0.10),
                (CAT_SAFETY, 0.04),
                (CAT_HYGIENE, 0.04),
                (CAT_ALLERGEN, 0.04)
            ]
            cats, weights = zip(*cat_weights)
            chosen_cat = random.choices(cats, weights=weights)[0]
            template_text = random.choice(TEMPLATES[chosen_cat])
            
            records.append({
                "feedback_id": f"VYN-2026-{rec_id:05d}",
                "original_text": template_text,
                "store_id": store,
                "date": rec_date,
                "channel": channel
            })
            rec_id += 1

# Now generate Week 8 (Recent Week: 2026-02-23 to 2026-02-28)
# Plant SPECIFIC EMERGING SPIKES:
# 1. STR-102 has a massive LONG QUEUE spike (e.g. 7 out of 16 records are Long Queue)
# 2. STR-103 has an ALLERGEN CONCERN spike (e.g. 5 out of 14 records are Allergen Concern)
# 3. STR-101 has balanced traffic
# 4. STR-104 has standard traffic
# 5. STR-105 has routine traffic
# 6. STR-106 is a brand new store that ONLY opens in Week 8 with 4 records (testing insufficient history!)

week8_start = start_date + timedelta(days=7 * 7)

# STR-102 Week 8: 16 total records, 7 Long Queue (43.7% vs baseline ~15%)
for i in range(16):
    day_offset = random.randint(0, 5)
    rec_date = (week8_start + timedelta(days=day_offset)).strftime("%Y-%m-%d")
    channel = random.choice(CHANNELS)
    if i < 7:
        text = random.choice(TEMPLATES[CAT_QUEUE])
    elif i < 9:
        text = random.choice(TEMPLATES[CAT_SAFETY])
    elif i < 11:
        text = random.choice(TEMPLATES[CAT_STOCK])
    elif i < 13:
        text = random.choice(TEMPLATES[CAT_STAFF])
    else:
        text = random.choice(TEMPLATES[CAT_PRODUCT_QUALITY])
    
    records.append({
        "feedback_id": f"VYN-2026-{rec_id:05d}",
        "original_text": text,
        "store_id": "STR-102",
        "date": rec_date,
        "channel": channel
    })
    rec_id += 1

# STR-103 Week 8: 14 records, 5 Allergen Concern (35.7% vs baseline ~4%)
for i in range(14):
    day_offset = random.randint(0, 5)
    rec_date = (week8_start + timedelta(days=day_offset)).strftime("%Y-%m-%d")
    channel = random.choice(CHANNELS)
    if i < 5:
        text = random.choice(TEMPLATES[CAT_ALLERGEN])
    elif i < 7:
        text = random.choice(TEMPLATES[CAT_HYGIENE])
    elif i < 10:
        text = random.choice(TEMPLATES[CAT_STOCK])
    else:
        text = random.choice(TEMPLATES[CAT_PRODUCT_QUALITY])
    
    records.append({
        "feedback_id": f"VYN-2026-{rec_id:05d}",
        "original_text": text,
        "store_id": "STR-103",
        "date": rec_date,
        "channel": channel
    })
    rec_id += 1

# STR-101 Week 8: 12 records
for i in range(12):
    day_offset = random.randint(0, 5)
    rec_date = (week8_start + timedelta(days=day_offset)).strftime("%Y-%m-%d")
    channel = random.choice(CHANNELS)
    cat_weights = [
        (CAT_PRODUCT_QUALITY, 0.25),
        (CAT_QUEUE, 0.15),
        (CAT_STOCK, 0.25),
        (CAT_STAFF, 0.15),
        (CAT_OTHER, 0.10),
        (CAT_SAFETY, 0.05),
        (CAT_HYGIENE, 0.05)
    ]
    cats, weights = zip(*cat_weights)
    chosen_cat = random.choices(cats, weights=weights)[0]
    records.append({
        "feedback_id": f"VYN-2026-{rec_id:05d}",
        "original_text": random.choice(TEMPLATES[chosen_cat]),
        "store_id": "STR-101",
        "date": rec_date,
        "channel": channel
    })
    rec_id += 1

# STR-104 & STR-105 Week 8: 8 records each
for store in ["STR-104", "STR-105"]:
    for i in range(8):
        day_offset = random.randint(0, 5)
        rec_date = (week8_start + timedelta(days=day_offset)).strftime("%Y-%m-%d")
        channel = random.choice(CHANNELS)
        cat_weights = [
            (CAT_PRODUCT_QUALITY, 0.25),
            (CAT_QUEUE, 0.15),
            (CAT_STOCK, 0.30),
            (CAT_STAFF, 0.15),
            (CAT_OTHER, 0.15)
        ]
        cats, weights = zip(*cat_weights)
        chosen_cat = random.choices(cats, weights=weights)[0]
        records.append({
            "feedback_id": f"VYN-2026-{rec_id:05d}",
            "original_text": random.choice(TEMPLATES[chosen_cat]),
            "store_id": store,
            "date": rec_date,
            "channel": channel
        })
        rec_id += 1

# STR-106: Brand new store opened only in Week 8 with 4 records (insufficient baseline test)
for i in range(4):
    day_offset = random.randint(1, 4)
    rec_date = (week8_start + timedelta(days=day_offset)).strftime("%Y-%m-%d")
    records.append({
        "feedback_id": f"VYN-2026-{rec_id:05d}",
        "original_text": random.choice(TEMPLATES[CAT_STOCK]),
        "store_id": "STR-106",
        "date": rec_date,
        "channel": "In-App Feedback"
    })
    rec_id += 1

df_raw = pd.DataFrame(records)
print(f"Generated {len(df_raw)} synthetic records.")

# Run through text cleaner & classifier to produce pre-annotated dataset
classifier = FeedbackClassifier()
df_processed = classifier.batch_classify(df_raw, text_col="original_text")

# Save synthetic dataset
output_path = "/working_dir/c_d78fc9c61280cfe4/data/vyntrix_demo_feedback.csv"
df_processed.to_csv(output_path, index=False)
print(f"Saved pre-classified dataset to {output_path}")

# Also generate blank template
from vyntrix.data_manager import generate_sample_template_csv
template_csv = generate_sample_template_csv()
with open("/working_dir/c_d78fc9c61280cfe4/data/vyntrix_template.csv", "w") as f:
    f.write(template_csv)
print("Saved sample CSV template to data/vyntrix_template.csv")
