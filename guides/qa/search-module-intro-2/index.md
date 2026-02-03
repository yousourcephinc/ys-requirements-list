---
title: "Search Module Intro 2"
division: "QA"
maturity: "Introduction 2"
source_url: https://www.notion.so/QA-Search-Module-Intro-2-2fba172b65a380b4b098dde3ce094958
---

### **Functional Requirements**
  - Check that search sends a request to the server when typing.
  - Confirm that results are shown in sections or pages.
  - Verify that filters and sort settings apply correctly to search results.
### **Performance Requirements**
  - Observe the slight pause before each search request is sent.
  - Confirm that users see a loading message or spinner while waiting.
  - Validate that previously searched terms load quickly when repeated.
### **Accessibility Requirements**
  - Test how search behaves on phones, tablets, and desktops.
  - Check that loading updates are easy to notice for screen reader users.
  - Ensure focus remains on the search area when using keyboard navigation.
### **Security Requirements**
  - Confirm users need to be logged in to perform search (if required).
  - Validate search input cannot break the system (e.g., with symbols or code).
  - Check that search results match the user's role and access rights.
### **Execution Checklist / Test Scenarios**