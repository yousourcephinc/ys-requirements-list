---
content_hash: 00f154ac4bd1d9cab542314819c4dfdd
created_at: '2025-10-31T05:54:20.375258'
division: se
maturity: foundational-1
title: Page Controller Pattern
---

> An object that handles a request for a specific page or action on a Web site. ***Martin Fowler***

This pattern is preferred when designing API controllers expected to be consumed by a Frontend, typically a SPA

We believe that this pattern has the following advantages over REST:

- A more straightforward structure of controllers: 1 page = 1 controller
- A more straightforward data modelling: what you see in the UI is similar to the model that the controller expects to be passed on

<br>

Best practices

- Do create one (1) controller for each frontend page you have&#x20;
  - Do create different actions as needed. For example a `POST` or `PATCH` in the same page controller. For example:
    - `POST api/register`
    - `POST api/login`
    - `POST api/login/forgot-password`
    - `GET api/dashboard`
  - Do consider creating a sub-route e.g. `api/page-controller/sub-path` if your page has a lot of responsibilities
  - Do use dash `-` to separate words in the route
- Do keep controllers thin (no logic). Usually 2 lines of code (call service, and return response)
- Do create `Request` models (`WebRequest`) for each method/action
- Do use `ModelState` for input/field validation using data annotations (attributes like `[Required]`)
- Do reuse `Services`
- Do use the `[Authorize]` attribute
  - Do combine with custom policies and roles
- Do return appropriate status codes
  - `201` for successful `POST`
  - `200` for successful `GET`
  - `422` for input validation errors
  - `400` for business logic validation errors
  - `429` for throttled requests
  - Other default status code returns such as `404`, `401`, `403`, `500`
- Do return Error Codes (string) for easier mapping and translating of error messages at the client side
  - Do use this convention for error codes: `service/error-code` e.g. `auth/duplicate-user`
- Do return `JSON`
- Do use `async-await`
- Do use API versioning
- Do use a generic, standard `WebResponse<T>` object that has the error code, and data (type T)