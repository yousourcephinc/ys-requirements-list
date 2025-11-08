---
title: "Performance"
division: "SE"
maturity: "Foundational 1"
source_url: https://www.notion.so/SE-Performance-2a4a172b65a381bea366dd5b94993941
---

The following items are kept high level and must be researched further for implementation. Most of the content are practices that we use that also came from Microsoft
<br>
### 1. Cache aggressively
See caching article for more information
### 2. Understand hot code paths
a *hot code path* is defined as a code path that is frequently called and where much of the execution time occurs. Hot code paths typically limit app scale-out and performance
### 3. Avoid blocking calls
ASP.NET Core apps should be designed to process many requests simultaneously. Asynchronous APIs allow a small pool of threads to handle thousands of concurrent requests by not waiting on blocking calls.
A common performance problem in ASP.NET Core apps is blocking calls that could be asynchronous
**Do not**:
- Block asynchronous execution by calling [Task.Wait](https://docs.microsoft.com/en-us/dotnet/api/system.threading.tasks.task.wait) or [Task\<TResult>.Result](https://docs.microsoft.com/en-us/dotnet/api/system.threading.tasks.task-1.result).
**Do**:
- Make [hot code paths](https://docs.microsoft.com/en-us/aspnet/core/performance/performance-best-practices?view=aspnetcore-6.0#understand-hot-code-paths) asynchronous.
- Call data access, I/O, and long-running operations APIs asynchronously if an asynchronous API is available. Do **not** use [Task.Run](https://docs.microsoft.com/en-us/dotnet/api/system.threading.tasks.task.run) to make a synchronous API asynchronous.
- Make controller/Razor Page actions asynchronous. The entire call stack is asynchronous in order to benefit from [async/await](https://docs.microsoft.com/en-us/dotnet/csharp/programming-guide/concepts/async/) patterns.
### 4. Return large collections across multiple smaller pages
A webpage shouldn't load large amounts of data all at once. When returning a collection of objects, consider whether it could lead to performance issues.
<br>
**Do** add pagination to mitigate the preceding scenarios. Using page size and page index parameters, developers should favor the design of returning a partial result. When an exhaustive result is required, pagination should be used to asynchronously populate batches of results to avoid locking server resources
<br>
For more information on paging and limiting the number of returned records, see:
- [Performance considerations](https://docs.microsoft.com/en-us/aspnet/core/data/ef-rp/intro?view=aspnetcore-6.0#performance-considerations)
- [Add paging to an ASP.NET Core app](https://docs.microsoft.com/en-us/aspnet/core/data/ef-rp/sort-filter-page?view=aspnetcore-6.0#add-paging)
### 5. Optimize data access and I/O
Interactions with a data store and other remote services are often the slowest parts of an ASP.NET Core app. Reading and writing data efficiently is critical for good performance.
Recommendations:
- Do** call all data access APIs asynchronously.
- Do not** retrieve more data than is necessary. Write queries to return just the data that's necessary for the current HTTP request.
- Do** consider caching frequently accessed data retrieved from a database or remote service if slightly out-of-date data is acceptable. Depending on the scenario, use a [MemoryCache](https://docs.microsoft.com/en-us/aspnet/core/performance/caching/memory?view=aspnetcore-6.0) or a [DistributedCache](https://docs.microsoft.com/en-us/aspnet/core/performance/caching/distributed?view=aspnetcore-6.0) (e.g. using redis). For more information, see [Response caching in ASP.NET Core](https://docs.microsoft.com/en-us/aspnet/core/performance/caching/response?view=aspnetcore-6.0).
- Do** minimize network round trips. The goal is to retrieve the required data in a single call rather than several calls.
Query issues can be detected by reviewing the time spent accessing data with [Application Insights](https://docs.microsoft.com/en-us/azure/application-insights/app-insights-overview) or with profiling tools. Most databases also make statistics available concerning frequently executed queries.
### 6. Keep common code paths fast
You want all of your code to be fast. Frequently-called code paths are the most critical to optimize. These include:
- Middleware components in the app's request processing pipeline, especially middleware run early in the pipeline. These components have a large impact on performance.
- Code that's executed for every request or multiple times per request. For example, custom logging, authorization handlers, or initialization of transient services.
### 7. Compress responses
[Response compression](https://docs.microsoft.com/en-us/aspnet/core/performance/response-compression?view=aspnetcore-6.0).
### 8. Minimize exceptions
Exceptions should be rare. Throwing and catching exceptions is slow relative to other code flow patterns. Because of this, exceptions shouldn't be used to control normal program flow.
Recommendations:
- Do not** use throwing or catching exceptions as a means of normal program flow, especially in [hot code paths](https://docs.microsoft.com/en-us/aspnet/core/performance/performance-best-practices?view=aspnetcore-6.0#understand-hot-code-paths).
- Do** include logic in the app to detect and handle conditions that would cause an exception.
- Do** throw or catch exceptions for unusual or unexpected conditions.
App diagnostic tools, such as Application Insights, can help to identify common exceptions in an app that may affect performance.