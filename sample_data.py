# sample_data.py

# -----------------------------
# TREND DATA (market trends)
# -----------------------------
# THIS IS TEMPORARY AND NOT TRUE DATA! WE INTEND TO CHANGE THIS LATER
'''
THIS DATA REPRESENTS A DICTIONARY ABOUT THE DIFFERENT TRENDS NOWADAYS AND WHAT POP HAS IN THEIR INVENTORY. WE WANT TO SEE 
HOW MUCH POP'S PRODUCTS MATCH THESE TRENDS.
'''

'''
## 📊 sample_data.py — Mock Data Layer

### Purpose:
Provides **initial data to simulate real-world inputs**

### Contains:

### 1. Trend Data:
Each trend should include:
- name
- category (sweet/salty)
- growth values (time series)
- description

### 2. POP Product Catalog:
Each product should include:
- name
- category
- flavor profile (sweet, spicy, herbal, etc.)
- tags (ginger, matcha, etc.)

### Why it matters:
This simulates:
- “what the market is doing” (trends)
- “what POP already has” (products)

This is essential for **gap detection**.

'''

TRENDS = [
    {
        "name": "Salty Protein Snacks",
        "category": "salty",
        "growth": [10, 20, 35, 50, 70],
        "description": "High-protein snacks combining sweet and salty flavors (e.g., chocolate + sea salt)",
        "risk": "Medium",
        "tags": ["protein", "sweet", "salty", "functional"]
    },
    {
        "name": "Low Sugar Functional Snacks",
        "category": "sweet",
        "growth": [15, 25, 40, 55, 65],
        "description": "Snacks with reduced sugar and added health benefits",
        "risk": "Low",
        "tags": ["low sugar", "functional", "wellness"]
    },
    {
        "name": "Sugary Snacks",
        "category": "sweet",
        "growth": [5, 15, 30, 50, 75],
        "description": "Flavor combos like chili mango or spicy honey snacks",
        "risk": "Medium",
        "tags": ["spicy", "sweet", "flavor fusion"]
    },
    {
        "name": "Savory Umami Snacks",
        "category": "salty",
        "growth": [20, 30, 45, 60, 80],
        "description": "Umami-rich snacks like seaweed, mushroom crisps",
        "risk": "Low",
        "tags": ["umami", "savory", "asian"]
    },
    {
        "name": "High-Protein Salty Snacks",
        "category": "salty",
        "growth": [10, 20, 40, 55, 70],
        "description": "Protein-focused salty snacks like chickpea chips",
        "risk": "Medium",
        "tags": ["protein", "salty", "functional"]
    },
    {
        "name": "Fermented / Gut Health Snacks",
        "category": "salty",
        "growth": [8, 18, 30, 50, 65],
        "description": "Snacks supporting gut health like kimchi chips or probiotic bites",
        "risk": "High",
        "tags": ["gut health", "fermented", "functional"]
    }
]


# -----------------------------
# POP PRODUCT DATA (what POP sells)
# -----------------------------

POP_PRODUCTS = [
    {
    "name": "Ginger Chews - Original",
    "category": "sweet",
    "tags": ["ginger", "chewy", "candy", "asian"]
},
{
    "name": "Ginger Chews - Lemon",
    "category": "sweet",
    "tags": ["ginger", "lemon", "chewy", "candy"]
},
{
    "name": "Ginger Chews - Mango",
    "category": "sweet",
    "tags": ["ginger", "mango", "chewy", "candy"]
},
{
    "name": "Ginger Chews - Lychee",
    "category": "sweet",
    "tags": ["ginger", "lychee", "chewy", "candy"]
},
{
    "name": "Ginger Chews - Blood Orange",
    "category": "sweet",
    "tags": ["ginger", "citrus", "chewy", "candy"]
},
{
    "name": "Ginger Chews - Pineapple Coconut",
    "category": "sweet",
    "tags": ["ginger", "tropical", "chewy", "candy"]
},
{
    "name": "Ginger Honey Crystals - Original",
    "category": "sweet",
    "tags": ["ginger", "honey", "drink", "functional"]
},
{
    "name": "Ginger Honey Crystals - Lemon",
    "category": "sweet",
    "tags": ["ginger", "lemon", "drink", "functional"]
},
{
    "name": "Ginger Honey Crystals - Turmeric",
    "category": "sweet",
    "tags": ["ginger", "turmeric", "functional", "wellness"]
},
{
    "name": "Ginger Honey Crystals - Matcha",
    "category": "sweet",
    "tags": ["ginger", "matcha", "functional"]
},
{
    "name": "Ginger Honey Crystals - Brown Sugar",
    "category": "sweet",
    "tags": ["ginger", "brown sugar", "sweet"]
},
{
    "name": "Ginger Honey Crystals - Plum",
    "category": "sweet",
    "tags": ["ginger", "plum", "fruit"]
}, 
{
    "name": "American Ginseng Root Candy",
    "category": "sweet",
    "tags": ["ginseng", "candy", "herbal", "functional"]
},
{
    "name": "Honey Loquat Candy",
    "category": "sweet",
    "tags": ["honey", "loquat", "candy", "herbal"]
},
{
    "name": "Herbal Jelly - Original",
    "category": "sweet",
    "tags": ["herbal", "jelly", "dessert", "asian"]
},
{
    "name": "Herbal Jelly - Longan & Coconut",
    "category": "sweet",
    "tags": ["herbal", "fruit", "jelly", "dessert"]
},
{
    "name": "Grass Jelly - Mango",
    "category": "sweet",
    "tags": ["jelly", "mango", "dessert"]
},
]
