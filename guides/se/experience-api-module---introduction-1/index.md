---
title: "Experience API Module - Introduction 1"
division: "SE"
maturity: "Introduction 1"
source_url: https://www.notion.so/Experience-API-Module-Introduction-1-2bea172b65a38072b021df84dd2cd02e
---

## 1. Functional Requirements
- Implement an **Experience API layer** using the **Page Controller Pattern**. Each page, view, or major UI workflow has a dedicated controller/endpoint that orchestrates backend calls and shapes responses for the client.
- Define **clear, documented routes** that reflect the UI/experience (e.g., `/dashboard/overview`, `/profile/details`, `/orders/list`) rather than raw entity CRUD endpoints.
- Use appropriate **HTTP verbs**:
  - `GET` for read-only views/data
  - `POST` for actions and commands (create, non-idempotent operations)
  - `PUT/PATCH` for updates (when needed)
  - `DELETE` for deletions (if exposed via Experience API)
- Standardize **HTTP status codes** for Experience API responses:
  - `2xx` for success (`200`, `201`, `204`)
  - `4xx` for client errors (`400`, `401`, `403`, `404`, `422`)
  - `5xx` for server errors (`500`, `502`, `503`)
- Implement **authorization checks** on each Experience API endpoint:
  - Require a **valid token** (JWT, access token, or equivalent).
  - Validate **roles and claims** to ensure the caller can access the requested resource/view.
- Implement **basic throttling** at the Experience API boundary:
  - Configure a **per-client/per-token request limit** (e.g., X requests per minute) to prevent abuse.
- Capture **essential metrics** per endpoint:
  - Average response time
  - Request count
  - Error rate (4xx/5xx)
  - Optionally, per-tenant/per-client usage counts
## 2. Security Requirements
- Expose all Experience API endpoints only over **HTTPS**.
- Validate and verify **access tokens** (signature, issuer, audience, expiration).
- Enforce **role- and claim-based authorization**:
  - Map UI flows to the minimum set of required roles/permissions.
  - Return `403 Forbidden` when the token is valid but access is not allowed.
- Ensure no sensitive information (e.g., stack traces, internal IDs, infrastructure details) is returned in error bodies.
- Normalize error responses into a **standard error envelope** (e.g., `{ code, message, details? }`) to prevent information leaks.
- Log security-relevant events (authorization failures, throttling events) for later analysis.
## 3. Performance Requirements
- Target a baseline **P95 response time** (e.g., < 500–800 ms depending on context) for all Experience API endpoints.
- Ensure each Page Controller aggregates data efficiently:
  - Minimize **chatty downstream calls** (prefer fewer, richer backend requests).
  - Use batching or fan-out/fan-in patterns when calling multiple services.
- Implement **basic throttling** with lightweight counters:
  - In-memory throttling is acceptable at this level if there is only one instance, or as a stepping stone to distributed limits.
- Avoid over-fetching data. Shape responses to match what the front-end page actually needs.
## 4. Usability Requirements (API UX)
- Design responses around **UI needs**, not database schemas:
  - Use view models tailored to the screen/workflow.
  - Provide pre-composed data where possible (e.g., `displayName`, `formattedDates`).
- Ensure **consistent status codes and response envelope** across endpoints:
  - Use the same success and error structure for all Experience API calls.
- Include **human-readable error messages** that the frontend can display directly or map to localized strings.
- Document common **error scenarios** (validation errors, unauthorized, forbidden, throttled) so frontend teams know how to handle them.
## 5. Authorization Requirements
- Enforce authorization **at the Experience API boundary**:
  - Reject unauthenticated requests with `401 Unauthorized`.
  - Reject unauthorized roles/claims with `403 Forbidden`.
- Map **routes/endpoints** to required permissions:
  - E.g., `/admin/**` requires `Admin` role; `/tenant/**` requires a matching tenant claim.
- Ensure authorization decisions are **idempotent and deterministic**:
  - Always rely on server-side token data—never UI hints.
## 6. Applicable Architectural Patterns
- **Page Controller Pattern** — each endpoint acts as a controller for a specific page or UX flow, composing data for that view.
- **API-Driven UI** — UI screens load their data via Experience API endpoints shaped for that screen.
- **Secure API Design** — consistent validation, authorization, and error handling across endpoints.
- **Basic Rate Limiting** — simple request-per-time-window limits per client.
## 7. Execution Checklist
- [ ] Page Controller endpoints exist for each key screen/flow (e.g., dashboard, profile, order list).
- [ ] Routes and HTTP verbs follow the agreed naming and REST semantics.
- [ ] Status codes are standardized and error responses follow a consistent envelope.
- [ ] Token validation, roles, and claims are checked on every endpoint.
- [ ] Basic per-client throttling is enforced (e.g., X requests per minute).
- [ ] Metrics for request count, average response time, and error rate are captured and viewable.
- [ ] No sensitive data is exposed in error messages.
- [ ] Performance is acceptable (P95 targets met in test/stage).