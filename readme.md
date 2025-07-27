# Galmart Product Reservation Service

A scalable Django backend service for managing product booking with support for scheduled task execution using Celery[Redis].

---

## 🧱 Features

- Product CRUD
- Booking products with automatic expiration using Celery
- RESTful APIs
- PostgreSQL database
- Integrated testing

---

## 🚀 Tech Stack

- Python 3.11.13
- Django 5.2.4
- Django REST Framework 3.16.0
- Celery 5.5.3
- Redis 7 (as Celery broker)
- PostgreSQL 15
- Docker 27.2.0
- Pytest 8.4.1

---

## 📦 Project Structure

```
.
├── bookings/            # Bookings app
├── products/            # Products app
├── galmart_task/        # Settings and shared utils
├── tests/               # Pytest test suite
├── .env                 
├── .gitignore                 
├── docker-compose.yml
├── Dockerfile
├── manage.py
├── pytest.ini
├── README.md
├── requirements.txt
└── wait_for_db.sh       # Script that delays Django app to build (waits for a database to init)
```

---

## ⚙️ Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/4libion/product_booking.git
cd product_booking
```

### 2. Configure environment

Create `.env` file from `.env.example` or define variables in `docker-compose.yml`:

```env
DEBUG=1
SECRET_KEY=your-secret-key

POSTGRES_DB=db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

### 3. Build and run Docker containers

```bash
docker compose up --build
```

This starts:
- Django app at `http://localhost:8000`
- PostgreSQL DB at `localhost:5432`
- Redis broker at `localhost:6379`
- Celery worker

---

## 🎯 Running Tests

Make sure containers are up, then run:

```bash
docker compose exec web pytest
```

To run a specific test:

```bash
docker compose exec web pytest tests/test_booking.py::test_create_booking
```

---

## 🔀 Celery Task for Booking Expiration

Bookings in `PENDING` status will expire after a delay via a Celery ETA task:

```python
from booking.tasks import clean_expired_booking
from datetime import timedelta
from django.utils import timezone

eta = timezone.now() + timedelta(seconds=60)
clean_expired_booking.apply_async(args=[booking_id], eta=eta)
```

If the task is triggered, it will:
- Mark booking as `EXPIRED`
- Set expired_at field to current time
- Restore quantity to the related product

---

## 🔪 Example Integration Test

```python
@pytest.mark.django_db
def test_product_quantity_after_booking(
    client,
    create_product,
    create_booking,
):
    product = create_product()
    create_booking(product=product, quantity=5)
    product.refresh_from_db()
    assert product.quantity == 95
```

---

## 📢 API Endpoints

Use Swagger to explore APIs at `http://localhost:8000/api/docs/swagger`

---

## 📜 License

MIT License

