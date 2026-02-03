---
title: "QA- Support Module Intro 2"
division: "QA"
maturity: "Introduction 2"
source_url: https://www.notion.so/QA-Support-Module-Intro-2-2fba172b65a380359902eeb9e0e870d6
---

### **Functional Requirements**
  - Verify that users can ask for help through a form inside the app with fields like subject, description, and issue type.
  - Check that when a support request is submitted, it reaches the company’s help desk tool and is properly recorded.
  - Confirm that users see a thank-you or confirmation message after sending their request.
  - If file uploads are allowed, test that users can attach screenshots or documents to their request.
  - If the system supports it, check that users can view the status of their past support requests or get a link to track them.
### **Security Requirements**
  - Make sure that access to the help desk tool is safe and that no sensitive information (like login keys) is visible in the app.
  - Validate that the user’s message is cleaned and safe before being sent.
  - Try submitting many support requests in a short time and confirm the system blocks abuse or spam.
### **Performance Requirements**
  - Submit a request and check that the app continues working while the request is being processed.
  - Simulate the help system being unavailable and confirm the app shows a helpful message (e.g., “Please try again later”).
  - Ensure that submitting a support request doesn’t cause the app to slow down or freeze.
### **Usability Requirements**
  - Check that the support form is easy to use and well-placed in the app.
  - Confirm that it’s clear which fields are required, and that users see helpful warnings if anything is missing.
  - Validate that users get clear feedback whether the request was sent successfully or not.
  - Test the form on different devices and screen sizes to ensure everything displays properly and is easy to use.