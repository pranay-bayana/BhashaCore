# BhashaCore System Architecture

This document provides a comprehensive technical overview of the system architecture, component boundaries, data flows, and security model of **BhashaCore**, an enterprise-grade multilingual conversational AI platform and research workbench supporting English and five major Indian languages (Hindi, Tamil, Telugu, Kannada, and Malayalam).

---

## 1. Architectural Overview & Design Philosophy

BhashaCore is designed around four foundational principles:

1. **Language-Agnostic Core with Script-Aware Periphery:** The core generation and reasoning capabilities leverage modern large language models, while input processing, tokenization, transliteration, and passage retrieval explicitly respect the orthographic and morphological rules of distinct Indic scripts.
2. **Honest, Verifiable Provenance (No Silent Fallbacks):** Answers are grounded in language-specific document corpora with transparent citation support scoring. Live-provider generation failures surface as actionable HTTP errors rather than fabricating pseudo-answers.
3. **Decoupled Retrieval and Response Languages:** The corpus query language (`retrieval_lang`) is decoupled from the target output language (`answer_lang`). This enables cross-lingual knowledge synthesis (e.g., retrieving facts from an English corpus while generating the response strictly in Telugu).
4. **Resilient Dual-Tier Session Persistence:** Authenticated users enjoy persistent, encrypted database conversations, while guest visitors are governed by a server-side, concurrency-safe 3-message trial backed by atomic PostgreSQL row locks.

```mermaid
graph TB
    subgraph ClientLayer ["Client Layer (Browser)"]
        UI["React 18 + Vite SPA<br/>(Tailwind CSS, Framer Motion)"]
        I18N["LanguageContext<br/>(6-Language UI Catalogs)"]
        Composer["ChatComposer & Workspace<br/>(Pill Selectors, Auto-Resize)"]
    end

    subgraph GatewayLayer ["Reverse Proxy & Web Gateway"]
        RenderLB["Render Cloud Load Balancer<br/>(TLS Termination, Port 443)"]
        GunicornWSGI["Gunicorn WSGI Server<br/>(Uvicorn/Worker Threads)"]
    end

    subgraph AppLayer ["Flask Backend Application (src/app.py)"]
        AuthModule["Auth & Session Controller<br/>(src/auth.py)"]
        LangRouter["Language Resolution & Priority Engine<br/>(src/lang_instruction.py)"]
        ScriptBridge["Transliteration & Script Toolkit<br/>(src/langkit.py, src/translit.py)"]
        RAGOrchestrator["RAG Decision Engine<br/>(answer_question())"]
        StreamEngine["NDJSON Streaming Pipeline<br/>(SSE Response Emitter)"]
    end

    subgraph RetrievalLayer ["Information Retrieval Engine"]
        Tokenizer["Script-Aware Tokenizer<br/>(NFC + 5-Char Prefixes)"]
        BM25Core["BM25Okapi Indices<br/>(Language-Specific Pools)"]
        CorpusStore[("Processed Pools<br/>data/processed/pool_*.jsonl")]
    end

    subgraph ModelLayer ["AI Generation Providers"]
        SarvamProvider["Sarvam AI Provider<br/>(sarvam-105b-conversations)"]
        NvidiaProvider["NVIDIA NIM Fallback / Benchmarking<br/>(minimax-m3.1-flash, glm-5.3)"]
    end

    subgraph DataLayer ["Data & Cache Infrastructure"]
        PostgresDB[("Supabase PostgreSQL<br/>Users, Convs, Messages, Guests")]
        RedisCache[("Upstash Redis<br/>Rate Limiting & Token Buckets")]
    end

    UI -->|HTTPS / NDJSON| RenderLB
    RenderLB -->|Reverse Proxy| GunicornWSGI
    GunicornWSGI --> AppLayer

    AppLayer --> AuthModule
    AppLayer --> LangRouter
    LangRouter --> ScriptBridge
    AppLayer --> RAGOrchestrator

    RAGOrchestrator --> Tokenizer
    Tokenizer --> BM25Core
    BM25Core --> CorpusStore

    RAGOrchestrator --> SarvamProvider
    RAGOrchestrator -.-> NvidiaProvider
    SarvamProvider -->|Async Chunks| StreamEngine
    StreamEngine -->|NDJSON Stream| UI

    AuthModule --> PostgresDB
    AppLayer --> RedisCache
```

---

## 2. End-to-End Request Lifecycle

When a user submits a question through the chat interface, the request traverses the following lifecycle:

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Frontend as React Client (ChatWorkspace)
    participant Flask as Flask Application (/api/chat)
    participant Limiter as Redis Rate Limiter
    participant DB as Supabase PostgreSQL
    participant LangEngine as Language Resolution (src/lang_instruction)
    participant BM25 as BM25 Retrieval Engine
    participant Sarvam as Sarvam AI API
    
    User->>Frontend: Enters query & clicks Send
    Frontend->>Flask: POST /api/chat (JSON payload: question, input_lang, answer_lang, session_id)
    
    Flask->>Limiter: Check rate limit (20 generations/hour per IP)
    alt Rate Limit Exceeded
        Limiter-->>Flask: 429 Too Many Requests
        Flask-->>Frontend: HTTP 429 Error (Retry-After)
    end
    
    alt Guest Session
        Flask->>DB: SELECT FOR UPDATE on guest_sessions WHERE id = guest_id
        DB-->>Flask: Locked GuestSession Row
        alt message_count >= 3
            Flask-->>Frontend: HTTP 403 Trial Limit Reached (Sign-in Required)
        end
        Flask->>Flask: Reserve slot & generate SHA-256 fingerprint
    else Authenticated User
        Flask->>DB: Validate user_id & fetch/create Conversation
    end
    
    Flask->>LangEngine: extract_language_instruction(question)
    LangEngine-->>Flask: Directives, Persistence Flags, Reset Flags
    Flask->>LangEngine: Resolve 4-Tier Language Priority Order
    LangEngine-->>Flask: Resolved answer_lang & retrieval_lang
    
    Flask->>BM25: Query passage index (pool_{retrieval_lang})
    alt Romanized Indic Query
        BM25->>BM25: Dual retrieval (ITRANS + Casual Digraph Normalization)
    end
    BM25-->>Flask: Top-k passages (pids, scores, text)
    
    Flask->>LangEngine: build_language_system_directive(answer_lang, answer_script)
    LangEngine-->>Flask: Mandatory System Prompt String
    
    Flask->>Sarvam: POST /chat/completions (Stream = True, Context + Directive + Question)
    
    Flask-->>Frontend: HTTP 200 OK (Transfer-Encoding: chunked, mimetype: application/x-ndjson)
    Flask-->>Frontend: Event: {"type": "meta", "session_id": "...", "lang": "...", "answer_lang": "..."}
    
    loop Stream Chunks
        Sarvam-->>Flask: data: {"choices": [{"delta": {"content": "..."}}]}
        Flask-->>Frontend: Event: {"type": "token", "content": "..."}
    end
    
    Sarvam-->>Flask: data: [DONE]
    
    Flask->>Flask: Compute passage support scores & mark used citations
    
    alt Guest Session
        Flask->>DB: UPDATE guest_sessions SET message_count = count + 1, data_json = ...
        DB-->>Flask: Commit transaction (Row lock released)
    else Authenticated User
        Flask->>DB: INSERT INTO messages (role="assistant", content=..., metadata_json=...)
        DB-->>Flask: Commit transaction
    end
    
    Flask-->>Frontend: Event: {"type": "done", "status": "answered", "citations": [...], ...}
    Frontend->>User: Renders completed response with interactive citation pills
```

---

## 3. Component Breakdown

### 3.1 Frontend Single-Page Application (`frontend/`)

Built with React 18, TypeScript 5.6, Vite 5.4, and Tailwind CSS, the client provides a dark-mode glassmorphic user interface:

- **`ChatWorkspace.tsx`**: Orchestrates message streams, autoscroll behavior, citation panel expansion, and welcome prompt suggestions.
- **`ChatComposer.tsx`**: Manages textarea auto-resize, submission throttling, keyboard bindings (Enter to submit, Shift+Enter for newlines), and language selection buttons (`Auto-detect`, `EN`, `HI`, `TE`, `TA`, `KN`, `ML`).
- **`ChatSidebar.tsx`**: Displays active conversation lists, "New Chat" creation with race-condition prevention, and live guest trial countdowns.
- **`LanguageContext.tsx`**: Comprehensive UI internationalization engine providing instantaneous localization of all labels, error messages, and descriptions across English and the 5 Indic languages from JSON catalogs (`frontend/src/localization/catalogs/*.json`).
- **`ResearchDashboardView.tsx`, `LanguageComparisonView.tsx`, `FailureAnalysisView.tsx`**: Interactive scientific exploration tools visualizing benchmark results, cross-language degradation waterfalls, and failure categorizations directly from API endpoints.

### 3.2 Flask Backend API (`src/app.py`)

A production-hardened Python 3.12 Flask application serving as both the REST/NDJSON API backend and the static file server for the built frontend:

- **Routing & Validation:** Enforces strict payload typing, maximum character lengths (2000 chars), valid UUID session tokens, and verified language codes (`LANGS`).
- **Proxy Accommodation:** Configured via `werkzeug.middleware.proxy_fix.ProxyFix(app, x_for=1, x_proto=1, x_host=1)` to correctly determine client IP addresses and protocol schemes behind Render's upstream load balancers.
- **NDJSON Streaming:** Streams incremental response tokens and citation metadata using `application/x-ndjson` chunks, terminating gracefully upon client abort (`/api/stop`) or upstream completion.
- **Health Verification (`/health`):** Verifies database connectivity (`SELECT 1`) and tests the availability of all 6 language retrieval pools before returning HTTP 200.

---

## 4. Multilingual Processing & Retrieval Architecture

### 4.1 Script-Aware BM25 Tokenization

Standard tokenizers fail on Dravidian languages (Tamil, Telugu, Kannada, Malayalam) due to **agglutinative morphology**, where grammatical suffixes, case markers, and postpositions attach directly to root nouns and verbs.

BhashaCore implements a specialized script-aware tokenizer in `src/retrieval.py`:

```python
def tokenize(text: str) -> list:
    toks = _normalize(text).split()
    prefixes = [t[:5] for t in toks if len(t) >= 6]
    return toks + prefixes
```

1. **NFC Normalization:** Converts decomposed Unicode character sequences into canonical precomposed characters, resolving font rendering discrepancies.
2. **Punctuation & Zero-Width Stripping:** Removes Zero-Width Joiners (ZWJ: `\u200D`) and Zero-Width Non-Joiners (ZWNJ: `\u200C`) that create false token mismatches.
3. **5-Character Prefix Augmentation:** For all tokens with $\ge 6$ characters, extracts the 5-character stem. This bridges schwa-variant spellings in Hindi and isolates base nominal roots from inflected agglutinative suffixes in Dravidian languages.

### 4.2 Mathematical Formulation of BM25Okapi

The retrieval engine scores passages using the BM25Okapi probabilistic ranking function:

$$\text{IDF}(q_i) = \ln \left( \frac{N - n(q_i) + 0.5}{n(q_i) + 0.5} + 1 \right)$$

$$\text{Score}(D, Q) = \sum_{i=1}^{|Q|} \text{IDF}(q_i) \cdot \frac{f(q_i, D) \cdot (k_1 + 1)}{f(q_i, D) + k_1 \cdot \left(1 - b + b \cdot \frac{|D|}{\text{avgdl}}\right)}$$

Where:
- $N$ is the total number of passages in the language pool.
- $n(q_i)$ is the number of passages containing query token $q_i$.
- $f(q_i, D)$ is the term frequency of $q_i$ in passage $D$.
- $|D|$ is the length of passage $D$ in tokens, and $\text{avgdl}$ is the average passage length across the pool.
- $k_1 = 1.5$ regulates term frequency saturation.
- $b = 0.75$ controls document length normalization.

### 4.3 Romanized Indic Dual-Retrieval Bridge

When users type Indic languages in Latin script ("Hinglish", "Tanglish", "Telugish"), lexical overlap with native-script documents drops to zero. BhashaCore resolves this via a dual-variant bridging algorithm (`src/langkit.py`):

```mermaid
flowchart LR
    A["Romanized User Query<br/>(e.g., 'photosynthesis ante enti')"] --> B["Accent & Digraph Normalizer<br/>(th -> t, aa -> A, ee -> I)"]
    B --> C["Strict ITRANS Transliteration"]
    B --> D["Casual Digraph Transliteration"]
    C --> E["Native Script Query 1<br/>(ఫోటోసింథసిస్ అంటే ఏంటి)"]
    D --> F["Native Script Query 2<br/>(ఫోటోసింథెసిస్ అంటే ఏమిటి)"]
    E --> G["BM25 Pool Search"]
    F --> G
    G --> H["Max-Score Candidate Fusion<br/>(Top-5 Passages)"]
```

---

## 5. Language Resolution & Priority Hierarchy

BhashaCore enforces an exact, four-tier priority hierarchy to resolve the target response language:

```mermaid
flowchart TD
    Q["Input Query + Request Metadata"] --> P1{"1. Explicit Natural Directive<br/>in User Message?<br/>(e.g., 'in Telugu', 'Answer in English')"}
    P1 -- Yes --> R1["Target Lang = Explicit Directive<br/>(If persistent 'from now on', save to DB)"]
    P1 -- No --> P2{"2. Stored Conversation Preference<br/>in Active Session?"}
    P2 -- Yes --> R2["Target Lang = Stored Preference"]
    P2 -- No --> P3{"3. Manual Selection in UI Pills?<br/>(input_lang != 'auto' or answer_lang)"}
    P3 -- Yes --> R3["Target Lang = Manually Selected Language"]
    P3 -- No --> P4["4. Auto-Detected Language<br/>(Native Script or Romanized Vocabulary)"]
    
    R1 --> SysPrompt["Inject Mandatory Language Directive into Prompt"]
    R2 --> SysPrompt
    R3 --> SysPrompt
    P4 --> SysPrompt
```

### Retrieval vs. Answer Language Decoupling

A critical architectural distinction is maintained between:
- **`retrieval_lang`**: The language of the query text itself, used to search the corresponding knowledge pool for factual evidence.
- **`answer_lang`**: The language in which the assistant generates its completion.

If an English query requests an answer in Telugu:
1. `retrieval_lang` is set to `"en"`. BM25 retrieves high-scoring English passages from `pool_en.jsonl`.
2. `answer_lang` is set to `"te"`. The system prompt instructs Sarvam 105B to synthesize the English facts and output the entire response in Telugu script.
3. Citation support scoring recognizes cross-lingual synthesis (`answer_lang != retrieval_lang`) and properly attributes the English source passages.

---

## 6. Database Schema & Data Models

BhashaCore uses SQLAlchemy 2.0 with Alembic migrations against Supabase PostgreSQL:

```mermaid
erDiagram
    users ||--o{ conversations : "owns (CASCADE)"
    users ||--o{ password_reset_tokens : "owns (CASCADE)"
    conversations ||--o{ messages : "contains (CASCADE)"
    
    users {
        int id PK
        string name "VARCHAR(100)"
        string email "VARCHAR(254) UNIQUE, INDEX"
        string password_hash "VARCHAR(512)"
        datetime created_at "TIMESTAMPTZ"
    }

    conversations {
        string id PK "VARCHAR(128)"
        int user_id FK "REFERENCES users(id) ON DELETE CASCADE"
        string title "VARCHAR(240)"
        datetime created_at "TIMESTAMPTZ"
        datetime updated_at "TIMESTAMPTZ, INDEX(user_id, updated_at)"
    }

    messages {
        int id PK
        string conversation_id FK "REFERENCES conversations(id) ON DELETE CASCADE"
        string role "VARCHAR(20) [user|assistant|system]"
        text content "TEXT"
        text metadata_json "TEXT (citations, status, preferred_lang)"
        datetime created_at "TIMESTAMPTZ"
    }

    password_reset_tokens {
        int id PK
        int user_id FK "REFERENCES users(id) ON DELETE CASCADE"
        string token_hash "VARCHAR(64) UNIQUE"
        datetime expires_at "TIMESTAMPTZ"
        datetime used_at "TIMESTAMPTZ (NULL if unused)"
    }

    guest_sessions {
        string id PK "VARCHAR(64) (guest_id token)"
        int message_count "INTEGER (Default 0)"
        datetime created_at "TIMESTAMPTZ"
        datetime updated_at "TIMESTAMPTZ"
        datetime expires_at "TIMESTAMPTZ (7-day TTL)"
        text data_json "TEXT (conversations, preferred_lang)"
    }
```

---

## 7. Concurrency, Locking & Quota Management

To enforce the 3-message guest trial across multiple Gunicorn workers and browser tabs without race conditions:

1. **Pessimistic Row Locking (`SELECT FOR UPDATE`):**
   ```python
   guest_sess = db.session.execute(
       db.select(GuestSession).where(GuestSession.id == guest_id).with_for_update()
   ).scalar_one_or_none()
   ```
2. **Two-Phase Reservation & Commit:**
   - **Phase 1 (Reservation):** When `/api/chat` receives a request, it checks `message_count < 3`. It registers a pending request key (SHA-256 fingerprint) and commits the reservation without incrementing the quota.
   - **Phase 2 (Commit or Release):** Once Sarvam AI successfully completes streaming (`[DONE]`), `commit_guest_response()` increments `message_count` and updates conversation history. If generation fails or is aborted by the user, `release_guest_reservation()` cancels the reservation, ensuring failed requests never consume a user's quota.

---

## 8. Security & Compliance Architecture

- **CSRF Protection:** Flask-WTF enforces CSRF token validation on state-changing POST endpoints, with client tokens retrieved via `/api/csrf-token`.
- **Session Cookie Hardening:** `SESSION_COOKIE_HTTPONLY=True`, `SESSION_COOKIE_SAMESITE='Lax'`, and `SESSION_COOKIE_SECURE=True` (in production).
- **Distributed Rate Limiting:** Flask-Limiter backed by Upstash Redis prevents denial-of-service and brute-force attacks:
  - Sign-up: 5 requests / hour
  - Sign-in: 10 requests / hour
  - Chat completions: 20 requests / hour per IP
- **Parameter Tampering Prevention:** Strict session ID validation rejects any identifiers containing invalid characters or path traversal sequences (`re.compile(r"^[A-Za-z0-9_-]{1,128}$")`).
- **Credential Storage:** User passwords are encrypted using Werkzeug's `generate_password_hash` with secure salt derivation (scrypt).
