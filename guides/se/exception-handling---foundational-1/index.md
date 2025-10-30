---
content_hash: 0b43d3c8c42b8792f13efb2f9317ebb7
created_at: '2025-10-31T06:40:23.371300'
division: se
maturity: foundational-1
title: 'Exception Handling '
---

Exception handling should be in place for every layer or module in the system. Ensure that exceptions don't bubble out of their respective module or layer as this will create coupling between the modules.&#x20;

**Requirements for Definition of Done**

- [ ] Exceptions are logged to a common repository (insights, new relic, etc)
- [ ] Exceptions types do not bubble out of their respective layer(s). *To avoid coupling.*

Guidelines

A great (bad!) example of this is that of a SqlException being caught in a service layer. The service layer should not know about the persistence layer. If the developers responsible for persistence try to change the data store - the service layer will not function properly as there is a hard coupling between the layers because of this exception type.

The recommended way of dealing with this - is that the persistence layer itself should catch the error and convert it to for instance a PersistenceException, which is allowed to be caught in a higher layer.

- [ ] Every layer should have its own custom exception, as per the example.
- [ ] Never swallow exceptions. An exception is what it is and needs to be dealt with.&#x20;
- [ ] An exception should be converted to a layer type exception in order to propagate to the top.&#x20;
- [ ] Exceptions are logged in Insights, New Relic or otherwise made available.&#x20;
- [ ] Your QM will ensure a zero exception policy. Support this by registering the exceptions
- [ ] Avoid exceptions to begin with - validate your input before calling it.&#x20;

<br>

[Home](https://share.nuclino.com/p/General-DZfOBycayOaee6tPGrdZob)