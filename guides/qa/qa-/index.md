---
title: "QA-"
division: "QA"
maturity: "Introduction 2"
source_url: https://www.notion.so/QA-Secure-File-Access-Role-Based-Controls-Intro-2-2fba172b65a380c3b671c35c4ca57565
---

### Functional Requirements
  - Check that users only see files they’re allowed to access.
  - Verify that role-based access is working (Admin, Viewer, etc.).
  - Confirm file visibility updates right after a user’s role changes.
  - Ensure users from other clients or groups can’t see unrelated files.
### Security Requirements
  - Test that access links expire correctly and block late access.
  - Attempt to access files across groups/tenants and confirm rejection.
  - Verify all file views/downloads are recorded with time and user info.
  - Confirm permission changes reflect immediately in both UI and backend.
### Accessibility & UX Standards
  - Check that restricted files are clearly marked or hidden.
  - Validate that denied access shows helpful error messages.
  - Ensure file visibility and controls work across all devices.
### Performance Requirements
  - Measure time to load file lists based on user role.
  - Check how fast the system applies permission checks under many users.
  - Test if switching roles or users refreshes file access correctly.
### Cross-Tenant Isolation
  - Try accessing files using direct links, IDs, or shared tokens—system must block it.
  - Verify that file activity logs show correct group/client assignment.
  - Confirm that switching accounts resets the file access state cleanly.
