from datetime import datetime
from bson import ObjectId
from app import mongo

class Application:
    """Model for Application documents in MongoDB"""
    
    collection = 'applications'
    
    @staticmethod
    def create(name, description, repo_url, tags=None, notes=''):
        """Create a new application"""
        app_doc = {
            'name': name,
            'description': description,
            'repo_url': repo_url,
            'tags': tags or [],
            'notes': notes,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        result = mongo.db[Application.collection].insert_one(app_doc)
        return str(result.inserted_id)
    
    @staticmethod
    def get_all():
        """Get all applications with task statistics"""
        apps = list(mongo.db[Application.collection].find())
        
        # Add task statistics for each app
        for app in apps:
            app['_id'] = str(app['_id'])
            tasks = Task.get_by_app_id(app['_id'])
            app['total_tasks'] = len(tasks)
            app['completed_tasks'] = len([t for t in tasks if t['status'] == 'Completed'])
            app['completion_percentage'] = (
                round((app['completed_tasks'] / app['total_tasks']) * 100) 
                if app['total_tasks'] > 0 else 0
            )
            
            # Group tasks by status
            app['in_progress_tasks'] = [t for t in tasks if t['status'] == 'In Progress']
            app['not_started_tasks'] = [t for t in tasks if t['status'] == 'Not Started']
        
        return apps
    
    @staticmethod
    def get_by_id(app_id):
        """Get a single application by ID"""
        app = mongo.db[Application.collection].find_one({'_id': ObjectId(app_id)})
        if app:
            app['_id'] = str(app['_id'])
        return app
    
    @staticmethod
    def update(app_id, update_data):
        """Update an application"""
        update_data['updated_at'] = datetime.utcnow()
        result = mongo.db[Application.collection].update_one(
            {'_id': ObjectId(app_id)},
            {'$set': update_data}
        )
        return result.modified_count > 0
    
    @staticmethod
    def delete(app_id):
        """Delete an application and all its tasks"""
        # Delete all associated tasks first
        Task.delete_by_app_id(app_id)
        
        # Delete the application
        result = mongo.db[Application.collection].delete_one({'_id': ObjectId(app_id)})
        return result.deleted_count > 0


class Task:
    """Model for Task documents in MongoDB"""
    
    collection = 'tasks'
    
    STATUSES = ['Not Started', 'In Progress', 'Completed']
    
    @staticmethod
    def create(app_id, title, status='Not Started', notes='', git_branch=''):
        """Create a new task"""
        task_doc = {
            'app_id': app_id,
            'title': title,
            'status': status,
            'notes': notes,
            'git_branch': git_branch,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        result = mongo.db[Task.collection].insert_one(task_doc)
        
        # Update the parent application's updated_at timestamp
        Application.update(app_id, {})
        
        return str(result.inserted_id)
    
    @staticmethod
    def get_by_app_id(app_id):
        """Get all tasks for an application"""
        tasks = list(mongo.db[Task.collection].find({'app_id': app_id}))
        for task in tasks:
            task['_id'] = str(task['_id'])
        return tasks
    
    @staticmethod
    def get_by_id(task_id):
        """Get a single task by ID"""
        task = mongo.db[Task.collection].find_one({'_id': ObjectId(task_id)})
        if task:
            task['_id'] = str(task['_id'])
        return task
    
    @staticmethod
    def update(task_id, update_data):
        """Update a task"""
        update_data['updated_at'] = datetime.utcnow()
        
        # Get the task to find its app_id
        task = Task.get_by_id(task_id)
        
        result = mongo.db[Task.collection].update_one(
            {'_id': ObjectId(task_id)},
            {'$set': update_data}
        )
        
        # Update the parent application's updated_at timestamp
        if task and result.modified_count > 0:
            Application.update(task['app_id'], {})
        
        return result.modified_count > 0
    
    @staticmethod
    def delete(task_id):
        """Delete a task"""
        # Get the task to find its app_id
        task = Task.get_by_id(task_id)
        
        result = mongo.db[Task.collection].delete_one({'_id': ObjectId(task_id)})
        
        # Update the parent application's updated_at timestamp
        if task and result.deleted_count > 0:
            Application.update(task['app_id'], {})
        
        return result.deleted_count > 0
    
    @staticmethod
    def delete_by_app_id(app_id):
        """Delete all tasks for an application"""
        result = mongo.db[Task.collection].delete_many({'app_id': app_id})
        return result.deleted_count