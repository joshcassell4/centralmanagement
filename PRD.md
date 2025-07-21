# Product Requirements Document (PRD)

## Project Title: Central Application Management Dashboard

### Overview
A Flask-based web application, running in a Docker container, for managing and tracking the development status of multiple applications. This tool provides a central dashboard to list active applications, view their feature/task progress, and observe ongoing development efforts across projects. It will be accessible via an obscure port (e.g., 8026) and serve as a personal dev orchestrator.

---

## Goals

- Centralize the visibility and control of application development.
- Track features and their development states per application.
- Associate features with active git branches.
- Easily add, update, and view status of applications and their development trajectory.
- Run isolated in Docker, accessible via port `8026`.

---

## Features

### 1. **Application List Page**
- Display a list of all tracked applications.
- Show basic metadata: app name, last updated, total tasks, % complete.
- Button to add new application.

### 2. **Add Application**
- Form to enter:
  - Application name
  - Description
  - Git repository URL
  - Tags (optional)
- On submission, the app is added to the dashboard.

### 3. **Application Detail Page**
- Display:
  - App name, description, and Git repo URL (clickable).
  - List of features/tasks with:
    - Title
    - Status: `Not Started`, `In Progress`, `Completed`
    - Optional notes
    - Associated Git branch
- Option to:
  - Add new tasks/features.
  - Update task status or associated branch.
  - Remove or edit existing tasks.

### 4. **Status Dashboard**
- Overview of:
  - All applications and % task completion.
  - Optional: display by tag or category.
- Sort/filter by completion status, most active, etc.

### 5. **Settings & Config**
- Ability to configure:
  - Port (default `8026`)
  - Admin login (future enhancement)
  - Optional notifications (future)

---

## Technical Details

### Tech Stack
- **Backend**: Flask
- **Frontend**: Jinja2 Templates + Bootstrap (for speed)
- **Database**: MongoDB (JSON-friendly, flexible schema)
- **Containerization**: Docker (served on port 8026)
- **Data Persistence**: MongoDB container uses a **volume** mapped to a local directory for persistent storage
- **Extensibility**: Flask **Blueprints** used to modularize routes, making it easy to expand functionality (e.g., auth, API, git integration)

### Directory Layout (Initial)

project/
├── app/
│ ├── init.py
│ ├── main/
│ │ ├── init.py
│ │ ├── routes.py
│ │ └── templates/
│ ├── models/
│ │ └── mongo_models.py
│ └── utils/
│ └── helpers.py
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env
└── PRD.md


---

## Docker Configuration

```yaml
# docker-compose.yml
version: '3.9'

services:
  dashboard:
    build: .
    ports:
      - "8026:5000"
    volumes:
      - .:/app
    environment:
      - FLASK_APP=app
      - FLASK_ENV=development
    depends_on:
      - mongodb
    restart: unless-stopped

  mongodb:
    image: mongo:7
    container_name: app_mongo
    ports:
      - "27017:27017"
    volumes:
      - ./mongo_data:/data/db
    restart: unless-stopped

MongoDB Notes
MongoDB will store application and task data.

The directory ./mongo_data/ on the host machine is mapped to the internal container path /data/db for persistent volume storage.

Documents will be stored in collections such as:

applications

tasks

Fields will include dynamic JSON where appropriate.

Flask Blueprints
The application will use Flask Blueprints to maintain modularity and extensibility. Initial blueprints might include:

main: handles dashboard views and routing

apps: handles application management

tasks: handles task CRUD operations

Future Blueprints:

auth: authentication

api: REST API for external integration

git: git repository interactions (future enhancement)

Success Criteria
Able to add applications and tasks via UI.

Tasks update with status and branch info.

Dashboard provides actionable insight into overall development progress.

All data persists across sessions via MongoDB volume.

Modular structure enables easy growth via Blueprints.

Runs successfully in Docker on port 8026.

Stretch Goals
Git branch auto-detection using gitpython

REST API for automation

Drag-and-drop task prioritization

User authentication

Export/import project data

Notifications for completed features

Notes
Keep UI simple and developer-focused.

Initial version targets single-user usage; multi-user and auth can come later.

Project can grow into a broader CI/CD productivity orchestration tool over time.