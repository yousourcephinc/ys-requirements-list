---
title: "Support Module - Introduction 1"
division: "SE"
maturity: "Introduction 1"
source_url: https://www.notion.so/Support-Module-Introduction-1-1c1a172b65a380bab6a5d547b7580382
---

### Functional Requirements
1. Provide **self-service support** via a **static FAQ section**:
  - FAQs are user-facing and searchable.
  - Content is served from a Markdown file or embedded third-party widget.
1. Display the FAQ section prominently in relevant areas of the app (e.g., footer, help pages, onboarding).
1. Include instructions for contacting support by **emailing a dedicated support address**.
1. The app does **not send emails directly** — users initiate contact using their **own email client**.
1. Provide a clear **mailto link** (e.g., `mailto:support@example.com`) to launch the user's default email app with pre-filled subject/template.
### Security Requirements
1. Ensure **FAQ content is sanitized** if editable to prevent injection attacks.
1. Do not collect or track email messages initiated through the user's external email client.
### Performance Requirements
1. Load FAQ content efficiently with minimal impact on core app performance.
1. Use caching or CDN delivery if FAQ content is served from static files or external services.
### Usability Requirements
1. Make the support email link **easily discoverable** within the app.
1. Ensure FAQ content is structured and readable across all devices.
1. Provide **visual cues and suggested keywords** to help users navigate the FAQ section.
## Applicable Architectural Patterns
- **Static Content Delivery**: For serving lightweight, searchable FAQ content.
- **Mailto URI Scheme**: For launching external email clients directly.
## Execution Checklist
- FAQ section is accessible and searchable by users.
- No in-app messaging is implemented — support is handled via external email.
- A dedicated mailto link is visible and functional.
- FAQ content is secure, readable, and performant.
- UI provides a helpful self-service experience.
