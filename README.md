# 🚀 CodeAlpha Web Development Internship — Completed Tasks

This repository contains the completed tasks for the **CodeAlpha Web Development Internship**. Both tasks are full-stack, responsive, and functional web applications with real databases, authentication, and automated testing suites.

---

## 📂 Repository Structure

```text
codealpha_tasks/
│
├── 🛍️ Task1_Ecommerce_Store/        --> Task 1: Simple E-commerce Store (NovaCart)
│   ├── ecommerce_project/
│   ├── store/
│   ├── templates/
│   ├── static/
│   ├── manage.py
│   ├── requirements.txt
│   └── README.md
│
├── ⚡ Task2_Social_Media_Platform/   --> Task 2: Social Media Platform (VIBEUP)
│   ├── vibeup_project/
│   ├── core/
│   ├── templates/
│   ├── static/
│   ├── media/
│   ├── manage.py
│   ├── requirements.txt
│   └── README.md
│
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 📌 Summary of Completed Tasks

### ✅ Task 1: Simple E-commerce Store (`NovaCart`)
A full-stack, responsive e-commerce web platform for electronics, streetwear, and lifestyle products.
- **Frontend**: HTML5, CSS3, Vanilla JavaScript (responsive grid, cart modifiers)
- **Backend**: Python & Django (MVT architecture)
- **Database**: SQLite with Django ORM
- **Key Features**:
  - Dynamic product catalog with category filter and search
  - Sorting by price (Low to High, High to Low) and customer rating
  - Product details view with stock validation and quantity picker
  - Shopping cart with real-time session updates and conditional free shipping
  - Checkout flow with shipping address form and payment method selection
  - Order processing with unique order numbers (`NC-XXXXXXXX`), stock decrement, and receipts
  - Customer registration, login, and order history dashboard
  - Automated tests passing (4/4 tests `OK`)
- **How to Run**:
  ```powershell
  cd Task1_Ecommerce_Store
  pip install -r requirements.txt
  python manage.py makemigrations store
  python manage.py migrate
  python manage.py seed_ecommerce
  python manage.py runserver 8001
  ```
  Open: **[http://127.0.0.1:8001](http://127.0.0.1:8001)**  
  Demo Login: `alex_customer` / `password123`

---

### ✅ Task 2: Social Media Platform (`VIBEUP`)
A Gen-Z-coded, community-driven social media application for campus life and creators.
- **Frontend**: HTML5, Modern Tailored CSS (Electric Purple, Acid Lime, Lavender palette), Vanilla JavaScript
- **Backend**: Python & Django
- **Database**: SQLite with Django ORM
- **Key Features**:
  - Real user authentication with hashed passwords and protected routes
  - Custom profiles with campus badges, pronouns, custom vibe tags, and interest pills
  - Clickable follower & following counters with dynamic user modals
  - "What's the vibe?" composer with mood tags, 1,000-char counter, and image uploads
  - Dual-tab home feed (**Following** vs **For You / Global**)
  - Real-time AJAX liking with heart bounce animation
  - Live commenting system with author deletion
  - Explore page with real database search across posts, bios, campuses, and hashtags
  - In-app notification center with live unread badge counters
  - Dark & Light theme switcher with persistence
  - 19 Automated unit & integration tests passing (19/19 `OK`)
- **How to Run**:
  ```powershell
  cd Task2_Social_Media_Platform
  pip install -r requirements.txt
  python manage.py makemigrations core
  python manage.py migrate
  python manage.py seed_data
  python manage.py runserver 8000
  ```
  Open: **[http://127.0.0.1:8000](http://127.0.0.1:8000)**  
  Demo Login: `vibemaster` / `password123` (or click instant demo login buttons)

---

## 🧪 Automated Test Verification

Both tasks include automated test suites:

- **Task 1 Tests**:
  ```powershell
  cd Task1_Ecommerce_Store
  python manage.py test store
  ```
- **Task 2 Tests**:
  ```powershell
  cd Task2_Social_Media_Platform
  python manage.py test core
  ```

---

## 👨‍💻 Intern Details
- **Intern Name**: Abhishek
- **Internship Track**: Web Development
- **Organization**: CodeAlpha
