---
title: "Observables"
division: "SE"
maturity: "Foundational 1"
source_url: https://www.notion.so/SE-Observables-2a4a172b65a38134bfb3fb413b50904d
---

As a publisher, you create an **Observable** instance that defines a subscriber function. This is the function that is executed when a consumer calls the **subscribe()** method. The subscriber function defines how to obtain or generate values or messages to be published.
To execute the observable you have created and begin receiving notifications, you call its **subscribe()** method, passing an observer. This is a TypeScript object that defines the handlers for the notifications you receive. The subscribe() call returns a **Subscription** object that has an unsubscribe() method, which you call to stop receiving notifications. The image below shows basic usage of Observables:
*Observables* provide support for passing messages between parts of your application. They are used frequently in Angular and are the recommended technique for **event handling, asynchronous programming, and handling multiple values**.
![](https://lh4.googleusercontent.com/xHz-vh5roIq5Ot3a43IHm1zzuzJRW2bRYOPxHWMxKoM6Fj1thPUW1UA4hIwu44HNvqq9KQFWPnmSxH6OCagnG0Zpc3qmTnMRw0g8YLC-pbgGDxqCd12IDU5q4hRTo8ak-um5rUnT)
<br>