# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Docker Development (Primary)
```bash
# Start the application
docker-compose up -d

# Rebuild after changes to requirements.txt or Dockerfile
docker-compose up --build

# View logs
docker-compose logs -f dashboard

# Stop the application
docker-compose down

# Stop and remove volumes (WARNING: deletes MongoDB data)
docker-compose down -v
```

### Local Development
```bash
# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run Flask development server
python run.py

# Run with Flask CLI
flask run --host=0.0.0.0 --port=5000 --reload
```

### Database Management
```bash
# Access MongoDB shell (Docker)
docker exec -it app_mongo mongosh app_management

# Backup MongoDB data (Docker)
docker exec app_mongo mongodump --db app_management --out /data/db/backup

# View MongoDB logs
docker logs app_mongo
```

## Architecture Overview

### Flask Blueprint Structure
The application uses Flask's Blueprint pattern for modularity:
- `app/__init__.py`: Application factory pattern with `create_app()` function
- `app/main/`: Main blueprint containing all routes and templates
- Blueprint registration allows easy extension with new features (auth, API, etc.)

### MongoDB Integration
- Uses Flask-PyMongo for MongoDB connection management
- Connection configured via `MONGODB_URI` environment variable
- MongoDB runs on port 27018 (mapped from internal 27017) to avoid conflicts
- Data persisted in `./mongo_data/` directory

### Model Layer
Located in `app/models/mongo_models.py`:
- `Application`: Manages app documents with CRUD operations
- `Task`: Manages task documents linked to applications
- Models handle their own MongoDB operations directly (no ORM)
- Automatic timestamp management (created_at, updated_at)

### Route Organization
All routes in `app/main/routes.py`:
- Application routes: `/`, `/applications/<id>`, `/applications/add`
- Task routes: `/applications/<id>/tasks/add`, `/tasks/<id>/update`
- Dashboard route: `/dashboard`
- Each route handles both GET and POST methods where applicable

### Template Structure
- Base template: `app/templates/base.html` (Bootstrap 5)
- Blueprint templates: `app/main/templates/main/`
- Error pages: `app/templates/errors/`
- All templates extend base.html for consistent layout

## Important Configuration

### Environment Variables (.env)
```
FLASK_APP=app
FLASK_ENV=development
SECRET_KEY=your-secret-key-here-change-in-production
MONGODB_URI=mongodb://localhost:27018/app_management
```

### Port Mappings
- Web Application: localhost:8026 → container:5000
- MongoDB: localhost:27018 → container:27017

### Docker Network
- Internal service communication uses service names (e.g., `mongodb:27017`)
- Dashboard service connects to MongoDB via `mongodb://mongodb:27017/app_management`

## Key Implementation Details

### Task Status Flow
Tasks progress through three states: "Not Started" → "In Progress" → "Completed"
Defined in `Task.STATUSES` constant in mongo_models.py

### Application Statistics
- Calculated dynamically in `Application.get_all()` method
- Includes total_tasks, completed_tasks, and completion_percentage
- Statistics not stored in database, computed on retrieval

### Form Validation
- Server-side validation in route handlers
- Required fields checked before database operations
- Flash messages for user feedback (success/danger categories)

### MongoDB Document Structure
Applications collection:
```python
{
    'name': str,
    'description': str,
    'repo_url': str,
    'tags': list,
    'notes': str,
    'created_at': datetime,
    'updated_at': datetime
}
```

Tasks collection:
```python
{
    'app_id': str,
    'title': str,
    'status': str,
    'notes': str,
    'git_branch': str,
    'created_at': datetime,
    'updated_at': datetime
}
```