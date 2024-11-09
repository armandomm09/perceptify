# Fall and Emotion Detection System for Elderly Care

### Project Overview
This project addresses the need for personalized attention and safety monitoring in elderly care facilities. Leveraging IoT devices, computer vision, and AI, our system aims to reduce risks associated with mental health issues and physical accidents, such as falls, by providing real-time alerts for caregivers. This allows for early intervention, reducing the reliance on in-person monitoring.

### Problem Statement
According to the World Health Organization (WHO), by 2050, one in six people globally will be over 65. In Mexico, the population over 60 is expected to double by 2030, emphasizing the need for improved elder care. With only one caregiver for every ten elderly individuals, there is a risk of undetected mental health issues, such as depression or anxiety, and physical accidents. This project seeks to address these issues through automated detection and alert systems.

### Project Objectives
Our system is designed to:
- **Detect Falls:** Using data from accelerometers and gyroscopes on an ESP32 module, combined with computer vision on a cloud server, the system detects falls in real-time. 
- **Monitor Emotional Health:** Employing YOLO (You Only Look Once) for emotion detection, the system captures facial expressions to identify signs of mental distress, such as anxiety or depression.
- **Real-Time Monitoring and Alerts:** WebSockets enable the ESP32 to stream live video feeds to a server for processing and display, ensuring caregivers can monitor the elderly in real-time.

---

### System Components

1. **Hardware**:  
   - **ESP32 Microcontroller**: Captures sensor data and transmits video frames for processing.
   - **MPU6050 Accelerometer and Gyroscope**: Tracks movements to detect falls.
   - **Camera**: Provides real-time facial data for emotion detection.

2. **Software and Communication**:  
   - **MQTT Protocol**: Ensures secure and efficient data transfer for sensor data.
   - **WebSockets**: Allows real-time video feed transmission from the ESP32, enabling immediate processing and display on the caregiver’s dashboard.
   - **Ubuntu Server**: Hosts the AI models, processes data, and provides real-time visualization.
   - **Computer Vision with YOLO**: Detects falls and evaluates facial expressions to monitor emotional states.

---

### Solution Architecture
Our modular IoT architecture divides the system into three main components:
- **Sensing**: Collects data on body movements and facial expressions.
- **Communication**: Transfers data securely using MQTT for sensor data and WebSockets for real-time video feed.
- **Processing**: Analyzes data on the server, triggering alerts when necessary and displaying results in real-time on a dashboard.

---

### Image Showcase: System in Action

Below are images demonstrating our system’s current progress in detecting falls, monitoring emotional states, and analyzing sensor data.

#### 1. Fall Detection via Computer Vision
   <img width="594" alt="Screenshot 2024-11-08 at 8 47 59 p m" src="https://github.com/user-attachments/assets/76b9b66c-8e2b-4763-9b25-a9688748d490">

   *Image 1: An example of the fall detection system accurately identifying a simulated fall.*

#### 2. Emotion Recognition with YOLO
   <img width="927" alt="Screenshot 2024-11-08 at 8 50 33 p m" src="https://github.com/user-attachments/assets/f05458d6-f5a0-4d6a-a580-fba913f97045">

   *Image 2: The YOLO-based emotion recognition system analyzing facial expressions to detect emotional states.*

#### 3. Sensor Data Analysis (MPU6050)
   <img width="498" alt="Screenshot 2024-11-08 at 8 51 48 p m" src="https://github.com/user-attachments/assets/75fd8edc-82ab-4f44-b54c-ef7ee5de131c">

   *Image 3: Visualization of sensor data from MPU6050 accelerometer and gyroscope.*

---

### Expected Impact
This system aims to enhance the quality of life for elderly individuals in care facilities by offering proactive monitoring and reducing risks associated with both physical and emotional health. Real-time data and video feeds empower caregivers with timely insights, enabling effective resource allocation and rapid intervention.
