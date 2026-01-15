# Delivery Cadet – LangGraph Conversational Data Agent

## 📌 Project Overview
This project is a **ChatGPT-style conversational data agent** built using **Python** and **LangGraph**. It allows users to ask natural language questions about datasets stored in a database, executes SQL queries dynamically, optionally performs Python-based analysis, and returns results conversationally.

The system is **dataset-agnostic**, supports **easy dataset swapping**, and runs fully **locally**.

---

## Requirements Mapping

| Requirement | Status |
|------------|--------|
| Built using Python 
| Built using LangGraph 
| Uses LangSmith for tracing 
| Runs locally | 
| ChatGPT-style interface 
| Dataset-agnostic 
| Easy dataset swapping 


---

##  Architecture

```
User (Browser / API Client)
        ↓
FastAPI (Chat UI Backend)
        ↓
LangGraph Agent
        ↓
LLM (Groq API)
        ↓
SQL Tools / Python Analysis
        ↓
MySQL Database
```

---

## 🛠️ Tech Stack

- **Python 3.10+**
- **LangGraph** – agent orchestration
- **LangChain** – LLM abstraction
- **LangSmith** – trace visualization
- **FastAPI** – backend API
- **MySQL** – database
- **Pandas** – data handling


---

## 📂 Project Structure

```
delivery_cadet/
│
├── app.py                  # FastAPI entry point
├── requirements.txt
├
│
├── agent/
│   └── graph.py            # LangGraph agent logic
│   └── prompts.py            # Dataset-agnostic system prompt
│   └── tools.py            # SQL execution tool
├── db/
│   ├── test_connection.py  # DB connectivity check
│   └── load_data.py        # CSV → MySQL loader
│
│
│
├── data/                   # CSV files (not committed)
└── README.md
```

---

## ⚙️ Setup Instructions (Step-by-Step)

### 1️⃣ Prerequisites

- Python **3.10 or above**
- MySQL Server running locally
- Git

---

### 2️⃣ Clone Repository

```bash
git clone https://github.com/bmkorde/delivery_cadet
cd delivery_cadet
```

---

### 3️⃣ Create Virtual Environment

#### for Windows (PowerShell)
```powershell
python -m venv venv
venv\Scripts\activate
```
> If you face **permission denied**, run PowerShell as **Administrator**.

#### for MAC (terminal)
```bash
python3 -m venv .venv
source .venv/bin/activate
```



---

### 4️⃣ Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirments.txt
```

---

### 5️⃣ Set Environment Variables

Temporary for current terminal session only

```
export GROQ_API_KEY="your_groq_api_key_here"
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_API_KEY="your_langsmith_key"
export LANGCHAIN_PROJECT="delivery-cadet"
```

#### OR (Windows CMD)
```cmd
setx GROQ_API_KEY "your_groq_api_key_here"
setx LANGCHAIN_API_KEY "your_langsmith_key"
```

Restart terminal after setting variables.

---

### 6️⃣ Setup MySQL Database

Login to MySQL:

```bash
mysql -u root -p
```
Enter password then
```sql
CREATE DATABASE delivery_db;
```
then 
```
EXIT
```


---

### 7️⃣ Test Database Connection

```bash
python db/test_connection.py
```

Expected output:
```
✅ Connected to MySQL successfully!
```

---

### 8️⃣ Load CSV Files into MySQL

Place CSV files inside:
```
data/
```

Run:
```bash
python db/loader.py
```

Each CSV will be loaded as a table (table name = file name).

---

### 9️⃣ Run the Application

```bash
python app.py
```

Open browser:
```
http://127.0.0.1:8000
```

---

## 💬 Chat Usage Example

```json
POST /ask
{
  "question": "Show total sales by customer"
}
```

The agent:
- Understands the question
- Inspects DB schema
- Generates SQL
- Executes query
- Returns conversational answer

---


---

## 🔁 Dataset Agnostic Design

- No dataset-specific prompts
- Schema is dynamically discovered
- Any CSV dataset can be loaded without code changes

---

## 🧪 LangSmith Tracing

To view traces:
1. Login to https://smith.langchain.com
2. Select project: `delivery-cadet`
3. Inspect LangGraph execution



## 🏁 Conclusion

This project demonstrates a production-ready, extensible conversational data agent built with LangGraph, fulfilling all assignment requirements while remaining flexible, local-first, and dataset-agnostic.

---

## 👤 Author

**Bhavesh Korde**

