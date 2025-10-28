# 🧾 Transaction Webhook Service

A lightweight, production-ready **FastAPI** service designed to handle **financial transaction webhooks** efficiently and idempotently.  
The API ensures duplicate webhook events are safely ignored, all events are logged, and transactional integrity is maintained — even under retries or failures.

---

## 🚀 Features

- ✅ **Webhook Receiver** — Accepts transaction events from external systems.
- 🧩 **Idempotent Processing** — Prevents duplicate transactions from being stored.
- 🪵 **Webhook Logging** — Stores every webhook payload for debugging and audit purposes.
- 🩺 **Health Check Endpoint** — Quick service liveness verification for Render or uptime monitoring.
- 🐘 **PostgreSQL** — Robust relational database for durable transaction storage.
- ⚡ **FastAPI + SQLAlchemy (async)** — High-performance, modern Python stack.
- 🔁 **Alembic Migrations** — Version-controlled schema management.
- ☁️ **Deployed on Render** — Zero-config cloud hosting with auto-deploy from GitHub.

---

## 🏗️ Project Structure


---

## ⚙️ Tech Stack & Design Choices

| Component | Technology | Reason |
|------------|-------------|--------|
| **Framework** | [FastAPI](https://fastapi.tiangolo.com/) | Async performance, type hints, easy validation |
| **Database ORM** | SQLAlchemy + AsyncPG | Robust ORM with async PostgreSQL support |
| **Migrations** | Alembic | Schema version control |
| **Deployment** | Render | Simple CI/CD with GitHub integration |
| **Database** | PostgreSQL (Render Cloud) | Reliable and ACID-compliant relational database |
| **Logging** | WebhookLog Table | Transparent debugging of duplicate/retry events |
| **Idempotency** | Unique constraint on `transaction_id` | Ensures no duplicate transaction processing |

---

## 🧠 Data Model Overview

### 🏦 Transactions Table
Stores processed transaction records.

| Column | Type | Description |
|---------|------|-------------|
| id | UUID | Primary key |
| transaction_id | String | Unique external transaction ID |
| source_account | String | Sender account |
| destination_account | String | Receiver account |
| amount | Float | Transaction amount |
| currency | String | Currency code (e.g. INR) |
| status | Enum | PROCESSING / PROCESSED / FAILED |
| created_at | DateTime | Time of creation |
| processed_at | DateTime | When processing completed |
| is_deleted | Boolean | Soft delete flag |

### 🧾 Webhook Logs Table
Stores every incoming webhook payload (even duplicates).

| Column | Type | Description |
|---------|------|-------------|
| id | UUID | Primary key |
| transaction_id | String | Incoming transaction ID |
| payload | JSON/Text | Raw webhook body |
| received_at | DateTime | Time received |
| is_deleted | Boolean | Soft delete flag |

---

## 🌐 API Endpoints

### 🔹 Health Check
```http
GET /
