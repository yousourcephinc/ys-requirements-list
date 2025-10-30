---
content_hash: 99005ef9548e01192ceb990e26ccc52c
created_at: '2025-10-31T06:18:06.034613'
division: se
maturity: foundational-1
title: Data Layer
---

Also, more often the data gateways are just an abstraction layer for data access.

<br>

Consider the interface below:

`IOrderDataGateway` with a method:

`Task<IEnumerable<Order>> GetOrdersAsync(.....)`

Having the interface above allows flexibility of implementing for example an SQL-based data access, No-SQL, and many more:

`OrderSqlDataGateway` or `OrderCosmosDbDataGateway` or `OrderApiDataGateway`

<br>

The data layer should throw a custom exception type often `DataException` so that it does not couple to implementation-specific exceptions such as `SqlException`. In this way, the Service layer can handle exceptions without having to be aware of how the data layer was implemented

<br>

The data layer is only expected to contain "data access" code such as stored procedure calls for SQL implementation, or Entity Framework queries for EF implementation.