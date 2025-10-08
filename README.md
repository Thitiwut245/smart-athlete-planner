# Smart Athlete Planner for Boxing

**Smart Athlete Planner** is a web-based fitness tracking and planning platform designed for boxers.  
It allows athletes to log training sessions, get exercise recommendations from APIs, and view motivational quotes —  
all through a clean, sporty dashboard.

---

##  Features

| Module | Description |
|---------|--------------|
|  **Dashboard** | Displays athlete overview, training stats, and motivational quotes |
|  **Session Management** | Log and review training sessions (rounds, minutes, RPE, notes) |
|  **Exercise Recommendation** | Fetch real exercises by muscle group and difficulty from API Ninjas |
|  **Google Login** | Secure sign-in using Google OAuth |
|  **Cloud Ready** | Deployable to Render or other platforms with Docker support |

---

## Tech Stack

| Layer | Technology |
|-------|-------------|
| **Frontend** | HTML, CSS, JavaScript |
| **Backend** | Python (FastAPI) |
| **Database** | SQLite3 |
| **APIs Used** | Exercise API (API Ninjas)|
| **Auth** | Google OAuth 2.0 |
| **Deployment** | Render (Docker-based) |
| **Version Control** | Git + GitHub |

---

## ⚙️ Setup Instructions

1️⃣ Clone the Repository

```bash
git clone https://github.com/Thitiwut245/smart-athlete-planner.git
cd smart-athlete-planner

2️⃣ Create and Activate Virtual Environment

python -m venv .venv
source .venv/bin/activate        # macOS/Linux
.venv\Scripts\activate           # Windows

3️⃣ Install Dependencies

pip install -r requirements.txt

4️⃣ Create .env File

Create a .env file in the project root with the following keys:

API_KEY=dev-secret-key
DATABASE_URL=sqlite:///./smart.db
EXERCISE_API_KEY=LRCporlwTPnN9h/C92ZRbQ==Evn4ZNUBGms12t4i
ALLOW_UI_NO_KEY=true
SECRET_KEY=your-long-random-string
ACCESS_TOKEN_EXPIRE_MINUTES=43200
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
OAUTH_REDIRECT_URL=http://127.0.0.1:8000/auth/google/callback

5️⃣ Run the Application

uvicorn app.main:app --reload


Then open browser and go to:
👉 http://127.0.0.1:8000


 API Reference
🔹 1. Athlete Management
Method	Endpoint	Description
GET	/api/v1/athletes	Retrieve all athletes
POST	/api/v1/athletes	Create a new athlete
DELETE	/api/v1/athletes/{id}	Delete athlete by ID
🔹 2. Training Sessions
Method	Endpoint	Description
GET	/api/v1/sessions/athlete/{id}	Get all sessions for a specific athlete
POST	/api/v1/sessions	Create a new training session
DELETE	/api/v1/sessions/{id}	Delete session by ID
🔹 3. Exercise Recommendations
Method	Endpoint	Description
GET	/api/v1/exercise/random	Get random exercise
GET	/api/v1/exercise?muscle={muscle}&difficulty={difficulty}	Search exercises by muscle & difficulty



Team Roles
Name	Student ID	Role	Responsibility
Thitiwut Sriamonrat	663380213-6	Developer / Project Lead	Backend API, Database, Deployment
Natrapa Srivicha    663380504-5 Frontend Developer	UI Design, HTML/JS integration
