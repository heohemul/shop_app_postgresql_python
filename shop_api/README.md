# 🛒 Electronics Shop — REST API

A production-ready **FastAPI + PostgreSQL** backend for an electronics e-commerce platform. Features JWT authentication, product catalog with filters, shopping cart, orders, reviews, coupons, and full admin management.

---

## 🚀 Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI 0.111 |
| Database | PostgreSQL + SQLAlchemy 2.0 |
| Auth | JWT (python-jose) + bcrypt (passlib) |
| Validation | Pydantic v2 |
| Migrations | Alembic |
| Server | Uvicorn |

---

## 📁 Project Structure

```
shop_api/
├── main.py                  # FastAPI entry point
├── requirements.txt
├── .env.example
└── app/
    ├── config.py            # Settings (.env)
    ├── database.py          # SQLAlchemy engine + session
    ├── models.py            # ORM models (all tables)
    ├── schemas.py           # Pydantic schemas (request/response)
    ├── auth.py              # JWT + bcrypt + Depends
    └── routers/
        ├── products.py      # GET/POST/PATCH/DELETE /api/products
        ├── categories.py    # /api/categories
        ├── brands.py        # /api/brands
        ├── users.py         # /api/users (register, login, me)
        ├── orders.py        # /api/orders
        ├── reviews.py       # /api/reviews
        ├── cart.py          # /api/cart
        └── coupons.py       # /api/coupons
```

---

## ⚡ Quick Start

### 1. Clone & set up environment

```bash
cd shop_api
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure database

```bash
# Create PostgreSQL database
createdb shop_db

# Copy and edit .env
cp .env.example .env
```

**.env.example:**
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/shop_db
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

### 3. Initialize tables

```bash
# Option A — via Python (quick for development)
python -c "from app.database import engine; from app import models; models.Base.metadata.create_all(engine)"

# Option B — load seed SQL manually
psql -d shop_db -f seed.sql
```

### 4. Run the server

```bash
uvicorn main:app --reload
```

| Interface | URL |
|---|---|
| API Base | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |

---

## 📡 API Endpoints

### 🔓 Public

| Method | URL | Description |
|---|---|---|
| GET | `/api/products` | Product catalog with filters |
| GET | `/api/products/featured` | Featured products |
| GET | `/api/products/{slug}` | Product details |
| GET | `/api/categories` | Category tree |
| GET | `/api/brands` | Brand list |
| POST | `/api/users/register` | User registration |
| POST | `/api/users/login` | Login (returns JWT) |

### 🔐 Authenticated (Bearer token required)

| Method | URL | Description |
|---|---|---|
| GET | `/api/users/me` | My profile |
| PATCH | `/api/users/me` | Update profile |
| GET / POST | `/api/users/me/addresses` | My addresses |
| DELETE | `/api/users/me/addresses/{id}` | Delete address |
| GET / POST | `/api/cart` | View / add to cart |
| PATCH | `/api/cart/items/{id}` | Update cart item quantity |
| DELETE | `/api/cart/items/{id}` | Remove cart item |
| DELETE | `/api/cart` | Clear cart |
| GET / POST | `/api/orders` | My orders / create order |
| GET | `/api/orders/{id}` | Order details |
| PATCH | `/api/orders/{id}/cancel` | Cancel order |
| GET | `/api/reviews/product/{id}` | Product reviews |
| POST | `/api/reviews/product/{id}` | Leave a review |
| DELETE | `/api/reviews/{id}` | Delete review |
| GET | `/api/coupons/validate/{code}` | Validate coupon |

### 🛡️ Admin / Moderator only

| Method | URL | Description |
|---|---|---|
| POST / PATCH / DELETE | `/api/products` | Manage products |
| POST | `/api/categories` | Create category |
| POST | `/api/brands` | Create brand |
| PATCH | `/api/orders/{id}/status` | Update order status |
| GET / POST | `/api/coupons` | Manage coupons |
| DELETE | `/api/coupons/{id}` | Deactivate coupon |

---

## 🔍 Product Filters

```
GET /api/products?page=1&per_page=20&category_id=2&brand_id=1&min_price=1000&max_price=50000&featured=true&search=iPhone
```

| Parameter | Type | Description |
|---|---|---|
| `page` | int | Page number (default: 1) |
| `per_page` | int | Items per page (max: 100) |
| `category_id` | int | Filter by category |
| `brand_id` | int | Filter by brand |
| `min_price` | float | Minimum price |
| `max_price` | float | Maximum price |
| `featured` | bool | Featured products only |
| `search` | string | Search by name |

---

## 🔑 Authentication

### Register

```bash
curl -X POST http://localhost:8000/api/users/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","username":"johndoe","password":"secret123"}'
```

### Login

```bash
curl -X POST http://localhost:8000/api/users/login \
  -H "Content-Type: application/json" \
  -d '{"username":"johndoe","password":"secret123"}'
```

### Use token

```bash
curl http://localhost:8000/api/users/me \
  -H "Authorization: Bearer <YOUR_TOKEN>"
```

---

## 🧩 Key Features

- **JWT Authentication** — secure token-based auth with role system (`customer`, `moderator`, `admin`)
- **Product Catalog** — full filtering, pagination, featured products, soft delete
- **Shopping Cart** — per-user cart with quantity management
- **Orders** — full order lifecycle with stock management and coupon support
- **Reviews** — one review per user per product, verified purchase badge, helpful votes
- **Coupons** — percentage or fixed discounts, minimum order amount, usage limits
- **Addresses** — multiple delivery addresses per user with default selection
- **Free Shipping** — automatically applied on orders over 2000

---

## 🗃️ Database Models

| Model | Description |
|---|---|
| `User` | Customer / admin accounts with UUID primary key |
| `Product` | Items with specs (JSONB), images, tags, rating |
| `Category` | Self-referencing tree structure |
| `Brand` | Product brands |
| `Order` | Orders with items, coupon, address |
| `Cart` | Per-user shopping cart |
| `Review` | Product reviews with verified purchase flag |
| `Coupon` | Discount codes (% or fixed) |
| `Address` | User delivery addresses |

---

## 📄 License

MIT — free to use and modify.
