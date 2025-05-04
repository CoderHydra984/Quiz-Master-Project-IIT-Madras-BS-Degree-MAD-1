# quiz-master-mad-1-project
In this repository, I will be creating a project for the Modern Application Development - 1 course as part of the IIT Madras BS Degree Program.

# Quiz Master 🧠🎓

A **Flask-based Exam Preparation Web App** that allows users to take quizzes, manage student lists, and handle authentication efficiently.


## 📌 Features

- 📝 **User Authentication** (Registration & Login with Flask-Security)
- 🎯 **Multi-User Support** (Admin & Students)
- 📚 **Quiz Management** (Create, Edit, Delete Quizzes)
- 🔍 **Course & Chapter Organization**
- 📊 **Score Tracking & Progress Analysis**

---

## 📂 Folder Structure

```
Quiz_Master/
│── application/           # Core application logic  
│   ├── api.py             # API endpoints  
│   ├── config.py          # App configuration  
│   ├── controllers.py     # Route handlers (Controllers)  
│   ├── database.py        # Database connection setup  
│   ├── functions.py       # Utility functions  
│   ├── models.py          # Database models (Flask-SQLAlchemy)  
│── db_directory/          # Database storage  
│── static/                # Static files (CSS, Images)  
│   ├── admin.css          # Admin panel styles  
│   ├── index.css          # General styles  
│   ├── user.css           # User dashboard styles  
│   ├── logo3.png          # App logo  
│── templates/             # HTML Templates (Jinja2)  
│   ├── index.html         # Homepage template  
│   ├── register.html      # User registration page  
│   ├── ...                # More templates  
│── .gitignore             # Git ignore file  
│── local_run.sh           # Local server startup script  
│── local_setup.sh         # Environment setup script  
│── main.py                # Main Flask application file  
│── README.md              # Project Documentation  
│── requirements.txt       # Dependencies list 
```

---

## 🚀 Installation & Setup  

### 1⃣ Clone the Repository  
```bash
git clone https://github.com/23f3001476/quiz_master_23f3001476.git  
cd quiz_master_23f3001476  
```  

### 2⃣ Run Setup Script  
```bash
bash local_setup.sh  
```  

### 3⃣ Run Initialization Script  
```bash
bash local_run.sh  
```  

Now, visit `http://127.0.0.1:8080/` in your browser. 🎉


---

## 🛠️ Technologies Used

### Backend  
- **Flask** – Web framework for handling routes and logic  
- **Flask-SQLAlchemy** – ORM for database management  
- **Flask-RESTful** – API development framework  
- **bcrypt** – Secure password hashing  

### Frontend  
- **HTML, CSS (Bootstrap)** – Styling and layout  
- **Jinja2** – Templating engine for dynamic content  

### Database  
- **SQLite** (Default) – Lightweight relational database  
- **SQLAlchemy** – ORM for database interactions  

### Additional Tools  
- **Chart Js** – For data visualization    


---

## 👨‍💻 Contributors

- **MAERAJ AKHTAR** ([@CoderHydra984](https://github.com/CoderHydra984))  

---


