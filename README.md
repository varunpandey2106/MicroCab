<h1 align="center">MicroCab</h1>
MicroCab is a an ongoing attempt at a scalable microservice application that showcases a robust implementation of distributed systems and the effective utilization of modern technologies in an event-driven architecture. MicroCab demonstrates key architectural patterns and seamless integration with various tools. I am developing this as a hands-on project to learn about building microservice applications. This project will be seeing varuous future enhancements so stay posted! 

  
## 📋 Overview

1. **👤 User Account Service:** Manages user registration, login, and ensures secure authentication. It functions as the authentication service, validating user credentials, issuing JWT tokens, and maintaining a secure authentication process.


2. **🚗 Driver Service:** Responsible for various driver-related tasks, including driver registration, handling driver responses to ride requests (acceptance and rejection), and retrieving driver information.


3. **🚕 Ride Service:** Responsible for managing all aspects of ride-related operations, including ride requests, ride confirmations, ride cancellations, and retrieval of past ride history.

   
4. **📍 Tracking Service:** The tracking service is essential for efficient rider-driver matching. It employs MongoDB geospatial indexing to locate the nearest available driver. Additionally, the service calculates the driver's estimated time of arrival (ETA)  factoring in the driver's recent location history, distance to the pickup location or rider's destinaion, and the driver average speed. To ensure precision, MicroCab provides the client application an endpoint for frequent driver location updates, typically every 30 seconds(configurable), ensuring real-time positioning and enhancing the rider's experience.

   
5. **💳 Payment Service:** Responsible for making payments.
   
   



## ⚒️ Technology Stack

- **Backend:** The backend of all services is powered by FastAPI, a modern and high-performance web framework for building APIs with Python. FastAPI's asynchronous capabilities complement the microservices architecture, ensuring exceptional performance and scalability.
  
- **Databases:** PostgreSQL is used for services handling structured data, while MongoDB is utilized for the tracking service's location data storage. Redis acts as a cache/temporary data storage, optimizing performance.

- **Message Broker:** RabbitMQ enables efficient asynchronous communication between services, promoting scalability and flexibility.

- **Payments:** Paystack enables very simple payment integration.
  
- **Docker:** Each microservice is containerized using Docker, enabling seamless deployment across various environments.

  



##  Future enhancements

- **Kubernetes** 
- **Notifications&websockets:** 

