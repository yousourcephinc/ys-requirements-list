---
content_hash: 7ef56746f5d15cd1177f89d6a3c260fe
created_at: '2025-10-31T06:18:06.040276'
division: se
maturity: foundational-1
title: Service Layer
---

Is simply where the logic is placed. Keep reusability or SRP in mind when creating services. A good example is Email Service for reusability, and Order Service for applying SRP i.e. isolating the complexity of the ordering process into a service.

<br>

Creating a service does not limit to the service class itself. You can have multiple classes used by a service such as implementation of a design pattern and so on.

<br>

Our standard approach is to create services in a separate class library. This is for the use case when they are needed to deploy as a standalone service e.g. Azure Function, then we can easily create a pipeline for one project/csproj

<br>

<br>