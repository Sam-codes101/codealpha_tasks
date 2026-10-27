# 🛍️ Task 1: NovaCart — Simple E-commerce Store

> **Built for CodeAlpha Web Development Internship — Task 1**

---

## ⚡ Overview
**NovaCart** is a clean, modern, and responsive e-commerce web application with product listings, dynamic category filters, search, a session-based shopping cart, order checkout processing, and customer accounts.

---

## 🛠️ Tech Stack
- **Frontend**: HTML5, CSS3, Vanilla JavaScript (Responsive grid, cart modifiers)
- **Backend**: Python & Django (MVT Architecture)
- **Database**: SQLite with Django ORM
- **Authentication**: Django's built-in session authentication

---

## ✨ Features Implemented
- **Product Catalog**: Grid layout with high-res product photos, discount badges, ratings, and instant "Add to Cart" actions.
- **Filters & Sorting**: Filter by category (Electronics, Footwear, Computers, Apparel, Bags), search by keyword, and sort by price or rating.
- **Product Details Page**: Quantity selector, stock status, specs, customer reviews count, and related products carousel.
- **Shopping Cart**: Real-time quantity increment/decrement, item removal, dynamic subtotal calculation, and conditional free delivery on orders above ₹1,000.
- **Order Processing & Checkout**: Full shipping address form, payment method selector (Cards, UPI, COD), stock deduction on order placement, and order confirmation receipt (`NC-XXXXXXXX`).
- **Customer Accounts**: Registration, login, logout, and order history dashboard (`/orders/`).

---

## 🚀 How to Run

```powershell
cd Task1_Ecommerce_Store

# 1. Install dependencies
pip install -r requirements.txt

# 2. Run migrations
python manage.py makemigrations store
python manage.py migrate

# 3. Seed demo products & categories
python manage.py seed_ecommerce

# 4. Start local development server
python manage.py runserver 8001
```

Visit: **[http://127.0.0.1:8001](http://127.0.0.1:8001)**

### Demo Customer Credentials:
- **Username**: `alex_customer`
- **Password**: `password123`
*(Admin: `admin` / `admin123`)*

---

## 🧪 Testing
```powershell
python manage.py test store
```
All 4 test suites pass with 100% success.
