---
title: "Subscription Management Intro 1"
division: "QA"
maturity: "Introduction 1"
source_url: https://www.notion.so/QA-Subscription-Management-Intro-1-2e2a172b65a38049841bc57e323ccd32
---

### **Functional Requirements**
  - Verify that users can subscribe to a plan through the system using the provided payment screen.
  - Confirm that the payment screen opens securely and shows the correct plan name and price.
  - Validate that the user is redirected to a confirmation page after successful payment.
  - Check that customer and subscription details (not card info) are saved properly in the system.
  - Test cancellation flow — users should be able to cancel their subscription easily.
  - Confirm that subscription status (active, canceled, etc.) updates correctly in the user's account or admin panel.
### **Security Requirements**
  - Validate that all subscription-related pages use a secure website connection (HTTPS).
  - Check that the system confirms any updates from Stripe (e.g., new subscription, cancellation) using a secure validation process.
  - Ensure that payment information is not stored in the system and only metadata is saved (e.g., user ID, plan name, status).
### **Performance Requirements**
  - Measure how long it takes for the subscription screen to load and process payments.
  - Confirm that the subscription status updates in real time or shortly after confirmation from the provider.
  - Test that webhooks from Stripe do not block the system or cause delays in the app.
### **Usability Requirements**
  - Ensure that the subscribe/cancel button is clearly labeled and easy to find.
  - Check that users get a clear success message after subscribing and canceling.
  - Validate the subscription flow on mobile and desktop to ensure layout and steps are user-friendly.
  - Confirm the user sees correct subscription status (e.g., "Active", "Canceled") in their account.