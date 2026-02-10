---
title: "QA-"
division: "QA"
maturity: "Growth 1"
source_url: https://www.notion.so/QA-External-File-Sharing-Advanced-Controls-Growth-1-2fba172b65a380fcb7d4f68b213b7e08
---

### Functional Requirements
  - Test that users can create shareable links with expiration and password options.
  - Confirm that settings like time limits and passwords work during actual downloads.
  - Verify users can update or remove shared links when needed.
### Security Requirements
  - Try accessing expired or edited links to ensure they’re blocked.
  - Confirm file uploads are scanned for harmful content.
  - Verify disguised or unsafe files (e.g., .exe in .pdf) are caught and blocked.
  - Ensure downloads are logged with details like time and user info (if possible).
### Performance Requirements
  - Test uploads with poor or unstable internet connections.
  - Confirm large files are uploaded in chunks without failing.
  - Check sharing and download features remain fast during high activity.
### Integration & Compatibility
  - Verify links work across platforms like web and mobile.
  - Test if links can be turned off or revoked by uploader or admin.
  - Confirm download activity appears in the audit log.
  - Ensure private downloads (uploader-only) are enforced properly with login or code.