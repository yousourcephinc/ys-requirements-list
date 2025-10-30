---
content_hash: b9e6632dc7a1a75d6d98978c04013bb3
created_at: '2025-10-31T06:40:23.366235'
division: se
maturity: foundational-1
title: "\U0001F91EPromises"
---

A *promise* is a placeholder for a future value.\
In Typescript, you can create a promise by simply instantiating a new **Promise** class, like so:

```
var promise = new Promise((resolve, reject) => {});

```

The Promise then has an inner function that takes two arguments, **resolve** and **reject**. The arguments resolve and reject are functions themselves.

Normal and successful execution of promises are properly finished by **resolve()**:

```
function doAsyncTask() {
  var promise = new Promise((resolve, reject) => {
    setTimeout(() => {
      console.log("Async Work Complete");
      resolve();
    }, 1000);
  });
  return promise;
}

```

If there was an error in the async task, the **reject()** function is called instead:

```
function doAsyncTask() {
  var promise = new Promise((resolve, reject) => {
    setTimeout(() => {
      console.log("Async Work Complete");
      if (error) {
        reject();
      } else {
        resolve();
      }
    }, 1000);
  });
  return promise;
}

```

Both **resolve()** and **reject()** could also return values:

```
function doAsyncTask() {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      if (error) {
        reject('error'); // pass values
      } else {
        resolve('done'); // pass values
      }
    }, 1000);
  });
}

```

When a promise gets resolved or rejected, a notification could be issued using the **then** function. The **then()** can take either one or two arguments; the first argument being the value returned by resolve() if there’s any, and the second argument returns the value passed from reject().

```
doAsyncTask().then(() => console.log("Task Complete!"));

```

```
doAsyncTask().then(
  (val) => console.log(val),
  (err) => console.error(err)
);
```

<br>