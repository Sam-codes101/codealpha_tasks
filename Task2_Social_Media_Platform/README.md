# ✨ VIBEUP — Your People. Your Chaos. Your Corner of the Internet.

> **A Gen-Z-coded, community-driven social media application built with Django, Vanilla JavaScript, and Custom Modern CSS.**

---

## ⚡ 1. Overview & Brand Identity

**VIBEUP** is the anti-corporate social platform engineered for campus students, young creators, late-night coders, and hyperfixation connoisseurs. It rejects the sanitized, sterile aesthetics of corporate dashboards and ad-bloated feeds in favor of an authentic, chaotic, expressive digital hangout.

### 🎨 Visual Direction & Palette
- **Electric Purple** (`#7C3AED` / `#8B5CF6`): Core brand glow and accents.
- **Acid Lime** (`#D4FF32` / `#CCFF00`): High-energy Gen-Z highlight and primary buttons.
- **Lavender & Soft Lilac** (`#E8DEF8` / `#A78BFA`): Subtle borders, badges, and secondary typography.
- **Near-Black Midnight** (`#0C0B12` / `#14121E`): Deep dark-mode canvas.
- **Warm Off-White** (`#F7F5FA` / `#FFFFFF`): Clean, accessible light mode.
- **Micro-Interactions**: Heart bounce on like, smooth sliding toasts, live character counters, dynamic image preview, and reduced-motion accessibility.
- **Dark & Light Modes**: 100% theme switch support, persistent across sessions and synced to user profile.

---

## 🛠️ 2. Tech Stack

- **Backend Framework**: Python & Django 6.1 (Clean MVT Architecture)
- **Database**: SQLite with Django ORM
- **Authentication**: Django's built-in session authentication (`User`, `Profile` with signals)
- **Frontend**: HTML5, Vanilla JavaScript (Fetch API for AJAX operations, no external framework dependencies)
- **Styling**: Tailored Custom CSS with CSS Custom Properties (Variables), Flexbox, CSS Grid, and responsive viewports for Mobile, Tablet, and Desktop.

---

## 🚀 3. Quick Start & Setup Guide

### Step 1: Clone or navigate to the repository
```bash
cd "INTERNSHIP TASK"
```

### Step 2: Install dependencies
Ensure Python 3.10+ is installed:
```bash
pip install -r requirements.txt
```

### Step 3: Run Database Migrations
```bash
python manage.py makemigrations core
python manage.py migrate
```

### Step 4: Populate Seed Data (Recommended!)
We provide a rich seed command that instantly injects realistic Gen-Z campus creators, posts with mood badges, hashtags, comments, likes, and follows:
```bash
python manage.py seed_data
```

### Step 5: Start the Local Development Server
```bash
python manage.py runserver
```
Open **[http://127.0.0.1:8000](http://127.0.0.1:8000)** in your browser!

---

## 👥 4. Seeded Demo Accounts

All seeded demo accounts share the password: `password123`

| Username | Name / Persona | Campus / Vibe |
|---|---|---|
| **`vibemaster`** *(Superuser)* | Vibe Master ✨ | Metaverse University '26 / Community Legend |
| **`maya_codes`** | Maya Lin 🍵 | UCLA CS '26 / Matcha Fiend |
| **`kai_visuals`** | Kai Vance 🎞️ | Parsons Design '25 / Aesthetic Curator |
| **`zara_beats`** | Zara Chen 🎧 | NYU Music Tech '26 / Sound Alchemist |
| **`leo_unhinged`** | Leo Rivera 💀 | UT Austin '27 / Unhinged Realist |
| **`chloe_core`** | Chloe Kim 📖 | Columbia '25 / Café Philosopher |
| **`dev_noah`** | Noah Patel 🚀 | Georgia Tech '26 / Hackathon Goblin |

> *Tip: On the Login screen, click any of the instant demo buttons to auto-populate credentials!*

---

## 🌟 5. Key Features & Pages

### 1. Landing Page (`/`)
- Expressive hero header with Gen-Z typography and highlights.
- Real-time community stats (Vibes dropped, campus creators, real moments).
- Dynamic trending hashtags cloud calculated directly from database posts.
- Feature breakdown and timeline sample previews for guests.

### 2. Authentication (`/signup/`, `/login/`, `/logout/`)
- User registration with validation for handle formatting, uniqueness, and password confirmation.
- Secure Django password hashing (no plain text passwords).
- Quick demo login pills on the login screen.
- Safe redirects to intended pages (`next=` parameter support).

### 3. Home Feed (`/feed/`)
- **Feed Toggle**: Switch between **"Following"** (curated posts from people you follow) and **"For You (All Campus)"** (global chronological timeline).
- **"What's the vibe?" Composer**:
  - Live 1,000-character counter.
  - Dropdown for Gen-Z mood tags (*🎧 In My Zone*, *☕ Campus Grind*, *💀 Brain Rot*, *✨ Feeling Iconic*, etc.).
  - Photo attachment with real-time thumbnail preview and remove button.
- Responsive right rail with **Trending on Campus** hashtags and **People You Might Vibe With** recommendations.
- Playful empty states with Gen-Z microcopy (*"It's giving quiet timeline. Drop the first post."*).

### 4. Post Detail & Comments (`/post/<id>/`)
- Individual post view with full content, mood tag, and image.
- Real-time commenting system via AJAX (injects thoughts immediately without page reload).
- Comment author deletion with live DOM fade-out and counter update.
- Empty comments state (*"No thoughts dropped yet. Be the first to chime in! 💬"*).

### 5. Like & Follow Systems
- **Like/Unlike**: Heart icon with bounce animation, updates counter instantly via JSON endpoint (`POST /post/<id>/like/`).
- **Follow/Unfollow**: Follow buttons update in real-time, update follower count, and prevent self-following.
- Clickable follower/following counters on profiles trigger a dynamic modal displaying the users.

### 6. Explore Page (`/explore/`)
- **Live Search**: Database-backed query filtering across post content, usernames, display names, bios, campuses, and interests.
- **Mood Chips Filter**: Filter the timeline by emotional mood (*🎧 In My Zone*, *💀 Brain Rot*, etc.).
- **Matching Creators Grid**: Highlights user profile cards matching search queries.
- **Trending Hashtags**: Real-time aggregation of hashtags from recent posts.

### 7. User Profile (`/profile/<username>/`)
- Custom gradient banner and avatar.
- Display name, pronouns, campus badge, vibe tag, join date, and personal link.
- Interests & hyperfixations pills (clickable to explore matching content).
- Profile tabs: **Posts**, **Photos & Media**, and **Liked Vibes**.
- Direct follow/unfollow button for other creators, or "Edit Vibe" for profile owner.

### 8. Notifications (`/notifications/`)
- In-app notification center tracking likes, comments, and new followers.
- Unread badge counter in desktop sidebar and mobile navigation.
- Unread highlighting with one-click **"Mark all as read"**.

### 9. Settings (`/settings/`)
- Full profile editor: update display name, avatar, bio, pronouns, campus, custom vibe tag, interests, and portfolio link.
- Email preferences and default theme selector (Dark / Light).

---

## 🧪 6. Testing & Quality Assurance

A comprehensive automated test suite covers all critical paths:
```bash
python manage.py test core
```
**Test Coverage Includes:**
- User registration, login, logout, and password mismatch rejection.
- Automatic Profile creation via signals and profile updating.
- Post creation, empty post validation, and author-only edit/delete protection.
- Like toggle, unlike toggle, like counter accuracy, and duplicate prevention.
- Comment creation, deletion by author, and validation.
- Follow and unfollow relationships, self-follow prevention, and follower count tracking.
- Home feed following-filter vs global feed.
- Explore database search across posts and users.
- In-app notification generation and mark-as-read workflows.

---

## 🔒 7. Security Highlights

- **CSRF Protection**: All POST/DELETE requests (standard and AJAX) pass Django's CSRF token check.
- **Safe Escaping**: User-generated content is escaped to prevent XSS.
- **File Validation**: Image uploads are validated on the server for allowed MIME types (JPEG, PNG, GIF, WEBP) and maximum file size (5MB for posts, 3MB for avatars).
- **Authorization Verification**: Editing and deleting posts or comments strictly verify that `request.user == object.author`.
- **Environment Support**: Secret keys and debug toggles read from environment variables when configured.

---

## 📱 8. Responsive Design

- **Desktop (1080px+)**: Left sidebar + center feed + right contextual widget rail.
- **Tablet (768px - 1080px)**: Collapsed right rail with full center feed and sticky sidebar.
- **Mobile (< 768px)**: Clean top bar + full-width mobile cards + sticky bottom navigation bar with quick post button.
