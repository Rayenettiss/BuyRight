# Database Architecture for FinCommerce Intelligence Engine (BuyRight)

This document outlines the complete database structure for BuyRight. The system uses a hybrid architecture:
*   **Vector Database (Qdrant)**: For multimodal similarity search (semantic recommendations).
*   **Relational Database (PostgreSQL)**: For structured data like user profiles and transactions.

## 1. Overall Architecture

### Vector Database (Qdrant)
Handles embeddings for semantic/multimodal search.
*   **Collections**: `products` (main catalog).
*   **Features**: Uses HNSW indexing, payload filtering, and quantization.

### Relational Database (PostgreSQL)
Stores non-vector data for joins/queries.
*   **Source of Truth**: The relational database acts as the primary source of truth for structured data.

---

## 2. Current Implementation

The following models are currently implemented in `backend/app/models/product.py` and synced via `backend/app/routers/ingestion.py`.

### Products (PostgreSQL & Qdrant)

**Relational Model (`NormalizedProduct`)**
Represents the normalized product data after ingestion.

| Field | Type | Description |
| :--- | :--- | :--- |
| `title` | string | Product name. |
| `description` | string | Full text description. |
| `price` | float | Current price. |
| `currency` | string | Currency code (default "USD"). |
| `url` | string | Product URL. |
| `image_url` | string | URL to image. |
| `brand` | string | Product brand. |
| `original_id` | string | ID from source system. |
| `category` | string | Product category. |
| `stars` | float | Average rating. |
| `reviews_count` | int | Number of reviews. |

**Vector Chunk (`ProductChunk`)**
Represents chunked data for embedding in Qdrant.

| Field | Type | Description |
| :--- | :--- | :--- |
| `product_id` | string (UUID) | Unique identifier linking chunks. |
| `chunk_index` | int | Index of the chunk. |
| `text_content` | string | Text used for embedding. |
| `source` | string | Source filename/origin. |
| *Metadata* | - | Includes `title`, `price`, `currency`, `url`, `image_url` for fast retrieval. |

---

## 3. Planned Architecture (Future Work)

The following models are planned for future implementation to support user personalization, financial constraints, and feedback loops.

### Users (Planned)
Stores core user data for authentication and personalization.
*   **user_id**: UUID.
*   **email**: User's email.
*   **password**: Hashed.
*   **profession**: Job field (e.g., "developer") for tailored recs.
*   **income**: Monthly salary for budget calculations.
*   **price_sensitivity**: "high", "medium", "low".
*   **financial_goals**: Array of goals (e.g., "save for trip").

### Budgets (Planned)
Per-category budgets for flexible guardrails.
*   **budget_id**: UUID.
*   **user_id**: Link to user.
*   **category**: Product category.
*   **hard_max**: Strict ceiling.
*   **soft_max**: Flexible preference for value trade-offs.

### Transactions (Planned)
Logs user purchases for feedback and metrics.
*   **transaction_id**: UUID.
*   **user_id**: Link to user.
*   **product_id**: Link to product.
*   **amount**: Purchase amount.
*   **status**: "completed" / "abandoned".

### Recommendations (Planned)
Logs for evaluation and explainability.
*   **rec_id**: UUID.
*   **user_id**: Link to user.
*   **algorithm_score**: Score from Qdrant/Reranker.
*   **explanation**: Generated text reason for the recommendation.
*   **clicked**: Boolean for CTR tracking.
