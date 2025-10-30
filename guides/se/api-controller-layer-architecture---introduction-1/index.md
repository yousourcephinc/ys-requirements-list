---
content_hash: 4027911396160a7b53cad192818360d3
created_at: '2025-10-31T05:49:28.926364'
division: se
maturity: introduction-1
title: API Controller Layer Architecture
---

**In summary:**

- Point of entry and exit; interface to the outside world
- Thin; only responsibility is to send request to services and return results as responses
- Proxy/gateway for common functionalities such as Authentication and Authorization
- Proxy/gateway for interacting with external services

  <br>

**Point of entry and exit and Thin**

We commonly use web clients like Angular. HTTP requests go "enters" the controller. While the services do the most logic, controllers are still expected to return the results in a meaningful format called a Response.&#x20;

<br>

**Proxy/gateway for common functionalities...**

Functionalities that are common or shared in order to achieve certain behaviors are developed in the API layer. Best example is authentication and authorization. This prevents us duplication, adhering to DRY principle. Some other behaviors include:

- Exception handling and logging
- Caching
- Security
- Throttling
- Routing/Proxying as discussed below

  <br>

**Proxy/gateway for interacting with external services**

Having the API will ensure clients to be interacting only with 1 endpoint, abstracting all other calls to external services (e.g. API).