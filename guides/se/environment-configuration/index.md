---
title: "Environment Configuration"
division: "SE"
maturity: "Foundational 1"
source_url: https://www.notion.so/SE-Environment-Configuration-2a4a172b65a38126bf66cd2165252f6a
---

- Do use the recommended configuration technique by ASP.NET: appsettings.json files
- Do create separate separate config files for each environment
- Do use the `ConnectionStrings` section of the appsettings.json
- Do use secret storages like Azure Key Vault for production
- Do include values that may change frequently as part of your config such as flags (boolean) that toggles certain features on and off, etc.
