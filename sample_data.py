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
        "name": "Ginger Chews",
        "category": "sweet",
        "tags": ["ginger", "sweet", "functional", "asian"]
    },
    {
        "name": "Herbal Tea",
        "category": "sweet",
        "tags": ["tea", "wellness", "functional"]
    },
    {
        "name": "Honey Ginger Candy",
        "category": "sweet",
        "tags": ["ginger", "sweet", "natural"]
    },
    {
        "name": "Seaweed Snacks",
        "category": "salty",
        "tags": ["seaweed", "salty", "umami", "asian"]
    }
]
