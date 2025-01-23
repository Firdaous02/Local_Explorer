
# Local Explorer

**Local Explorer** is a web application that helps users discover the perfect activity for every moment. 
Whether you're looking for nearby places, outdoor adventures, or relaxing indoor activities, 
this platform delivers personalized recommendations tailored to your preferences.

---

## Table of Contents
1. About the Project  
2. Features  
3. Tech Stack
4. Prerequisites
5. Installation  
6. Usage  
7. Screenshots  
8. Future Enhancements  

---

## About the Project

Local Explorer is designed to simplify activity discovery and enhance your leisure time. 
With location and weather-based suggestions and a user-friendly design, the platform helps users find places and activities effortlessly.

### Key Objectives
- Provide **personalized activity and place recommendations** based on user preferences and weather.
- Facilitate **location-based discovery** with an interactive map.
- Deliver an engaging and intuitive user experience.

---

## Features
- **Personalized Recommendations**: Receive tailored activity suggestions based on your input.
- **Location-Based Discovery**: Explore activities and events near your location using a dynamic map.
- **Responsive Design**: Access the platform on any device with a clean, modern interface.
- **User Authentication**:  
  - Secure **registration** and **login** for personalized user experiences.
  - **Session management** to ensure secure and seamless browsing.
  - **Logout functionality** to protect user data after their session ends.

---

## Tech Stack
- **Backend**: Python (Flask framework)  
- **Frontend**: HTML5, CSS3, JavaScript  
- **Mapping Library**: [Leaflet.js](https://leafletjs.com/)
- **APIs**: OpenCage, OpenweatherMap, gpt-4o-mini
- **Deployment**: Local environment (Flask development server)

---
## Prerequisites

Before getting started, make sure you have the following installed:

- **Python 3.x**: [Download Python](https://www.python.org/downloads/)
- **MySQL Server**: [Download MySQL](https://dev.mysql.com/downloads/mysql/)
- **Git**: [Download Git](https://git-scm.com/downloads)

---
## Installation

Follow these steps to set up the project locally:

1. Clone the repository:
   ```bash
   git clone https://github.com/Firdaous02/Local_Explorer.git
   cd local-explorer
   ```

2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   python app.py
   ```

7. Open your browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```

---

## Usage

- **Login**: Log in with your username and password or register, to access location-based activity suggestions.
- **Swipe based**: swipe through the suggestions and personalize your experience.  
- **Interactive Map**: Discover nearby places and activities visually using the map interface.  
- **Logout**: Use the logout button to securely end your session.

---

## Screenshots

### Landing Page
_A visually appealing landing page with a background image and a bold call-to-action._

![Landing Page](https://github.com/user-attachments/assets/29554fc1-256b-4eb1-bd2e-475b57c1974f)

### Features Section
_A layout showcasing the platform's core features with images, titles, and descriptions._

![Features Page](https://github.com/user-attachments/assets/70df8c7d-2f9b-4866-a0d6-ae460c57da90)

![activities](https://github.com/user-attachments/assets/f414fbbd-a5b1-4b7e-8c90-51e00ed7d424)

### Login or Register
_The users can log in if they already have an account, and if they don't, they are required to register._

![login](https://github.com/user-attachments/assets/ea235deb-b9a3-4780-a664-e7d2b93a4294)

![Register](https://github.com/user-attachments/assets/fafffb36-3167-469a-9d04-8fe349e91dee)

### Suggestions Page
_A dynamic page where the user can swipe through the suggestions for places and activities, and express their preferences smoothly._

![loading](https://github.com/user-attachments/assets/5786908e-8726-4f2f-8062-9359f89c97b0)

![suggestion](https://github.com/user-attachments/assets/afed9252-d6c0-4ef6-ae01-c6a29aa51db4)

![again](https://github.com/user-attachments/assets/852bd941-7411-490e-a0b2-c1651129f05b)

---

## Future Enhancements

- Add **OAuth integration** for login using social accounts (e.g., Google, Facebook).  
- Implement **multi-factor authentication (MFA)** for added security.  
- Provide **password reset functionality** via email.  
- Add **advanced filters** for activity suggestions.  
- Deploy the application online using platforms like Heroku or AWS.


