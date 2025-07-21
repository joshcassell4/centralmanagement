# Central Application Management Dashboard

A Flask-based web application for managing and tracking the development status of multiple applications.

## Features

- **Application Management**: Add, view, edit, and delete applications
- **Task Tracking**: Create and manage tasks/features for each application
- **Status Dashboard**: Overview of all applications and their progress
- **Git Integration**: Track git branches associated with tasks
- **Tag Support**: Organize applications with tags
- **Progress Visualization**: Visual progress bars and completion percentages
- **Application Notes**: Add notes to applications (e.g., port numbers, configuration details)

## Quick Start

### Using Docker (Recommended)

1. Make sure Docker and Docker Compose are installed on your system.

2. Clone or navigate to the project directory.

3. Start the application:
   ```bash
   docker-compose up -d
   ```

4. Access the application at: http://localhost:8026

5. MongoDB will be accessible on port 27018 (instead of the default 27017)

6. To stop the application:
   ```bash
   docker-compose down
   ```

### Local Development (Without Docker)

1. Install MongoDB locally and ensure it's running on port 27018 (or update the MONGODB_URI in .env).

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   python run.py
   ```

5. Access the application at: http://localhost:5000

## Usage

1. **Add an Application**: Click "Add New Application" to track a new project
2. **Manage Tasks**: Click on any application to add and manage its tasks
3. **Update Status**: Change task status from "Not Started" → "In Progress" → "Completed"
4. **View Dashboard**: Check the dashboard for an overview of all applications

## Data Persistence

- MongoDB data is persisted in the `./mongo_data` directory
- This ensures your data is retained even when containers are stopped

## Environment Variables

Create a `.env` file to customize settings:
```
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
MONGODB_URI=mongodb://localhost:27017/app_management
```

## Architecture

- **Backend**: Flask with Blueprint architecture
- **Database**: MongoDB for flexible data storage
- **Frontend**: Bootstrap 5 for responsive UI
- **Containerization**: Docker for easy deployment