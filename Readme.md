# Versity - Volunteer Opportunity Matching Platform

## Overview

Versity is a comprehensive platform designed to connect volunteers with organizations offering volunteer opportunities. The system facilitates the entire volunteering lifecycle — from opportunity discovery and application to hour tracking and verification.

---

## Features

### For Volunteers
- **Profile Management**: Create and maintain a volunteer profile with skills and preferences
- **Opportunity Discovery**: Browse and search for volunteer opportunities
- **Application Management**: Apply for opportunities and track application status
- **Hour Tracking**: Log volunteer hours for completed work
- **Skill Development**: Build a verifiable record of volunteer experience

### For Organizations
- **Profile Management**: Create and maintain an organization profile
- **Opportunity Management**: Create, edit, and manage volunteer opportunities
- **Applicant Review**: Review and respond to volunteer applications
- **Hour Verification**: Verify volunteer hours for completed work
- **Volunteer Management**: Track and manage volunteer engagement

### For Administrators(MAX = 3)
- **User Management**: Oversee all users in the system
- **Content Moderation**: Ensure appropriate content across the platform
- **System Monitoring**: Monitor system health and performance
- **Analytics**: Access platform usage statistics and reports

---

## Technical Architecture

- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT-based authentication
- **Email**: SMTP integration for notifications

---

## API Documentation

### Authentication Routes (`auth_routes.py`)

#### User Registration
```bash
curl -X POST http://localhost:8000/api/auth/register \
-H "Content-Type: application/json" \
-d '{"username": "newuser", "email": "user@example.com", "password": "password123", "role": "volunteer"}'
```
### Admin Registratin 
``` bash
curl -X POST http://localhost:8000/api/auth/register \
-H "Content-Type: application/json" \
-d '{
  "username": "admin_user",
  "email": "admin@example.com",
  "password": "password1234",
  "role": "admin",
  "admin_key": "stored in .env"
}'
```

#### User Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
-d "username=newuser&password=password123" \
-H "Content-Type: application/x-www-form-urlencoded"
```
### Get Current User Profile 
```bash
curl -X GET http://localhost:8000/api/auth/me \
-H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```
### Refresh Token
```bash
curl -X POST http://localhost:8000/api/auth/refresh-token \
-H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```
### Logout 
```bash
curl -X POST http://localhost:8000/api/auth/logout \
-H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```
### Forgot Password
```bash
curl -X POST http://localhost:8000/api/auth/forgot-password \
-H "Content-Type: application/json" \
-d '{"email": "user@example.com"}'
```
### Reset Password
```bash
curl -X POST http://localhost:8000/api/auth/reset-password \
-H "Content-Type: application/json" \
-d '{"token": "RESET_TOKEN", "new_password": "newpassword123"}'
```


### Match Routes (match_routes.py)
### List Matches 
```bash
curl -X GET http://localhost:8000/api/matches \
-H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```
### Create Match (Apply for Oppotunity)
```bash
curl -X POST http://localhost:8000/api/matches \
-H "Content-Type: application/json" \
-H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
-d '{"opportunity_id": 1}'
```
### Update Match Status (Accept/Reject)
``` bash 
curl -X PUT http://localhost:8000/api/matches/1 \
-H "Content-Type: application/json" \
-H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
-d '{"status": "accepted"}'
```


### Opportunity Routes (opportunity_routes.py)

### Get Opportunity
``` bash 
curl -X GET http://localhost:8000/api/opportunities/1
```
### List Opportunities
``` bash 
curl -X GET http://localhost:8000/api/opportunities
``` 
### Create Opportunity
``` bash 
curl -X POST http://localhost:8000/api/opportunities \
-H "Content-Type: application/json" \
-H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
-d '{"title": "New Opportunity", "description": "Description", "skills_required": "Skills", "start_date": "2023-12-01T00:00:00", "end_date": "2023-12-31T00:00:00", "location": "Location"}'
``` 
### Update Opportunity
``` bash 
curl -X PUT http://localhost:8000/api/opportunities/1 \
-H "Content-Type: application/json" \
-H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
-d '{"title": "Updated Title"}'
```


### Organization Routes (organization_routes.py)
### Get Organization Profile
``` bash 
curl -X GET http://localhost:8000/api/organizations/1
```
### Update Organization Profile
``` bash
 curl -X PUT http://localhost:8000/api/organizations/1 \
-H "Content-Type: application/json" \
-H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
-d '{"name": "Updated Name", "description": "Updated Description"}'
```
### Volunteer Routes (volunteer_routes.py)
### Get Volunteer Profile
``` bash 
curl -X GET http://localhost:8000/api/volunteers/1 \
-H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```
### Update Volunteer Profile
``` bash 
curl -X PUT http://localhost:8000/api/volunteers/1 \
-H "Content-Type: application/json" \
-H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
-d '{"skills": "Updated Skills"}'
```
### Get Volunteer Hours
``` bash 
curl -X GET http://localhost:8000/api/volunteers/1/hours \
-H "Authorization: Bearer YOUR_ACCESS_TOKEN"

```

### Hour Tracking Routes (hour_tracking_routes.py)
### Log Hours
``` bash 
curl -X POST http://localhost:8000/api/hours \
-H "Content-Type: application/json" \
-H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
-d '{"opportunity_id": 1, "hours": 5, "date": "2023-12-01"}'
```
### Verify Hours
``` bash 
curl -X PUT http://localhost:8000/api/hours/1/verify \
-H "Content-Type: application/json" \
-H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
-d '{"status": "approved"}'
``` 
### Health Routes(health_route.py)
### Database Health Check 
``` bash 
curl -x GET http://localhost:8000/api/health/db
```

### Admin Routes(admin_routes.py)
These routes would typically be accessible only to admin user and might include:
* User management 
* System configuration
* Analytic and reporting

## Getting Started

### Prerequisites
- Python 3.8+  
- PostgreSQL  
- SMTP server for email functionality  

### Installation

**Clone the repository**
```bash
git clone https://github.com/yourusername/versity.git
cd versity
```
### Create and activate a virtual environment
``` bash 
python -m venv venv
source venv/bin/activate 
```
### Install dependencies
``` bash
pip install -r requirements.txt
```
### Set up environment variables
``` bash 
cp .env.example .env
```
### Run database migrations
``` bash 
alembic revision --autogenerate -m "Add bidirectional relationship between User and Admin"
&&&
alembic upgrade head
```
### Start the development server
``` bash
 uvicorn app.main:app --reload

 ```
 The API will be available at: http://localhost:8000

### Database Schema
 Core models include:
 
 * User: Stores user authentication and profile data
 
 * Organization: Contains organization profile information
 
 * Opportunity: Represents volunteer opportunities
 
 * Match: Tracks applications/matches between volunteers and opportunities
 
 * VolunteerHour: Records hours logged by volunteers
 
 ### Environment Variables
 * DATABASE_URL: PostgreSQL database connection string
 * SECRET_KEY: Secret key for JWT tokens
 * EMAIL_HOST:
 * EMAIL_PORT: SMTP server port
 * EMAIL_HOST_USER: SMTP server username
 * EMAIL_HOST_PASSWORD: SMTP server password
 * EMAIL_USE_TLS: SMTP server TLS setting
 * EMAIL_USE_SSL: SMTP server SSL setting
 * EMAIL_FROM: Email address used for sending emails
 * ADMIN_REGISTRATION_KEY : Key for admin registration


 Run the cnmd below to generate a secure random string 
 ``` bash 
 openssl rand -hex 32
```



## Quick Start
Tailwind lets you style elements directly in your HTML/JSX using utility classes. Think of it like LEGO blocks for styling!

## Basic Examples

### Colors
```html
<div class="text-blue-500">Blue text</div>
<div class="bg-red-200">Red background</div>

```
### Spacing
- Margin: m-4 (1rem all around)
- Padding: p-8 (2rem all around)
- Specific sides: mt-2 (margin-top), pb-4 (padding-bottom)

### Layout
```html
<!-- Flex container -->
<div class="flex justify-center items-center">
  <div>Centered content</div>
</div>

<!-- Grid -->
<div class="grid grid-cols-3 gap-4">
  <div>Column 1</div>
  <div>Column 2</div>
  <div>Column 3</div>
</div>
```

### Typography

<h1 class="text-4xl font-bold">Large Title</h1>
<p class="text-lg text-gray-600">Normal paragraph</p>


### responsive design
<div class="hidden md:block">This content is hidden on small screens.</div>

- sm: Small screens (640px)
- md: Medium screens (768px)
- lg: Large screens (1024px)

:Example 
```html
<div class="text-sm md:text-lg lg:text-xl">
  Gets bigger on larger screens
</div>

```
### Cards
```html
<div class="bg-white shadow-lg rounded-lg p-6">
  <h2 class="text-xl font-bold mb-2">Card Title</h2>
  <p class="text-gray-600">Card content</p>
</div>
```

### Buttons
```html
<button class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
  Click me
</button>
```
### Forms
```html
<input type="text" class="border border-gray-300 rounded px-2 py-1">
<textarea class="border border-gray-300 rounded px-2 py-1"></textarea>
```

### Tips & Tricks for styling with tailwind 

1. Stack classes from left to right: layout → spacing → colors → effects
1. Use className="" in React/Next.js instead of class=""
1. Hover effects use hover: prefix
1. Dark mode with dark: prefix
1. Use responsive classes like md: or lg: for responsive design
1. Use utility classes like text-center or text-right for layout
1. Use utility classes like bg-gray-200 or bg-blue-500 for colors 


### Resources 

1. Tailwind CSS Docs: https://tailwindcss.com/docs
1. Tailwind UI: https://tailwindui.com/
1. Tailwind cheat sheet : https://nerdcave.com/tailwind-cheat-sheet
