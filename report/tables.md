# Auto-generated tables

### Judge correctness (0-5)

| Language | Closed-book | Gold context | RAG | RAG + Romanized query |
|---|---|---|---|---|
| EN (English) | 2.74 | 4.94 | 4.68 | - |
| HI (Hindi) | 2.48 | 4.86 | 4.08 | 0.00 |
| TA (Tamil) | 1.53 | 4.52 | 2.76 | 0.21 |
| TE (Telugu) | 2.45 | 4.76 | 4.29 | 0.40 |
| KN (Kannada) | 1.76 | 4.50 | 3.06 | 0.04 |
| ML (Malayalam) | 2.38 | 4.80 | 3.90 | 0.41 |

### Exact match

| Language | Closed-book | Gold context | RAG | RAG + Romanized query |
|---|---|---|---|---|
| EN (English) | 0.00 | 0.08 | 0.06 | - |
| HI (Hindi) | 0.00 | 0.00 | 0.00 | 0.00 |
| TA (Tamil) | 0.00 | 0.04 | 0.02 | 0.00 |
| TE (Telugu) | 0.00 | 0.00 | 0.00 | 0.00 |
| KN (Kannada) | 0.00 | 0.00 | 0.00 | 0.00 |
| ML (Malayalam) | 0.00 | 0.02 | 0.00 | 0.00 |

### Token F1

| Language | Closed-book | Gold context | RAG | RAG + Romanized query |
|---|---|---|---|---|
| EN (English) | 0.11 | 0.39 | 0.35 | - |
| HI (Hindi) | 0.08 | 0.25 | 0.18 | 0.01 |
| TA (Tamil) | 0.04 | 0.23 | 0.11 | 0.00 |
| TE (Telugu) | 0.06 | 0.21 | 0.18 | 0.02 |
| KN (Kannada) | 0.03 | 0.29 | 0.16 | 0.00 |
| ML (Malayalam) | 0.05 | 0.25 | 0.15 | 0.02 |

### Faithfulness to context (1-5)

| Language | Gold context | RAG | RAG + Romanized query |
|---|---|---|---|
| EN (English) | 4.94 | 4.96 | - |
| HI (Hindi) | 4.88 | 4.94 | 4.75 |
| TA (Tamil) | 4.85 | 4.56 | 5.00 |
| TE (Telugu) | 4.74 | 4.98 | 4.72 |
| KN (Kannada) | 4.81 | 4.69 | 3.50 |
| ML (Malayalam) | 4.80 | 4.59 | 5.00 |

### Responses in target language/script (purity >= 0.8)

| Language | Closed-book | Gold context | RAG | RAG + Romanized query |
|---|---|---|---|---|
| EN (English) | 1.00 | 0.98 | 1.00 | - |
| HI (Hindi) | 0.98 | 1.00 | 1.00 | 1.00 |
| TA (Tamil) | 0.91 | 0.98 | 1.00 | 1.00 |
| TE (Telugu) | 0.93 | 1.00 | 1.00 | 0.98 |
| KN (Kannada) | 1.00 | 1.00 | 1.00 | 1.00 |
| ML (Malayalam) | 0.98 | 0.98 | 0.98 | 0.98 |

### Generator family comparison (judge correctness, 0-5)

| Language | Mode | minimaxai/minimax-m3.1-flash | z-ai/glm-5.3-flash |
|---|---|---|---|
| EN (English) | Gold context | 4.94 | 5.00 |
| EN (English) | RAG | 4.68 | 4.80 |
| HI (Hindi) | Gold context | 4.86 | 4.64 |
| HI (Hindi) | RAG | 4.08 | 3.68 |
| TA (Tamil) | Gold context | 4.52 | 4.44 |
| TA (Tamil) | RAG | 2.76 | 2.68 |
| TE (Telugu) | Gold context | 4.76 | 4.80 |
| TE (Telugu) | RAG | 4.29 | 4.40 |
| KN (Kannada) | Gold context | 4.50 | 4.64 |
| KN (Kannada) | RAG | 3.06 | 3.48 |
| ML (Malayalam) | Gold context | 4.80 | 4.68 |
| ML (Malayalam) | RAG | 3.90 | 3.64 |
