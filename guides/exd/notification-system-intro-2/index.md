---
title: "Notification System Intro 2"
division: "EXD"
maturity: "Introduction 2"
source_url: https://www.notion.so/Notification-System-Intro-2-28ea172b65a380b09439dbde1858816e
---

## Module Requirements
## User Flow
## **Design Principles & Best Practices**
  - [ ] **Layout & Structure**
    - [ ] Clear and scannable hierarchy: subject, greeting, message body, CTA, footer
    - [ ] Use of consistent grid/margin/padding within email containers
    - [ ] Logical grouping of content: header, message, variables, closing
    - [ ] Mobile-responsive layout (single-column stacking, appropriate padding)

  - [ ] **Visual Design & Branding**
    - [ ] Consistent use of brand colors, fonts, and logos
    - [ ] Message types visually differentiated (Info, Success, Warning, Error) through color/icons
    - [ ] No custom design overrides—strict adherence to static design templates
    - [ ] Visual balance maintained across various email lengths and content variations

  - [ ] **Usability & Interaction**
    - [ ] Email copy uses simple, human-readable language
    - [ ] Dynamic variables (e.g., {{customerName}}, {{loanAmount}}) formatted clearly
    - [ ] Clear and visible CTAs (if applicable)—or no CTA when simplicity is prioritized
    - [ ] All links styled for visibility and accessibility (e.g., underlined, brand color)

  - [ ] **Responsiveness & Accessibility**
    - [ ] Templates render well across devices and email clients (desktop & mobile)
    - [ ] Adequate font sizes and line spacing for readability
    - [ ] Sufficient contrast ratios for text, backgrounds, and status indicators
    - [ ] Touch-friendly link spacing for mobile users
## **Execution Checklist**
  - [ ] **Email Header** (company logo or app name)
  - [ ] **Greeting** (e.g., “Dear {{customerName}}”)
  - [ ] **Message Body** with variable fields (e.g., loan amount, reference ID)
  - [ ] **Visual Status Indicator** (type-based: Info, Success, Warning, Error)
  - [ ] **Timestamp** or event context (optional)
  - [ ] **Optional CTA** (e.g., “View Details”) or closing statement
  - [ ] **Email Footer** (company contact info, disclaimer)
  - [ ] **Static template layout** reused across notification types
  - [ ] **Preview-friendly layout** that renders correctly in Gmail, Outlook, Apple Mail
  - [ ] **Fallback content** if dynamic variables fail to load
  - [ ] **Testing across devices and clients** before deployment
  - [ ] **No interactive content** (no carousels, scripts—email-safe formatting only)
## Prototype
  [prototype link here]
## Examples
## References
