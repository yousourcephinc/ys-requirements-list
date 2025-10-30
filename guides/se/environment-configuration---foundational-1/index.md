---
content_hash: 339c8f7413ed50165e979dfbf6cd93eb
created_at: '2025-10-31T06:18:06.038276'
division: se
maturity: foundational-1
title: Environment Configuration
---

- Do use the recommended configuration technique by ASP.NET: appsettings.json files
- Do create separate separate config files for each environment
- Do use the `ConnectionStrings` section of the appsettings.json
- Do use secret storages like Azure Key Vault for production
- Do include values that may change frequently as part of your config such as flags (boolean) that toggles certain features on and off, etc.