# 🤖 AGENTS.md — Instructions for Codex

## 📌 Project Context

This project is a **hackathon prototype** for a snack strategy tool called:

> **POP Snack Strategy Engine (Flavor Gap Detector)**

The goal is NOT to build a generic trend dashboard.

The goal is to build:

> **A system that recommends what snack products POP should launch or distribute next**

---

## 🎯 Core Problem

The system must:

1. Identify **emerging snack trends**
2. Evaluate **whether POP can execute them**
3. Detect **gaps in POP’s current product lineup**
4. Output **clear business recommendations**

---

## 🍬 Scope (IMPORTANT)

Only focus on:

- Sweet snacks
- Salty snacks

Do NOT expand into unrelated food categories.

All logic should assume:
- shelf-stable products
- packaged snack goods
- easy distribution

---

## 💡 Core Concept: Flavor Gap Detection

This is the defining feature of the project.

The system must compare:

- **What is trending**
vs
- **What POP already sells**

And identify:

> **Where POP is missing opportunities**

---

## 🧠 Required Output Behavior

For each trend, the system should ultimately provide:

- Trend description
- Trend strength (score or label)
- POP presence (LOW / MEDIUM / HIGH)
- Risk level
- Recommendation:
  - Build a new product
  - Distribute an existing one
- Explanation (why this is a good opportunity)

---

## 🏗️ Architecture Rules

Code MUST be modular.

### Files and responsibilities:

- `app.py`
  - Streamlit UI only
  - No heavy logic

- `sample_data.py`
  - mock trends
  - mock POP product catalog

- `scoring.py`
  - trend scoring
  - feasibility scoring

- `gap_analysis.py`
  - compares trends vs POP products
  - calculates "POP presence"

- `constraints.py`
  - rules like shelf stability, cost, etc.

---

## ⚙️ Development Philosophy

### 1. Start simple
- Always build the simplest working version first

### 2. Use mock data
- Do NOT require real datasets initially

### 3. Prioritize UI over intelligence
- A working demo is more important than perfect logic

### 4. Keep everything replaceable
- Logic should be easy to swap with real models later

---

## 🚫 What NOT to do

Do NOT:

- implement complex ML models early
- add unnecessary frameworks
- tightly couple UI and logic
- over-engineer data pipelines
- fetch external APIs unless explicitly required

---

## 🧪 Expected Build Order

When adding features, follow this order:

1. UI skeleton (Streamlit)
2. Mock data integration
3. Trend ranking display
4. Clickable detail view
5. Scoring functions
6. Gap detection logic
7. Improved explanations

---

## 🧩 Data Design Expectations

Mock data should include:

### Trends:
- name
- category (sweet/salty)
- growth values (list or time series)
- description

### POP Products:
- product name
- flavor profile
- category
- tags (e.g., ginger, herbal, sweet, spicy)

---

## 🧠 Decision Logic (IMPORTANT)

All recommendations must come from:

Trend Score  
+ Feasibility Score  
+ Gap Opportunity  

NOT from random or hardcoded rankings.

---

## 🏁 Success Criteria

A successful implementation must:

- run locally with `streamlit run app.py`
- display ranked snack opportunities
- allow users to explore trends
- clearly show reasoning behind recommendations
- demonstrate gap detection

---

## 🧭 Guiding Principle

Always optimize for:

> **Clarity, simplicity, and demo-ability**

This is a hackathon project, not a production system.

---

## 🔥 Final Reminder

If unsure:

- make it simpler
- make it runnable
- make it explainable

DO NOT make it more complex.
