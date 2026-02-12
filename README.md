# 🚀 Django + Aiogram Task Manager Bot

This project is a modern Task Management System that integrates a powerful Django backend with a fast, asynchronous Telegram Bot interface using Aiogram.



## ✨ Key Features
* **Django ORM**: Robust data management and storage.
* **Aiogram 3.x**: High-performance asynchronous Telegram interaction.
* **User Isolation**: Personalized task lists (Users only see their own tasks).
* **FSM (Finite State Machine)**: Step-by-step guided task creation flow.
* **Statistics Dashboard**: Real-time reporting of completed and pending tasks.
* **Security Focused**: Sensitive data managed via Environment Variables (.env).

## 🛠 Tech Stack
* **Python 3.13+**
* **Django 5.x**
* **Aiogram 3.x**
* **PostgreSQL** 

## 🚀 Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd task_manager
    ```

2.  **Set up a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables:**
    Create a `.env` file in the root directory and add your credentials:
    ```env
    BOT_TOKEN=your_telegram_bot_token
    DEBUG=True
    SECRET_KEY=your_django_secret_key
    DATABASE_URL=postgres://user:password@localhost:5432/dbname
    ```

5.  **Run Migrations:**
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

6.  **Launch the Bot:**
    ```bash
    python bot.py
    ```

## 📊 Database Schema
The system uses a relational structure where each `Task` is linked to a specific Telegram `user_id`, ensuring data privacy and security.



---
Developed with by Risolat ❤️