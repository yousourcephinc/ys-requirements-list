---
title: "Security   General"
division: "SE"
maturity: "Foundational 1"
source_url: https://www.notion.so/SE-Security-General-2a4a172b65a381eca682c4dc5d6073f8
---

- Do configure CORS to only allow valid origins such as your SPA (Frontend)
- Use environment configuration to store URLs
- Do ensure all controllers have `[Authorize]` attributes. Public API endpoints such as register and login can obviously be public by using the `[AllowAnonymous]` attribute
- Do use `[AllowAnonymous]` at the method/action level so that you will not mistakenly publicize the whole controller/endpoint
- Do ensure role-based authorization using `[Authorize(Roles="Rolename")]` attribute
- You can also include multiple roles by using comma e.g. `Admin,Customer`
- Do create custom authorization rules using policies e.g. `[Authorize(Policy="MyCustomPolicy")]`
- Do use SSLs (https)