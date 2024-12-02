---
layout: home
permalink: index.html

# Please update this with your repository name and title
repository-name: e20-co227-Artery-Resolver
title: Artery Resolver
---

[comment]: # "This is the standard layout for the project, but you can clean this and use your own template"

# A software to aid analysis of flow mediated dialation of arteries 

---

<!-- 
This is a sample image, to show how to add images to your page. To learn more options, please refer [this](https://projects.ce.pdn.ac.lk/docs/faq/how-to-add-an-image/)

![Sample Image](./images/sample.png)
 -->

## Team
-  E/20/054, Mineth De Croos, [e20054@eng.pdn.ac.lk](mailto:e20054@eng.pdn.ac.lk)
-  E/20/285, Methmi Ravindi, [e20285@eng.pdn.ac.lk](mailto:e20285@eng.pdn.ac.lk)
-  E/20/449, Sandharu Wijewardhana, [e20449@eng.pdn.ac.lk](mailto:e20449@eng.pdn.ac.lk)
-  E/20/288, Chalaka Perera, [e20288@engdn.ac.lk](mailto:e20288@eng.pdn.ac.lk)

## Table of Contents
1. [Introduction](#introduction)
2. [Other Sub Topics](#other-sub-topics)
3. [Links](#links)

---

## Introduction

 Software for flow-mediated dilation (FMD) analysis provides automated tools for accurately assessing arterial function by measuring changes in vessel diameter and blood velocity in response to blood flow changes.
 Artery Resolver is a software for the estimation of early markers of cardiovascular risk. In particular, the software is composed of two main modules of measurement:
   Average diameter calculation
   Average flow velocity calculation

The device is based on an algorithm that identifies the edges of the arterial vessel by analyzing ultrasound scanning video by breaking it into sequences of ultrasound images frames. We have used a machine learning model to enhance the diameter calculation part and an openCV model to calculate flow velocity. 

The software must be used by trained and qualified personnel, such as laboratory technicians, nurses, physicians and / or sonographers.

#
## Hardware part which is used to get the inputs for the software
![WhatsApp Image 2024-12-01 at 21 43 31_8f6556f4](https://github.com/user-attachments/assets/03546db5-7157-4135-aee7-d577a5a8950c)

# Interfaces

## Login Interface
![WhatsApp Image 2024-12-01 at 21 43 31_57dd7b7c](https://github.com/user-attachments/assets/68ccf143-3c9d-4e12-9058-8b86f7de7631)

## Doctor Registraton Interface
![WhatsApp Image 2024-12-01 at 21 43 27_96f77396](https://github.com/user-attachments/assets/d0fe10ea-0cd4-4735-806b-abebe6741104)

## Patient Registration Interface
![WhatsApp Image 2024-12-01 at 21 43 32_67ccf15c](https://github.com/user-attachments/assets/f478ae4e-2020-49d3-89c9-6ed6ffc147dc)

## Summerized Report Interface
![WhatsApp Image 2024-12-01 at 21 43 28_4671d6fa](https://github.com/user-attachments/assets/fe4dae14-2a1b-4d17-8575-47ca47a65088)


# Key Features

## The Region of Interest (ROI)
![WhatsApp Image 2024-12-01 at 16 16 22_cb2a1a99](https://github.com/user-attachments/assets/c8e76861-afc7-41ff-aa9b-d4b05bffde38)

![WhatsApp Image 2024-12-01 at 16 16 22_46ead7a2](https://github.com/user-attachments/assets/bfa90d91-2e44-4940-b24a-8fdf4522073f)

## The graph shows the trend of the time averaged diameter you can obtain after running the diameter calculation part in the software

![WhatsApp Image 2024-12-01 at 16 16 20_86d35026](https://github.com/user-attachments/assets/c2bcdbfd-cbe5-4980-9103-26f374660235)

## The graph shows the trend of the live time averaged diameter you can obtain after running the flow velocity calculation part in the software

![WhatsApp Image 2024-12-01 at 21 43 29_75447aa4](https://github.com/user-attachments/assets/92161c61-75e5-421f-9ca5-f195fc016901)



## Links

- [Project Repository](https://github.com/cepdnaclk/e20-co227-Artery-Resolver){:target="_blank"}
- [Project Page](https://cepdnaclk.github.io/{{ page.repository-name}}){:target="_blank"}
- [Department of Computer Engineering](http://www.ce.pdn.ac.lk/)
- [University of Peradeniya](https://eng.pdn.ac.lk/)


[//]: # (Please refer this to learn more about Markdown syntax)
[//]: # (https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet)
