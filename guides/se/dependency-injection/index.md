---
title: "Dependency Injection"
division: "SE"
maturity: "Foundational 1"
source_url: https://www.notion.so/SE-Dependency-Injection-2a4a172b65a381069c7ae5dbfd198b68
---

- Do create extension methods/classes to contain related dependency injection
- Do not create a separate class library project to share injection configurations (this introduces coupling or interfaces' implementations can be hard to change)
- Do use appropriate Lifetime for injected dependencies
- Most of the time `Scoped` is the way to go. Use `Transient` and `Singleton` with care ([read more](https://docs.microsoft.com/en-us/aspnet/core/fundamentals/dependency-injection?view=aspnetcore-6.0 "Dependency injection in ASP.NET Core"))
- Do configure `HttpClientFactory` for `HttpClient` usage.&#x20;