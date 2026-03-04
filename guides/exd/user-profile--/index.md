---
title: "User Profile -"
division: "EXD"
maturity: "Introduction 2"
source_url: https://www.notion.so/User-Profile-Intro-2-1e8a172b65a380daade8faedf196455a
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
  - [ ] Design includes **username/password login option** alongside social login buttons.
  - [ ] Add a **“Forgot password?” flow** with modal/page navigation.
  - [ ] Include **email input field with feedback** for valid/invalid address in reset flow.
  - [ ] Visualize the **token expired/success/error screen** in reset journey.
  - [ ] Create a screen for **“Enter new password”** with confirm password and strength indicator.
  - [ ] Display **rate-limit notice UI** after repeated reset attempts.
  - [ ] Design a **change password form** with current and new password fields.
  - [ ] Clearly separate **authentication and profile** sections in navigation/IA.
  - [ ] All flows should account for **success, error, loading, and disabled** states.
  - [ ] Designs follow **best practices for password UX** (e.g., show/hide toggle, strength meter).
## Prototype
  [prototype link here]
## Examples
## References
