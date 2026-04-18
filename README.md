# 🚀 POP Snack Strategy Engine (Flavor Gap Detector)

## 📌 Overview

This project is a **decision-making tool for snack innovation**, built for POP (Prince of Peace / Prince of Price).

It helps answer a single high-value question:

> **“What snack products should POP launch or distribute next?”**

Instead of just showing trends, this system:
- predicts **what is trending**
- evaluates **what POP can realistically execute**
- identifies **where POP is missing opportunities**

---

## 🎯 Problem Statement

Most tools answer:
> What is trending?

This project answers:
> What is trending AND feasible AND strategically valuable for POP?

We solve 3 key problems:

1. **Forecast snack trends (1–2 year horizon)**
2. **Filter by POP constraints**
   - shelf-stable
   - scalable
   - cost-efficient
3. **Recommend actions**
   - build a product
   - distribute an existing product

---

## 🍬 Scope: Why Sweet + Salty Snacks

We focus specifically on:
- **Sweet snacks**
- **Salty snacks**

This is intentional and strategic.

### Why this works:

- Aligns with POP’s current products:
  - ginger chews
  - teas
  - wellness consumables
- These categories are:
  - shelf-stable
  - easy to distribute
  - high-margin
- Strong overlap with major trends:
  - functional snacks (health + food)
  - low sugar snacks
  - protein snacks
  - Asian-inspired flavors
  - sweet + spicy / sweet + salty combinations

---

## 🔥 Core Concept: Flavor Gap Detector

This is what makes the project unique.

We are NOT building:
> a trend dashboard

We ARE building:
> a system that detects **gaps between trends and POP’s current product lineup**

---

### How it works:

For each trend, we evaluate:

1. **Trend strength**
2. **POP’s current presence**
3. **Execution feasibility**

Then we output:

> **What POP should do next**


### System Design: Mermaid Diagram
![alt text](image.png)


---

### Example Output

#### Trend: Sweet + Salty Protein Snacks

- Trend strength: HIGH  
- POP presence: LOW  

👉 Recommendation:
- Distribute: Asian protein snack brands  
- Develop: Ginger + chocolate + sea salt chew  

---

#### Trend: Spicy + Sweet Snacks

- Trend strength: HIGH  
- POP presence: MEDIUM  

👉 Recommendation:
- Develop: Ginger + chili fruit snack  

---

## 💡 Core Model

Each trend is scored using:

Final Score = Trend Score + Feasibility Score − Gap Penalty

Where:

- **Trend Score**
  - growth rate
  - popularity
  - momentum

- **Feasibility Score**
  - shelf stability
  - sourcing difficulty
  - manufacturing complexity

- **Gap Penalty / Bonus**
  - LOW POP presence → bonus (opportunity)
  - HIGH POP presence → penalty (already saturated)

---

## 🖥️ Product Experience (UI Flow)

### 1. Category Selection
- Sweet
- Salty

---

### 2. Ranked Trend Dashboard
- Trends ranked from best → worst opportunity
- Each card shows:
  - mini trend chart
  - risk level
  - short explanation

---

### 3. Trend Deep Dive

On click, show:

- Is this trend promising for POP?
- Build vs distribute?
- What constraints exist?
- Why now?
- What gap exists in POP’s lineup?

---

## 🏗️ Tech Stack

### Prototype (Current)
- Python
- Streamlit
- Mock data

### Future
- Pandas
- Time series forecasting
- NLP trend extraction
- Real sales + market datasets

