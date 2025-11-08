---
title: "Cors"
division: "SE"
maturity: "Foundational 1"
source_url: https://www.notion.so/SE-Cors-2a4a172b65a381b2934ff145dafff00f
---

Do configure CORS; it allows requests only for certain origins (like a Frontend). In your Startup.cs (API project), you will have a line similar to this.
<br>
``` var allowedOrigins = Configuration.GetSection("AllowedOrigins").AsEnumerable(); string[] origins = allowedOrigins.Select(o => o.Value).Where(v => !string.IsNullOrEmpty(v)).ToArray(); services.AddCors(options => { options.AddPolicy(AppCors, builder => builder.WithOrigins(origins) .AllowAnyMethod() .AllowAnyHeader() .AllowCredentials()); }); ```
<br>
And in your appSettings, you can add more `"AllowedOrigins"` as necessary.
``` ... { "AllowedOrigins": [ "https://sample.com" ] } ... ```
<br>
**\*Note:** that this measure comes by default if you used our [ASP.NET Core Seed](https://app.nuclino.com/Yousource/Engineering/ASPNET-Core-6-Seed-841ac9ff-5741-4ef6-9c6d-ece3245dd357 "Nuclino")