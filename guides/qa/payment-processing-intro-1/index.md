---
title: "Payment Processing Intro 1"
division: "QA"
maturity: "Introduction 1"
source_url: https://www.notion.so/QA-Payment-Processing-Intro-1-2e2a172b65a38067a32bff0bbc07b05c
---

### Functional Requirements
  - Check if users can pay once or set up automatic monthly payments.
  - Make sure the payment form (either built-in or customized) loads properly.
  - Test if the system checks all required fields before submitting (e.g., name, card info).
  - Confirm that no card numbers or sensitive payment details are saved in the system.
  - Ensure users always see a clear message if the payment went through or failed.
### Security Requirements
  - Verify that all payment pages and forms are accessed through a secure website (starts with https://).
  - Check that the system accepts payment updates only from trusted sources.
  - Confirm that private payment info is not stored, shown, or written in any logs.
  - Try sending fake payment updates and make sure they’re rejected.
### Transaction Handling
  - Confirm that payment status (paid, failed, pending) updates correctly after every attempt.
  - Make sure each record includes the reference number, name of the user, total amount, payment type, and status.
  - Simulate a failed payment and check if the system shows it correctly and keeps a record.
### Performance & User Experience
  - Measure how fast the form loads and responds after a user clicks “Pay.”
  - Confirm the system does not freeze or slow down when submitting payment.
  - Check if users see a loading symbol or message while waiting for payment to complete.
### Integration Readiness
  - Verify that updates from the payment provider correctly reflect on the user’s screen and system records.
  - Check if every payment is correctly linked to the account that made it.
  - Run several payments at the same time and make sure the system keeps up without errors.