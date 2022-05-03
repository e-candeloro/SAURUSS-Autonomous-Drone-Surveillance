# SAURUSS: IoT & 3D Project

## WHAT IS IT?
**SAURUSS** stands for: **S**mart **A**utonomous **U**AV **R**ecognizer for **U**niversal **S**urveillance **S**ystem and it is a fully autonomous surveillance system that uses a drone and sensors to search and spot intruders over a perimeter.

This system employ:
- Computer Vison and Deep Learning algorithms to detect the presence of intruders and to guide a drone (Tello drone) with AruCo markers
- A bridge (Raspberry Pi 3) and perimeter sensors (Arduino Uno) with ad hoc Finite State Machines and communication protocols
- An Android smartphone app plus a Telegram Bot to communicate with the system remotely
- A backend server (Raspberry Pi 1) to handle the users data

## ABOUT THE PROJECT
SAURUSS is a group project developed for the course of [IoT & 3-D Systems (2020-2021)](https://offertaformativa.unimore.it/corso/insegnamento?cds_cod=20-262&aa_ord_id=2009&pds_cod=20-262-2&aa_off_id=2020&lang=ita&ad_cod=IIM-63&aa_corso=1&fac_id=10005&coorte=2020&anno_corrente=2022&durata=2) done at the [University of Modena and Reggio Emilia](https://www.ingmo.unimore.it/site/en/home.html).
#### Team Members:
- **Candeloro Ettore** ([LinkedIn](https://www.linkedin.com/in/ettore-candeloro-900081162/) - [GitHub](https://github.com/e-candeloro))
- **Garuti Thomas** ([LinkedIn](https://www.linkedin.com/in/thomas-garuti-135649196/) - [GitHub](https://github.com/Thomas-Garuti))
- **Millunzi Monica** ([LinkedIn](https://www.linkedin.com/in/monica-millunzi-1b70411b1/) - [GitHub](https://github.com/monnieka))
### DEMO VIDEO
https://user-images.githubusercontent.com/67196406/166443367-cc99dd4c-8b04-48ad-8701-01d4048b12a8.mp4
### OVERVIEW
![immagine](https://user-images.githubusercontent.com/67196406/166440670-5df8d9de-0e7b-4c6c-b7ed-d3a906639d62.png)

### FULL ARCHITECTURE
![General Architecture@2x(3)](https://user-images.githubusercontent.com/67196406/166441082-ca84c2bb-ade5-4f22-b58d-4cb7b1fb2a07.png)

### COMPANION APP MOCKUP
![Mockup APP@2x](https://user-images.githubusercontent.com/67196406/166441584-ea44e07b-5d4e-48e7-9d51-3075f1857a11.png)

### BRIDGE FINITE STATE MACHINE
![Bridge FSM@2x(1)](https://user-images.githubusercontent.com/67196406/166441379-1aae2645-e902-43d0-8fbf-e0be87f9716d.png)

### SENSORS FINITE STATE MACHINE
![Arduino FSM@2x(1)](https://user-images.githubusercontent.com/67196406/166441372-be617bb8-eba4-4ac1-85f0-196dab1dc9c9.png)

### WHAT THIS PROJECT USES
![immagine](https://user-images.githubusercontent.com/67196406/166442157-9cd6fbf3-04e4-4aef-8099-2a57eaa0ec34.png)

## PROJECT PRESENTATION AND EXPLANATION
A full explanation of the project can be found in the 'Project Presentation' folder.
Two set of slides are present:
- one explaining the general parts of SAURUSS
- one focusing more on the 3D and Computer Vision of the drone automous flying and intruder detection
