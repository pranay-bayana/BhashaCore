# BhashaCore REST & Streaming API Reference

This document provides a complete, verified reference for all HTTP and streaming endpoints exposed by the BhashaCore Flask backend (`src/app.py`).

---

## 1. Global Conventions

### 1.1 Base URLs
- **Production:** `https://bhashacore.onrender.com`
- **Local Development:** `http://127.0.0.1:8001`

### 1.2 Authentication & Sessions
- **Session Cookie:** Authenticated state is managed via an HTTP-only, SameSite-Lax cookie (`session`).
- **Guest Identity:** Unauthenticated visitors are automatically assigned a persistent `guest_id` in their session cookie, tracking their 3-message free trial limit.
- **CSRF Token:** Non-GET mutating requests (`POST`) require either an `X-CSRFToken` request header or a `csrf_token` body parameter. Retrieve tokens via `GET /api/csrf-token`.

### 1.3 Streaming Media Type
Streaming endpoints (`POST /api/chat`) return `Content-Type: application/x-ndjson`. Each line emitted is a standalone, valid JSON object terminated by a newline (`\n`).

---

## 2. Authentication & User Management Endpoints

### 2.1 Get CSRF Token
Retrieves a valid CSRF token for subsequent mutating requests.

- **URL:** `/api/csrf-token`
- **Method:** `GET`
- **Auth Required:** No
- **Response `200 OK`:**
```json
{
  "csrf_token": "IjE0ZjViYjE2..."
}
```

---

### 2.2 Get Current User Profile
Returns the profile of the currently signed-in user, or null if unauthenticated.

- **URL:** `/api/auth/me`
- **Method:** `GET`
- **Auth Required:** No
- **Response `200 OK` (Authenticated):**
```json
{
  "user": {
    "id": 1,
    "name": "Pranay Bayana",
    "email": "user@example.com"
  }
}
```
- **Response `200 OK` (Guest):**
```json
{
  "user": null
}
```

---

### 2.3 User Registration
Creates a new authenticated user account.

- **URL:** `/api/auth/signup`
- **Method:** `POST`
- **Rate Limit:** 5 requests / hour
- **Headers:** `Content-Type: application/json`, `X-CSRFToken: <token>`
- **Request Body:**
```json
{
  "name": "Pranay Bayana",
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```
- **Validation Rules:**
  - `name`: String between 2 and 100 characters.
  - `email`: Valid email format (RFC-compliant regex).
  - `password`: Minimum 12 characters.
- **Response `201 Created`:**
```json
{
  "status": "success",
  "user": {
    "id": 1,
    "name": "Pranay Bayana",
    "email": "user@example.com"
  }
}
```
- **Error Responses:**
  - `400 Bad Request`: `{"error": "Use a password with at least 12 characters."}`
  - `409 Conflict`: `{"error": "An account already exists for that email address."}`

---

### 2.4 User Sign-In
Authenticates an existing user and establishes an authenticated session.

- **URL:** `/api/auth/signin`
- **Method:** `POST`
- **Rate Limit:** 10 requests / hour
- **Headers:** `Content-Type: application/json`, `X-CSRFToken: <token>`
- **Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```
- **Response `200 OK`:**
```json
{
  "status": "success",
  "user": {
    "id": 1,
    "name": "Pranay Bayana",
    "email": "user@example.com"
  }
}
```
- **Error Response `401 Unauthorized`:**
```json
{
  "error": "Invalid email or password."
}
```

---

### 2.5 User Sign-Out
Clears the active user session.

- **URL:** `/api/auth/logout`
- **Method:** `POST`
- **Headers:** `X-CSRFToken: <token>`
- **Response `200 OK`:**
```json
{
  "status": "success"
}
```

---

## 3. Conversational Chat & Streaming Endpoints

### 3.1 Streaming Chat Completion
The primary conversational endpoint. Evaluates input, executes BM25 retrieval over language-specific pools, injects mandatory language directives, and streams NDJSON tokens from Sarvam AI (`sarvam-105b-conversations`).

- **URL:** `/api/chat`
- **Method:** `POST`
- **Rate Limit:** 20 requests / hour per client IP
- **Headers:** `Content-Type: application/json`, `X-CSRFToken: <token>`
- **Request Body:**
```json
{
  "question": "What is photosynthesis?",
  "session_id": "c72a710a-7ca7-4240-842d-52b9bc251251",
  "input_lang": "auto",
  "input_style": "auto",
  "answer_lang": "te",
  "answer_script": "native",
  "mode": "rag",
  "eval_mode": false
}
```

#### Request Parameters
| Parameter | Type | Required | Default | Allowed Values / Description |
|---|---|---|---|---|
| `question` | string | **Yes** | — | User prompt (1–2000 characters). |
| `session_id` | string | No | UUID v4 | Conversation ID (`^[A-Za-z0-9_-]{1,128}$`). |
| `input_lang` | string | No | `"auto"` | `"auto"`, `"en"`, `"hi"`, `"ta"`, `"te"`, `"kn"`, `"ml"`. |
| `input_style` | string | No | `"auto"` | `"auto"`, `"native"`, `"romanized"`. |
| `answer_lang` | string | No | `null` | Target output language (`en`, `hi`, `ta`, `te`, `kn`, `ml`). Overrides auto-detection. |
| `answer_script` | string | No | `"native"` | `"native"`, `"romanized"`, `"latin"`. |
| `mode` | string | No | `"rag"` | `"rag"`, `"closed_book"`, `"gold_context"`, `"rag_translit"`. |
| `eval_mode` | boolean | No | `false` | When true, returns deterministic dataset gold answers during test evaluations. |

#### NDJSON Stream Event Types

##### 1. Meta Event (Initial Chunk)
Emitted immediately upon successful request validation and quota reservation.
```json
{
  "type": "meta",
  "session_id": "c72a710a-7ca7-4240-842d-52b9bc251251",
  "lang": "en",
  "input_lang": "en",
  "input_style": "native",
  "answer_lang": "te",
  "answer_script": "native",
  "mode": "rag",
  "model": "sarvam-105b-conversations",
  "guest_message_count": 1,
  "guest_limit": 3,
  "guest_quota_reached": false
}
```

##### 2. Token Event (Streaming Delta)
Emitted iteratively as text chunks arrive from the generator.
```json
{
  "type": "token",
  "content": "కిరణజన్య "
}
```

##### 3. Done Event (Final Chunk)
Emitted once upstream completes generation (`[DONE]`). Contains complete answer, citation provenance, and latency metrics.
```json
{
  "type": "done",
  "answer": "కిరణజన్య సంయోగక్రియ అనేది మొక్కలు సూర్యరశ్మి, నీరు మరియు కార్బన్ డయాక్సైడ్ ఉపయోగించి గ్లూకోజ్ మరియు ఆక్సిజన్ తయారుచేసే ప్రక్రియ.",
  "status": "answered",
  "latency_ms": 1420,
  "input_lang": "en",
  "input_style": "native",
  "input_detected_script": "Latin",
  "input_ambiguous": false,
  "bridged_query": null,
  "answer_lang": "te",
  "answer_script": "native",
  "translation_note": null,
  "is_model_only": false,
  "gold_rank": 1,
  "guest_message_count": 1,
  "guest_limit": 3,
  "guest_quota_reached": false,
  "citations": [
    {
      "pid": "en_para_0142",
      "title": "Photosynthesis and Plant Biology",
      "text": "Photosynthesis is the process used by plants and other organisms to convert light energy into chemical energy...",
      "score": 14.82,
      "support": 0.85,
      "used": true
    }
  ]
}
```

##### 4. Error Event (Failure Chunk)
Emitted if generation provider transport or rate limit fails during streaming.
```json
{
  "type": "error",
  "error": "provider_rate_limited",
  "message": "The AI service is busy. Please wait a moment and retry once.",
  "retryable": true
}
```

---

### 3.2 Abort Stream
Terminates an ongoing generation stream for the specified session.

- **URL:** `/api/stop`
- **Method:** `POST`
- **Headers:** `Content-Type: application/json`, `X-CSRFToken: <token>`
- **Request Body:**
```json
{
  "session_id": "c72a710a-7ca7-4240-842d-52b9bc251251"
}
```
- **Response `200 OK`:**
```json
{
  "status": "stopped"
}
```

---

### 3.3 New Conversation
Initializes a new conversational session on the server.

- **URL:** `/api/new-chat`
- **Method:** `POST`
- **Headers:** `X-CSRFToken: <token>`
- **Response `200 OK`:**
```json
{
  "session_id": "3b29c920-562a-4318-971c-7be1a80521ad",
  "title": "New chat",
  "lang": "en"
}
```

---

### 3.4 Load Conversation History
Retrieves all historical messages, citations, and language preferences for an existing session.

- **URL:** `/api/load-chat`
- **Method:** `POST`
- **Headers:** `Content-Type: application/json`, `X-CSRFToken: <token>`
- **Request Body:**
```json
{
  "session_id": "c72a710a-7ca7-4240-842d-52b9bc251251"
}
```
- **Response `200 OK`:**
```json
{
  "status": "loaded",
  "session": {
    "session_id": "c72a710a-7ca7-4240-842d-52b9bc251251",
    "title": "What is photosynthesis?",
    "lang": "en",
    "messages": [
      {
        "role": "user",
        "content": "What is photosynthesis?"
      },
      {
        "role": "assistant",
        "content": "Photosynthesis is the process...",
        "status": "answered",
        "citations": [...]
      }
    ]
  }
}
```

---

### 3.5 List Conversation Sessions
Lists all saved conversations owned by the authenticated user, or active guest sessions.

- **URL:** `/api/history`
- **Method:** `GET`
- **Response `200 OK`:**
```json
{
  "conversations": [
    {
      "id": "c72a710a-7ca7-4240-842d-52b9bc251251",
      "title": "What is photosynthesis?",
      "updated_at": "2026-11-13T14:48:00Z"
    }
  ]
}
```

---

### 3.6 Check Guest Quota Status
Returns the current guest trial consumption and remaining allowance.

- **URL:** `/api/guest-status`
- **Method:** `GET`
- **Response `200 OK`:**
```json
{
  "guest_id": "a982f1b04e6c...",
  "message_count": 1,
  "limit": 3,
  "remaining": 2,
  "quota_reached": false,
  "authenticated": false
}
```

---

## 4. Research & Evaluation Endpoints

### 4.1 Supported Languages Metadata
Returns the active configuration and scripts for supported languages.

- **URL:** `/api/languages`
- **Method:** `GET`
- **Response `200 OK`:**
```json
{
  "en": {"name": "English", "script": "Latin"},
  "hi": {"name": "Hindi", "script": "Devanagari"},
  "ta": {"name": "Tamil", "script": "Tamil"},
  "te": {"name": "Telugu", "script": "Telugu"},
  "kn": {"name": "Kannada", "script": "Kannada"},
  "ml": {"name": "Malayalam", "script": "Malayalam"}
}
```

---

### 4.2 Research Summary Dashboard
Returns macro aggregate metrics from empirical evaluations across all 6 languages.

- **URL:** `/api/dashboard`
- **Method:** `GET`
- **Response `200 OK`:**
```json
{
  "total_evaluations": 1458,
  "languages_evaluated": 6,
  "primary_model": "minimaxai/minimax-m3.1-flash",
  "average_correctness": {
    "en": {"gold_context": 4.94, "rag": 4.68, "closed_book": 2.74},
    "hi": {"gold_context": 4.86, "rag": 4.08, "closed_book": 2.48},
    "te": {"gold_context": 4.76, "rag": 4.29, "closed_book": 2.45},
    "ta": {"gold_context": 4.52, "rag": 2.76, "closed_book": 1.53},
    "kn": {"gold_context": 4.50, "rag": 3.06, "closed_book": 1.76},
    "ml": {"gold_context": 4.80, "rag": 3.90, "closed_book": 2.38}
  }
}
```

---

### 4.3 Language Comparison Matrix
Returns fine-grained metric breakdowns across dimensions (Comprehension, Retrieval, Romanization).

- **URL:** `/api/comparison`
- **Method:** `GET`
- **Response `200 OK`:**
```json
{
  "retrieval_metrics": [
    {"lang": "en", "recall_at_5": 0.95, "mrr_10": 0.914},
    {"lang": "hi", "recall_at_5": 0.80, "mrr_10": 0.643},
    {"lang": "te", "recall_at_5": 0.85, "mrr_10": 0.783},
    {"lang": "ta", "recall_at_5": 0.57, "mrr_10": 0.419},
    {"lang": "kn", "recall_at_5": 0.67, "mrr_10": 0.579},
    {"lang": "ml", "recall_at_5": 0.84, "mrr_10": 0.688}
  ]
}
```

---

### 4.4 Failure Taxonomy Distribution
Returns the categorized failure analysis breakdown across 530 evaluated failure cases.

- **URL:** `/api/failures`
- **Method:** `GET`
- **Response `200 OK`:**
```json
{
  "total_failures": 530,
  "categories": [
    {"flag": "Retrieval miss", "count": 306, "percentage": 57.7},
    {"flag": "Refusal", "count": 282, "percentage": 53.2},
    {"flag": "Wrong answer", "count": 224, "percentage": 42.3},
    {"flag": "Hallucinated", "count": 122, "percentage": 23.0},
    {"flag": "Incomplete", "count": 51, "percentage": 9.6},
    {"flag": "Off-topic", "count": 32, "percentage": 6.0}
  ]
}
```

---

## 5. UI Internationalization Endpoints

### 5.1 Set Interface Language
Updates the active interface localization in session and cookie.

- **URL:** `/api/set-interface-lang`
- **Method:** `POST`
- **Headers:** `Content-Type: application/json`, `X-CSRFToken: <token>`
- **Request Body:**
```json
{
  "lang": "te"
}
```
- **Response `200 OK`:**
```json
{
  "status": "success",
  "lang": "te"
}
```

---

### 5.2 Get Translations Catalog
Retrieves complete dictionary key-value pairs for the requested language code.

- **URL:** `/api/translations?lang=te`
- **Method:** `GET`
- **Response `200 OK`:**
```json
{
  "lang": "te",
  "translations": {
    "landing_title": "భాషా అవరోధాలు లేని మేధస్సు.",
    "cta_start_chatting": "చాట్ ప్రారంభించండి",
    ...
  }
}
```

---

## 6. System Health Check Endpoint

### 6.1 Service Health & Readiness
Performs database ping (`SELECT 1`) and verifies accessibility of all six BM25 knowledge pools. Used by Render deployment monitoring.

- **URL:** `/health`
- **Method:** `GET`
- **Auth Required:** No
- **Response `200 OK`:**
```json
{
  "status": "ok",
  "environment": "production",
  "database": "connected",
  "provider": "sarvam",
  "model": "sarvam-105b-conversations",
  "pools_verified": ["en", "hi", "ta", "te", "kn", "ml"],
  "timestamp": 1731672000
}
```
- **Error Response `503 Service Unavailable`:** Returned if database connection fails or any language pool is unreadable.
