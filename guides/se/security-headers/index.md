---
title: "Security Headers"
division: "SE"
maturity: "Foundational 1"
source_url: https://www.notion.so/SE-Security-Headers-2a4a172b65a38198a6b8f99f110affcb
---

From OWASP Top 10, in order to prevent malicious attacks, it is advised to add additional headers as well as to include in your API responses to keep the application secure.
<br>
In your `Startup.cs`, you can add the following:
<br>
``` app.Use(async (context, next) => { context.Response.Headers.Add("X-Frame-Options", "deny"); context.Response.Headers.Add("X-Content-Type-Options", "nosniff"); context.Response.Headers.Add("X-Xss-Protection", "1"); context.Response.Headers[HeaderNames.CacheControl] = "no-cache, no-store"; await next().ConfigureAwait(false); }); ```
<br>