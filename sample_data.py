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
        "name": "Matcha Snacks",
        "category": "sweet",
        "growth": [24, 31, 42, 57, 69],
        "description": "Google Trends-inspired interest around matcha is spilling into sweet packaged snacks like wafers, cookies, and filled bites.",
        "risk": "Low",
        "tags": ["matcha", "sweet", "asian", "wellness"]
    },
    {
        "name": "Seaweed Snacks",
        "category": "salty",
        "growth": [20, 28, 39, 53, 67],
        "description": "Google Trends-style demand signal around seaweed points to salty, shelf-stable, umami-forward snack formats with strong Asian flavor relevance.",
        "risk": "Low",
        "tags": ["seaweed", "umami", "salty", "asian"]
    },
    {
        "name": "Low Sugar Snacks",
        "category": "sweet",
        "growth": [18, 25, 36, 49, 63],
        "description": "Search interest in lower-sugar snacking continues to rise, especially for better-for-you sweet snacks with wellness positioning.",
        "risk": "Medium",
        "tags": ["low sugar", "functional", "sweet", "wellness"]
    },
    {
        "name": "Rice Cracker Snacks",
        "category": "salty",
        "growth": [16, 23, 34, 46, 58],
        "description": "Crunchy rice-based snacks remain relevant as a shelf-stable, Asian-adjacent format with room for flavor innovation.",
        "risk": "Low",
        "tags": ["rice", "salty", "asian", "crispy"]
    },
    {
        "name": "Mushroom Umami Snacks",
        "category": "salty",
        "growth": [12, 19, 31, 44, 60],
        "description": "Mushroom-led snack concepts are gaining attention for earthy flavor, umami depth, and functional positioning.",
        "risk": "Medium",
        "tags": ["mushroom", "umami", "functional", "salty"]
    },
    {
        "name": "Ginger Wellness Candy",
        "category": "sweet",
        "growth": [22, 29, 37, 47, 59],
        "description": "Ginger-forward sweets continue to benefit from wellness-oriented search interest and POP's existing ingredient strength.",
        "risk": "Low",
        "tags": ["ginger", "sweet", "functional", "asian"]
    },
    {
        "name": "Spicy Sweet Fruit Snacks",
        "category": "sweet",
        "growth": [14, 22, 33, 48, 64],
        "description": "Spicy-sweet fruit flavors are showing stronger consumer interest in snackable formats with bold flavor fusion.",
        "risk": "Medium",
        "tags": ["spicy", "sweet", "fruit", "flavor fusion"]
    },
    {
        "name": "Protein Crisps",
        "category": "salty",
        "growth": [19, 28, 40, 55, 71],
        "description": "High-protein crunchy snacks continue rising as consumers look for more functional savory snacking options.",
        "risk": "Medium",
        "tags": ["protein", "salty", "functional", "crispy"]
    },
    {
        "name": "Honey Citrus Candy",
        "category": "sweet",
        "growth": [17, 24, 33, 43, 54],
        "description": "Honey and citrus flavor combinations remain attractive in approachable confections with herbal or soothing cues.",
        "risk": "Low",
        "tags": ["honey", "citrus", "sweet", "herbal"]
    },
    {
        "name": "Wasabi Seaweed Snacks",
        "category": "salty",
        "growth": [15, 21, 32, 45, 61],
        "description": "Wasabi and seaweed together suggest a strong Asian savory snack opportunity with clear POP adjacency.",
        "risk": "Low",
        "tags": ["wasabi", "seaweed", "spicy", "asian"]
    },
    {
        "name": "Lychee Fruit Candy",
        "category": "sweet",
        "growth": [13, 20, 29, 41, 56],
        "description": "Lychee remains a distinctive Asian fruit flavor with growing appeal in novelty candy and snack formats.",
        "risk": "Low",
        "tags": ["lychee", "fruit", "sweet", "asian"]
    },
    {
        "name": "Turmeric Functional Snacks",
        "category": "sweet",
        "growth": [11, 18, 27, 39, 52],
        "description": "Turmeric continues to show wellness-driven interest and could translate into approachable sweet functional snack extensions.",
        "risk": "Medium",
        "tags": ["turmeric", "functional", "wellness", "sweet"]
    },
    {
        "name": "Fermented Flavor Snacks",
        "category": "salty",
        "growth": [9, 15, 24, 37, 49],
        "description": "Fermented flavor profiles like kimchi and pickled spice are attracting curiosity in shelf-stable savory snacks.",
        "risk": "High",
        "tags": ["fermented", "salty", "asian", "functional"]
    },
    {
        "name": "Herbal Dessert Snacks",
        "category": "sweet",
        "growth": [10, 16, 25, 36, 50],
        "description": "Herbal dessert-style snacks reflect growing interest in Asian-inspired sweet products with familiar wellness cues.",
        "risk": "Medium",
        "tags": ["herbal", "sweet", "dessert", "asian"]
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
{
    "name": "1mm Potato Crackers - BBQ",
    "category": "salty",
    "tags": ["potato", "crispy", "bbq", "snack"]
},
{
    "name": "1mm Potato Crackers - Garlic",
    "category": "salty",
    "tags": ["potato", "crispy", "garlic"]
},
{
    "name": "1mm Potato Crackers - Japanese Sauce",
    "category": "salty",
    "tags": ["potato", "crispy", "umami", "asian"]
},
{
    "name": "1mm Potato Crackers - Wasabi Seaweed",
    "category": "salty",
    "tags": ["potato", "wasabi", "seaweed", "spicy"]
},
{
    "name": "1mm Potato Crackers - Black Pepper",
    "category": "salty",
    "tags": ["potato", "pepper", "crispy"]
}
]
