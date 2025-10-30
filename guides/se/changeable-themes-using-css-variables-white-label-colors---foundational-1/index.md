---
content_hash: 9cf548c76120f303f47b4f0912cca61f
created_at: '2025-10-31T06:40:23.364013'
division: se
maturity: foundational-1
title: Changeable Themes Using Css Variables (White Label Colors)
---

When implementing changeable themes for your web pages, the code should already be built to use primary and secondary colors via SCSS variables. Since sass variables are only applied when the application is built, they cannot be changed in real time. This is a problem when integrating themes.

<br>

The solution to this problem is converting SCSS variables into CSS variables. CSS variables are similar to SCSS variables but it’s integrated into the browser and can be dynamically changed.

+-------------------------------+
|//From                         |
|                               |
|$primary: rgb(276, 123, 67);   |
|                               |
|.box {                         |
|                               |
|    background: $primary;      |
|                               |
|}                              |
+-------------------------------+
|//To                           |
|                               |
|\--primary: rgb(276, 123, 67); |
|                               |
|.box {                         |
|                               |
|    background: var(--primary);|
|                               |
|}                              |
+-------------------------------+

<br>

Do not forget to set the default values for these variables. It is recommended to put all of these variables into one place, preferably in the file called \_variables.scss under root.

+-------------------------------------+
|:root {                              |
|                                     |
|  --primary: rgb(238, 0, 137);       |
|                                     |
|  --primary-light: rgb(255, 65, 174);|
|                                     |
|  --primary-dark: rgb(140, 0, 81);   |
|                                     |
|}                                    |
+-------------------------------------+

<br>

To set the values in real time, use this line of code in your TS/JS code.

| document.documentElement.style.setProperty('--primary', ’rgb(238, 0, 137)’); |
| ---------------------------------------------------------------------------- |

<br>

**General Tips**

1. SCSS functions that are used to manipulate color cannot be used anymore so find an alternative way to do this.

<br>

+------------------------------------------------------------------------------+
|// Method to change a color hex code into numbers                             |
|                                                                              |
|    getRgbFromHex(hex: string): RgbModel {                                    |
|                                                                              |
|        const rPart = parseInt(hex.substring(0, 2), 16).toString() ?? '0';    |
|                                                                              |
|        const gPart = parseInt(hex.substring(2, 4), 16).toString() ?? '0';    |
|                                                                              |
|        const bPart = parseInt(hex.substring(4, 6), 16).toString() ?? '0';    |
|                                                                              |
|        return {                                                              |
|                                                                              |
|            r: rPart,                                                         |
|                                                                              |
|            g: gPart,                                                         |
|                                                                              |
|            b: bPart                                                          |
|                                                                              |
|        };                                                                    |
|                                                                              |
|    }                                                                         |
+------------------------------------------------------------------------------+
|// Method to lighten or darken a color                                        |
|                                                                              |
|    lightenDarkenColor(color: RgbModel, amount: number): RgbModel {           |
|                                                                              |
|        return {                                                              |
|                                                                              |
|            r: this.borderHexValue(parseInt(color.r, 10) + amount).toString(),|
|                                                                              |
|            g: this.borderHexValue(parseInt(color.g, 10) + amount).toString(),|
|                                                                              |
|            b: this.borderHexValue(parseInt(color.b, 10) + amount).toString() |
|                                                                              |
|        } as RgbModel;                                                        |
|                                                                              |
|    }                                                                         |
|                                                                              |
|<br>                                                                          |
+------------------------------------------------------------------------------+

<br>

2. If you’re going to use the lighter and darker versions of the primary color, make sure to make CSS variables for those too like in the example and to change those variables when the primary color changes.
3. Store the color data being used in the local cache of the browser so that the theme colors are used immediately without having to wait for the fetching of those data to finish after each reload.