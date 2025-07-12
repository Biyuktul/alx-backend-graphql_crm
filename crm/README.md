# CRM Project Setup & Usage Guide

This document provides step-by-step instructions to get your CRM backend up and running, including Redis installation, Django migrations, Celery setup, and log verification.

---

## 1. Install Redis and Dependencies

### Install Redis

- **Ubuntu/Debian:**

```bash
sudo apt update
sudo apt install redis-server
sudo systemctl enable redis-server.service
sudo systemctl start redis-server.service
````

* **MacOS (with Homebrew):**

```bash
brew update
brew install redis
brew services start redis
```

* **Verify Redis is running:**

```bash
redis-cli ping
# Expected output: PONG
```

### Install Python Dependencies

Make sure you have a virtual environment activated, then:

```bash
pip install -r requirements.txt
```

Your `requirements.txt` should include at least:

* `django`
* `celery`
* `redis`
* `gql`
* any other project-specific packages

---

## 2. Database Setup

Run Django migrations to set up your database schema:

```bash
python manage.py migrate
```

---

## 3. Start Celery Worker

Start the Celery worker process to handle background tasks:

```bash
celery -A crm worker -l info
```

---

## 4. Start Celery Beat Scheduler

Start the Celery Beat scheduler to trigger periodic tasks like report generation:

```bash
celery -A crm beat -l info
```

---

## 5. Verify Logs

Your CRM report task logs are saved in:

```
crm/tmp/crm_report_log.txt
```

Check the logs by running:

```bash
cat crm/tmp/crm_report_log.txt
```

Example log entry:

```
2025-07-12 05:49:15,343 - Report: 355 customers, 151 orders, 157,106.78 revenue
```

---

## Additional Notes

* Always ensure Redis is running **before** starting Celery worker or beat.
* Restart Celery processes after modifying task or logging code.
* The log directory (`crm/tmp`) and file are created automatically if they don’t exist.
* Adjust commands and paths as needed to fit your environment setup.

---

Happy coding and smooth task automation! 🚀

```
