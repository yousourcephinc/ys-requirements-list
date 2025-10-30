---
content_hash: 0599f9f1de0a45efbbe039e84cf50cb9
created_at: '2025-10-31T06:40:23.364834'
division: se
maturity: foundational-1
title: Data Gateways
---

- Do return models (abstract) from data gateways
- Do not return persistence-specific times like Sql's DataTables because your data source may change at some point (breaks the abstraction principle)
- Do consider interface segregation for data access interfaces i.e. separating read, write, etc.
- Do name your data gateway implementations based on what it is using. For example `CustomerSqlDataGateway` for SQL then the interface should be `ICustomerDataGateway`
- Do consider the amount of data gateway calls to complete a transaction. Consider using a [Transaction Script](https://martinfowler.com/eaaCatalog/transactionScript.html "P of EAA: Transaction Script") if you find yourself concerned on rollbacks and performance (because a TS compiles multiple queries in one execution, therefore also opens and closes the database connection once rather than every data gateway execution)