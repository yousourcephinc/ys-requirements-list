---
title: "Changeable Themes Using Css Variables (White Label Colors)"
division: "SE"
maturity: "Foundational 1"
source_url: https://www.notion.so/SE-Changeable-Themes-Using-Css-Variables-White-Label-Colors-2a4a172b65a3815390ddc301216ae5c7
---

When implementing changeable themes for your web pages, the code should already be built to use primary and secondary colors via SCSS variables. Since sass variables are only applied when the application is built, they cannot be changed in real time. This is a problem when integrating themes.
<br>
The solution to this problem is converting SCSS variables into CSS variables. CSS variables are similar to SCSS variables but it’s integrated into the browser and can be dynamically changed.
+-------------------------------+ |//From                         | |                               | |$primary: rgb(276, 123, 67);   | |                               | |.box {                         | |                               | |    background: $primary;      | |                               | |}                              | +-------------------------------+ |//To                           | |                               | |\--primary: rgb(276, 123, 67); | |                               | |.box {                         | |                               | |    background: var(--primary);| |                               | |}                              | +-------------------------------+
<br>
Do not forget to set the default values for these variables. It is recommended to put all of these variables into one place, preferably in the file called \_variables.scss under root.
+-------------------------------------+ |:root {                              | |                                     | |  --primary: rgb(238, 0, 137);       | |                                     | |  --primary-light: rgb(255, 65, 174);| |                                     | |  --primary-dark: rgb(140, 0, 81);   | |                                     | |}                                    | +-------------------------------------+
<br>
To set the values in real time, use this line of code in your TS/JS code.
| document.documentElement.style.setProperty('--primary', ’rgb(238, 0, 137)’); | | ---------------------------------------------------------------------------- |
<br>
**General Tips**
1. SCSS functions that are used to manipulate color cannot be used anymore so find an alternative way to do this.
<br>
<br>
2. If you’re going to use the lighter and darker versions of the primary color, make sure to make CSS variables for those too like in the example and to change those variables when the primary color changes. 3. Store the color data being used in the local cache of the browser so that the theme colors are used immediately without having to wait for the fetching of those data to finish after each reload.