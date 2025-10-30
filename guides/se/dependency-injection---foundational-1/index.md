---
content_hash: 07bb046268a935ecff79259a225f6736
created_at: '2025-10-31T06:40:23.372675'
division: se
maturity: foundational-1
title: Dependency Injection
---

- Do create extension methods/classes to contain related dependency injection
- Do not create a separate class library project to share injection configurations (this introduces coupling or interfaces' implementations can be hard to change)
- Do use appropriate Lifetime for injected dependencies
  - Most of the time `Scoped` is the way to go. Use `Transient` and `Singleton` with care ([read more](https://docs.microsoft.com/en-us/aspnet/core/fundamentals/dependency-injection?view=aspnetcore-6.0 "Dependency injection in ASP.NET Core"))
- Do configure `HttpClientFactory` for `HttpClient` usage.&#x20;