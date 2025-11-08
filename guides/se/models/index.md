---
title: "Models"
division: "SE"
maturity: "Foundational 1"
source_url: https://www.notion.so/SE-Models-2a4a172b65a3812fb5b6c3d742177991
---

*General*
- Having multiple models of the same definition prevents coupling. An entity may contain business logic while models are just meant to display data. Very similar to a DTO (data transfer object)
- Models and Web Models are the same. They are just counterparts of the infrastructure model definition and web (api) model definition
- Make use of constructors so that you won't miss properties to be set
<br>
*Entities*
- Can contain other entities or relationships
- Can contain logic such as calculations
- Services should not return entities. They should return Models
*Models (Infrastructure)*
- Models are similar to DTOs
- Models are representation of data. They can be a combination of properties/data from multiple entities
*Web Models*
- Keep logic out of web models; their only role is to display (presentation) the values that has been set. How the values are calculated and/or set should be non of their concern. In this way, presentation is decoupled from business logic
- You may think of it this way: the UI (or also API) may always need to display the same data over and over again but it is not concerned on how the data was calculated, fetched, or processed
- Web models should be anemic similar to Infrastructure Models (getters and setters only)