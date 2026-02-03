---
title: "QA- Support Module Intro 1"
division: "QA"
maturity: "Introduction 1"
source_url: https://www.notion.so/QA-Support-Module-Intro-1-2e2a172b65a38049a1e4f2046971d402
---

### **Functional Requirements**
  - Verify that users can access a help section that includes frequently asked questions (FAQs).
  - Confirm the FAQ content is visible and searchable by keywords.
  - Check that FAQ content loads properly from a static source or embedded help widget.
  - Ensure the FAQ section appears in key areas like the website footer, help page, and onboarding screens.
  - Confirm there are clear instructions on how users can contact the support team by sending an email.
  - Validate that the system does not send emails itself — instead, the user’s own email app should open when contacting support.
  - Test that the “Contact Support” link opens the user’s email app with a pre-filled subject line and email address using the mailto format.
### **Security Requirements**
  - If the FAQ content can be edited, check that all displayed text is clean and does not allow any unwanted scripts or code.
  - Confirm that the app does not store or monitor any messages sent through the user’s external email app.
### **Performance Requirements**
  - Measure how quickly the FAQ section loads compared to other parts of the app.
  - If the FAQ is served from a file or external service, validate that it loads without delays and does not affect overall app speed.
  - Confirm caching behavior works as expected — FAQ content should not reload unnecessarily.
### **Usability Requirements**
  - Check that the “Contact Support” link is easy to find in all relevant pages.
  - Test the FAQ layout across different screen sizes (mobile, tablet, desktop) to ensure readability.
  - Verify that users see helpful hints or keyword suggestions to guide them when searching for answers in the FAQ section.