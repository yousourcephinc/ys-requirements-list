---
title: "User Profile -"
division: "EXD"
maturity: "Growth 1"
source_url: https://www.notion.so/User-Profile-Growth-1-1e8a172b65a380189017dd370fd516fe
---

## Module Requirements
## User Flow
## **Design Principles & Best Practices**
    **1. Layout & Structure**
    - Uses consistent form layout with grouped fields (e.g., profile info, credentials)
    - Clear sectioning between editable vs. non-editable fields
    - Includes consistent hierarchy across all sub-flows (e.g., reset password, edit info)
    - Displays predictable form structure with logical field progression
    **2. Visual Design & Branding**
    - Applies brand-aligned form elements (inputs, buttons, alerts)
    - Uses visual cues (icons, tooltips, labels) to distinguish editable vs. locked fields
    - States (default, hover, focus, error, success) clearly defined across forms
    - Includes organization-specific UI (e.g., logos, badges, themes) for SSO/role-based flows
    **3. Usability & Interaction**
    - Form interactions provide real-time feedback (validation, tooltips, character limits)
    - Displays loading, success, error, and empty states clearly and consistently
    - Password fields follow usability guidelines (toggle visibility, strength meter, confirm match)
    - Profile save/edit workflows include undo or cancel affordances
    **4. Responsiveness & Accessibility**
    - Responsive design handles various form widths and mobile layouts gracefully
    - Inputs and buttons follow tap-friendly sizing and spacing
    - Includes keyboard navigability and screen reader-friendly labeling
    - Maintains accessible contrast and semantic structure for forms and messages
    **5. Handoff & Design Consistency**
    - Reuses design tokens for input fields, button states, alerts, and icons
    - All form states (error, loading, disabled, success) included in design files
    - Design system components used for consistency across flows
    - Annotated designs explain conditional logic, validation rules, and tooltip behaviors
## Prototype Checklist
  - [ ] Add **SSO login screen** with branding for supported identity providers.
  - [ ] Clearly label the **“Login with Org Account”** option for SAML-based flows.
  - [ ] UI adjusts dynamically based on **selected login method** (e.g., username/password vs. SSO).
  - [ ] Display **post-login role or organization-specific visual cues** (e.g., company name, badge).
  - [ ] Show **logout confirmation modal** and link session management to user profile.
  - [ ] Include screen for **“You’ve been logged out due to inactivity”** with re-login options.
  - [ ] Add a **role-based dashboard preview** to confirm proper access (if applicable).
  - [ ] Visualize **authentication logs or login activity** (basic timeline or last login alert).
  - [ ] Ensure prototype is **responsive and optimized for mobile**.
  - [ ] Include guidance for **empty/error states on login or access screens**.
## Prototype
  [prototype link here]
## Examples
## References
