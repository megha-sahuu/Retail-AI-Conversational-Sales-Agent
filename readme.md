# Retail AI Conversational Sales Agent

A multi-channel AI shopping assistant that works seamlessly across **Web Chat**, **In-Store Kiosk**, and **WhatsApp** — while maintaining **shared conversational context** across all channels.

This project simulates a next-generation retail experience where customers can start shopping on one channel and continue on another while the AI agent handles:

- 🛍️ Intelligent product recommendations (LLM + rule-based)  
- 🏬 Real-time inventory checks  
- 📦 Store reservations  
- 💳 Multi-method payments  
- 🚚 Home delivery or store pickup  
- 🔄 Stateful, cross-platform conversations  

---

## 🌟 Demo Flow (Competition-Friendly)

You can demo the system in ~3–4 minutes using this storyline:

---

### **1️⃣ Start on Web Chat**

**User (Web Chat):**

> Suggest outfits for a beach vacation under 3000

**What happens:**

- The agent recommends products based on **intent**, **budget**, and **context**.
- Selected products are stored in **session memory** for later steps.

---

### **2️⃣ Continue on In-Store Kiosk**

**User (Kiosk):**

> Check availability for the first one

**What happens:**

- The kiosk continues the **same conversation context**.
- The agent checks **store inventory** for the selected product.
- Responds with **availability per store / location**.

---

### **3️⃣ Reserve the Item**

**User (Kiosk):**

> Reserve it in store

**What happens:**

- The system creates a **store reservation**.
- Reservation details (store, product, time) are stored in **shared state**.

---

### **4️⃣ Switch to WhatsApp**

**User (WhatsApp):**

> Proceed to payment

**What happens:**

- The agent **remembers** the previously selected & reserved product.
- Applies **loyalty discounts** (if any).
- Initiates **checkout flow** on WhatsApp.

---

### **5️⃣ Complete Payment and Delivery**

**User (WhatsApp):**

> Pay with UPI  
> Home delivery please

**What happens:**

- Mock **UPI payment** is processed.  
- User chooses **home delivery** vs **store pickup**.  
- Fulfillment is confirmed with a final **order summary**.

---

## 🏗️ Tech Stack

### **Frontend**

- ⚛️ **React + TypeScript**  
- 🎨 ChatGPT / Gemini-inspired **conversational UI**  
- 📡 **REST API** integration with backend  
- 💬 Multi-channel chat interface (Web / Kiosk views, WhatsApp-style mock)

### **Backend**

- 🚀 **FastAPI (Python)**  
- 🤖 **LLM orchestration layer** (SalesAgent + micro-agents)  
- 🧠 **Session state** (in-memory / Redis-ready design)  
- 🛍️ **Micro-agent architecture:**
  - `RecommendationAgent`
  - `InventoryAgent`
  - `LoyaltyAgent`
  - `PaymentAgent`
  - `FulfillmentAgent`

### **AI Layer**

- Natural-language **product retrieval**  
- **Budget extraction** & preference parsing  
- Hybrid **rule-based + LLM** scoring model  
- Fallback LLM for open-ended queries & small talk
  
## ✅ Prerequisites

Ensure the following are installed on your system:

- **Node.js (LTS version recommended)**
- **Python 3.10+**
- *(Optional)* **Redis** — only required if you switch from in-memory to external session storage.

---

# 1️⃣ Backend (FastAPI)

### ➤ Setup & Installation

```bash
cd backend
python -m venv .venv

<img width="1919" height="901" alt="image" src="https://github.com/user-attachments/assets/96abc148-d02c-4048-bf4f-fef23896947e" />
<img width="1919" height="971" alt="image" src="https://github.com/user-attachments/assets/e0dcb750-dfa3-4512-8914-4a0c2928be05" />
<img width="1919" height="944" alt="image" src="https://github.com/user-attachments/assets/ea0967c8-aa36-439d-96bf-b8769725087c" />
<img width="1919" height="929" alt="image" src="https://github.com/user-attachments/assets/49923bf2-394e-4209-95e8-73dc657d9b98" />


---

## 🧩 Architecture Overview

```text
            ┌──────────────────────────┐
            │        React App         │
            │  Web • Kiosk • WhatsApp  │
            └────────────┬─────────────┘
                         │ REST API
                         ▼
           ┌───────────────────────────┐
           │           FastAPI         │
           │        /api/v1/chat       │
           └───────┬──────────┬────────┘
                   │          │
                   ▼          ▼
        ┌────────────────┐   ┌────────────────────┐
        │   SalesAgent   │ → │ RecommendationAgent │
        └──────┬─────────┘   └────────────────────┘
               │
               ▼
  ┌────────────┬───────────────┬──────────────────┐
  │ Inventory  │ Loyalty Engine │ Payment Engine    │
  │ Agent      │   (discount)   │  (mock payments)  │
  └────────────┴───────────────┴──────────────────┘
               │
               ▼
       ┌──────────────────────┐
       │   FulfillmentAgent   │
       │ Reserve / Delivery   │
       └──────────────────────┘

## 📂 Project Structure (High-Level)
.
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entrypoint
│   │   ├── api/                 # Routes (e.g., /api/v1/chat)
│   │   ├── agents/              # SalesAgent + sub-agents
│   │   ├── core/                # LLM client, config, utils
│   │   └── domain/              # Models: Product, CustomerProfile, etc.
│   └── tests/
│
├── frontend/
│   ├── src/
│   │   ├── components/          # Chat UI, layout, channel selector
│   │   ├── pages/               # Web, Kiosk views
│   │   ├── api/                 # Client for /api/v1/chat
│   │   └── state/               # Conversation + channel state
│   └── public/
│
└── README.md
# 🚀 Running the Project

This guide explains how to set up and run both the **Backend (FastAPI)** and **Frontend (React + TypeScript)** for the Retail AI Conversational Sales Agent.




