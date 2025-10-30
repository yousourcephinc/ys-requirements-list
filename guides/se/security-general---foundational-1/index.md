---
content_hash: a8ec2151c80e464668fad1fb7a64f4b6
created_at: '2025-10-31T06:40:23.361699'
division: se
maturity: foundational-1
title: Security   General
---

- Do configure CORS to only allow valid origins such as your SPA (Frontend)
  - Use environment configuration to store URLs
- Do ensure all controllers have `[Authorize]` attributes. Public API endpoints such as register and login can obviously be public by using the `[AllowAnonymous]` attribute
  - Do use `[AllowAnonymous]` at the method/action level so that you will not mistakenly publicize the whole controller/endpoint
- Do ensure role-based authorization using `[Authorize(Roles="Rolename")]` attribute
  - You can also include multiple roles by using comma e.g. `Admin,Customer`
- Do create custom authorization rules using policies e.g. `[Authorize(Policy="MyCustomPolicy")]`
- Do use SSLs (https)