# Distributed IOT Based App Development Platform


## Overview of platform

### Platform Summary
1. Distributed IOT platform is a Platform as a Service(PaaS) project which allows developers to deploy, scale, monitor and execute their IOT based applications.
2. In our project IOT devices can be integrated and used for deployment of IOT based applications.
3. Developer's app can be deployed on multiple containers based on scalability requirements of the developer, our platform also supports load balancing across multiple VM instances.
4. In our IoT platform, we offer comprehensive support for monitoring and fault tolerance. This means that if any instance of a subsystem goes offline, the system promptly orchestrates the deployment of a new instance for that subsystem, ensuring uninterrupted operation.


### Actors of platform
1. App Developer
2. Platform Admin
3. Platform Developer

### How app developer will interact with platform 
1. App developer needs to register on the platform first.
2. Developer will download the contracts developer need to follow and formats in which they need to 
   upload the code base through platform UI.
3. Developer will upload the code base on the platform website.
4. Now, developer will go to the deaployment process page and schedule the  deployment time of the
   application.
5. After deployment gets completed developer recieves the link to access the application.

## Detailed information about the platform

### Tech Stack 
1. Python
2. Apache-kafka
3. Docker

### Database
1. Mongodb
2. Blob-storage
3. Azure Container Registry

### Subsystems of the platform
1. Bootstrapper
2. Application Controller (Scheduler + Validator Workflow)
3. Deployer
4. Node Manager + Load Balancer
5. Sensor Manager
6. Monitoring And Fault Tolerance
7. Logger
8. Platform UI

### Other modules
1. API Gateway
2. LDAP Authentication Server 
3. Logger UI

### Platform Architecture

![Platform Architecture](https://github.com/js141199/IOT-Platform/blob/main/Diagrams/Platform-Architecture.png)  

### Other Diagrams
1. [Communication Model]
2. [Application Model]
3. [Packaging Model]
4. [Bootstrapper]
5. [Application-Controller]
6. [Deployer]
7. [Sensor-Manager]
8. [Node-Manager]
9. [Monitoring And Fault Tolerance]

[Communication Model]: https://github.com/js141199/IOT-Platform/blob/main/Diagrams/Communication-Model.pdf
[Application Model]: https://github.com/js141199/IOT-Platform/blob/main/Diagrams/Application-Model.pdf
[Packaging Model]: https://github.com/js141199/IOT-Platform/blob/main/Diagrams/Packaging-Model.pdf
[Bootstrapper]: https://github.com/js141199/IOT-Platform/blob/main/Bootstrapper/Bootstrapper.drawio.png
[Application-Controller]: https://github.com/js141199/IOT-Platform/blob/main/Diagrams/Application-Controller.pdf
[Deployer]: https://github.com/js141199/IOT-Platform/blob/main/platform--deployer/Deployer_Sub_System.drawio.png
[Sensor-Manager]: https://github.com/js141199/IOT-Platform/blob/main/Diagrams/Sensor-Manager.pdf
[Node-Manager]: https://github.com/js141199/IOT-Platform/blob/main/Diagrams/Node-Manager.pdf
[Monitoring And Fault Tolerance]: https://github.com/js141199/IOT-Platform/blob/main/Diagrams/Monitoring%20And%20Fault-Tolerance.pdf
