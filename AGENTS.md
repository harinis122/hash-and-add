# 🤖 AGENTS.md — Codex Operating Guide

## 📌 Project Identity

This project is a **hackathon prototype** for:

> **POP Snack Strategy Engine (Flavor Gap Detector)**

This is NOT a generic data science project.

This is a **business decision tool** that simulates how a real company decides:

> “What products should we launch or distribute next?”

---

## 🏢 About POP (Prince of Peace / Prince of Price)

POP is a company that:

- imports and distributes **Asian food and wellness products**
- focuses on **herbal, natural, and functional consumables**
- sells through **retail + wholesale channels**
- prioritizes **accessible, mass-market products**

### Example product categories:
- ginger chews
- herbal teas
- wellness snacks
- shelf-stable packaged goods

---

## 🎯 POP’s Core Mission

POP aims to:

- bring **Asian-inspired wellness products** to global markets
- offer **affordable, accessible health-oriented foods**
- balance **traditional herbal ingredients** with **modern trends**

---

## ⚠️ CRITICAL BUSINESS CHALLENGE (VERY IMPORTANT)

POP’s biggest weakness is NOT lack of ideas.

It is:

> **SLOW EXECUTION due to regulatory and operational constraints**

### Why POP is slow:

- strict compliance with **FDA regulations**
- conservative product approval processes
- supply chain complexity (importing, manufacturing, labeling)
- longer product development timelines

---

## 🚨 Strategic Implication (CORE INSIGHT)

Because POP is slow to act:

> **They must detect trends EARLIER than competitors**

If they identify trends too late:
- competitors launch first
- market becomes saturated
- opportunity is lost

---

## 🎯 What This System Must Do Differently

This system is NOT just finding trends.

It must:

> **Prioritize EARLY-STAGE trends with future growth potential**

NOT just currently popular ones.

---

## 🧠 Updated Decision Logic (CRITICAL)

Every trend must be evaluated on:

1. **Trend Strength (Current Popularity)**
2. **Trend Momentum (How early vs saturated)**
3. **POP Presence**
4. **Feasibility**
5. **Time-to-Market Risk**

---

### New Concept: Timing Advantage Score

Each trend should include:

- EARLY → high strategic value  
- PEAK → medium value  
- SATURATED → low value  

---

### Updated Final Score

Final Score =  
Trend Strength  
+ Trend Momentum (early-stage bonus)  
+ Feasibility Score  
+ Gap Opportunity Score  
− Saturation Penalty  

---

## ⏱️ Time-to-Market Awareness

The system must consider:

> “Can POP realistically act on this BEFORE the trend peaks?”

If NOT:
- deprioritize the trend

---

## 🍬 Scope of This Project

ONLY focus on:

- Sweet snacks
- Salty snacks

These are:
- shelf-stable
- scalable
- aligned with POP’s capabilities

---

## 🔥 Core Idea: Flavor Gap Detection

The system must detect:

> **Where trends exist but POP has no strong presence**

Combined with:

> **Whether it is early enough to act**

---

## 🧩 Build vs Distribute Logic

### DISTRIBUTE if:
- trend is already accelerating quickly
- time-to-market is critical
- existing products can be sourced fast

### DEVELOP if:
- trend is early-stage
- POP has ingredient advantage (e.g., ginger, herbal)
- enough time exists before peak

---

## 🧪 Example Thinking

### Trend: Collagen Snacks

- growing but early-stage
- moderate feasibility
- POP presence: LOW

👉 GOOD opportunity (early + gap)

---

### Trend: Protein Bars

- highly saturated
- many competitors
- complex manufacturing

👉 BAD opportunity (too late)

---

### Trend: Spicy + Sweet Snacks

- rising quickly
- strong flavor alignment with POP
- feasible ingredients

👉 HIGH priority

---

## 🚧 Real-World Constraints (CRITICAL)

All recommendations MUST respect:

### 1. Shelf Stability
- must last months without refrigeration

### 2. Scalability
- must be mass-producible

### 3. Cost Sensitivity
- affordable ingredients only

### 4. Supply Chain Reality
- long shipping times
- import logistics

### 5. FDA Compliance
- approved food ingredients
- proper labeling
- no medical claims

---

## 🏗️ Architecture Rules

Code MUST be modular.

- `app.py` → UI only  
- `sample_data.py` → mock data  
- `scoring.py` → scoring logic  
- `gap_analysis.py` → POP vs trend comparison  
- `constraints.py` → feasibility rules  

---

## ⚙️ Development Philosophy

- prioritize working UI
- use mock data first
- keep logic simple
- make reasoning visible

---

## 🚫 What NOT to do

Do NOT:

- ignore time-to-market
- recommend saturated trends
- suggest unrealistic products
- overcomplicate models

---

## 🏁 Success Criteria

A successful system must:

- highlight early-stage opportunities
- reflect POP’s slow execution constraint
- prioritize trends with enough lead time
- clearly explain WHY a trend is actionable

---

## 🧭 Guiding Principle

Always think like:

> **A strategist at POP who must act early because the company is slow to execute**

NOT:

> Someone reacting to already-popular trends

---

## 🔥 Final Rule

If unsure:

- prefer earlier trends over bigger trends  
- prefer realistic over perfect  
- prefer explainable over complex 