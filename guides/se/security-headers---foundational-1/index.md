---
content_hash: 9727ec2d31d1c31ff4e79a84f8151d75
created_at: '2025-10-31T06:40:23.373137'
division: se
maturity: foundational-1
title: Security Headers
---

From OWASP Top 10, in order to prevent malicious attacks, it is advised to add additional headers as well as to include in your API responses to keep the application secure.

<br>

In your `Startup.cs`, you can add the following:

<br>

```
app.Use(async (context, next) =>
            {
                context.Response.Headers.Add("X-Frame-Options", "deny");
                context.Response.Headers.Add("X-Content-Type-Options", "nosniff");
                context.Response.Headers.Add("X-Xss-Protection", "1");
                context.Response.Headers[HeaderNames.CacheControl] = "no-cache, no-store";
                await next().ConfigureAwait(false);
            });
```

<br>