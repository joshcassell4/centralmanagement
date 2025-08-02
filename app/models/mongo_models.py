from datetime import datetime
from bson import ObjectId
from app import mongo

class Application:
    """Model for Application documents in MongoDB"""
    
    collection = 'applications'
    
    @staticmethod
    def create(name, description, repo_url, tags=None, notes='', local_directory=''):
        """Create a new application"""
        app_doc = {
            'name': name,
            'description': description,
            'repo_url': repo_url,
            'local_directory': local_directory,
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


class Pet:
    """Model for Pet documents in MongoDB"""
    
    collection = 'pets'
    
    SPECIES = ['Dog', 'Cat', 'Bird', 'Fish', 'Rabbit', 'Hamster', 'Guinea Pig', 'Reptile', 'Other']
    GENDERS = ['Male', 'Female', 'Unknown']
    
    @staticmethod
    def create(name, species, breed='', age='', weight='', color='', gender='Unknown', 
               microchip_id='', registration_number='', photo_url='', vet_info='', 
               medical_conditions='', allergies='', medications='', last_checkup_date=None,
               feeding_schedule='', special_notes='', vaccination_dates=''):
        """Create a new pet"""
        pet_doc = {
            'name': name,
            'species': species,
            'breed': breed,
            'age': age,
            'weight': weight,
            'color': color,
            'gender': gender,
            'microchip_id': microchip_id,
            'registration_number': registration_number,
            'photo_url': photo_url,
            'vet_info': vet_info,
            'medical_conditions': medical_conditions,
            'allergies': allergies,
            'medications': medications,
            'last_checkup_date': last_checkup_date,
            'feeding_schedule': feeding_schedule,
            'special_notes': special_notes,
            'vaccination_dates': vaccination_dates,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        result = mongo.db[Pet.collection].insert_one(pet_doc)
        return str(result.inserted_id)
    
    @staticmethod
    def get_all():
        """Get all pets"""
        pets = list(mongo.db[Pet.collection].find().sort('name', 1))
        for pet in pets:
            pet['_id'] = str(pet['_id'])
        return pets
    
    @staticmethod
    def get_by_id(pet_id):
        """Get a single pet by ID"""
        pet = mongo.db[Pet.collection].find_one({'_id': ObjectId(pet_id)})
        if pet:
            pet['_id'] = str(pet['_id'])
        return pet
    
    @staticmethod
    def update(pet_id, update_data):
        """Update a pet"""
        update_data['updated_at'] = datetime.utcnow()
        result = mongo.db[Pet.collection].update_one(
            {'_id': ObjectId(pet_id)},
            {'$set': update_data}
        )
        return result.modified_count > 0
    
    @staticmethod
    def delete(pet_id):
        """Delete a pet"""
        result = mongo.db[Pet.collection].delete_one({'_id': ObjectId(pet_id)})
        return result.deleted_count > 0
    
    @staticmethod
    def get_by_species(species):
        """Get pets by species"""
        pets = list(mongo.db[Pet.collection].find({'species': species}).sort('name', 1))
        for pet in pets:
            pet['_id'] = str(pet['_id'])
        return pets


class InventoryItem:
    """Model for Inventory Item documents in MongoDB"""
    
    collection = 'inventory'
    
    CATEGORIES = ['Food', 'Toys', 'Medical', 'Grooming', 'Bedding', 'Accessories', 'Treats', 'Other']
    UNITS = ['pieces', 'lbs', 'kg', 'bottles', 'boxes', 'bags', 'cans', 'tubes']
    
    @staticmethod
    def create(name, description='', category='Other', quantity=0, unit='pieces', 
               low_stock_threshold=5, price_per_unit=0.0, supplier='', 
               purchase_date=None, expiration_date=None, for_pets=None, usage_notes=''):
        """Create a new inventory item"""
        inventory_doc = {
            'name': name,
            'description': description,
            'category': category,
            'quantity': quantity,
            'unit': unit,
            'low_stock_threshold': low_stock_threshold,
            'price_per_unit': price_per_unit,
            'supplier': supplier,
            'purchase_date': purchase_date,
            'expiration_date': expiration_date,
            'for_pets': for_pets or [],
            'usage_notes': usage_notes,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        result = mongo.db[InventoryItem.collection].insert_one(inventory_doc)
        return str(result.inserted_id)
    
    @staticmethod
    def get_all():
        """Get all inventory items with stock status"""
        items = list(mongo.db[InventoryItem.collection].find().sort('name', 1))
        for item in items:
            item['_id'] = str(item['_id'])
            # Add stock status
            item['is_low_stock'] = item['quantity'] <= item['low_stock_threshold']
            item['stock_status'] = 'Low Stock' if item['is_low_stock'] else 'In Stock'
        return items
    
    @staticmethod
    def get_by_id(item_id):
        """Get a single inventory item by ID"""
        item = mongo.db[InventoryItem.collection].find_one({'_id': ObjectId(item_id)})
        if item:
            item['_id'] = str(item['_id'])
            item['is_low_stock'] = item['quantity'] <= item['low_stock_threshold']
            item['stock_status'] = 'Low Stock' if item['is_low_stock'] else 'In Stock'
        return item
    
    @staticmethod
    def update(item_id, update_data):
        """Update an inventory item"""
        update_data['updated_at'] = datetime.utcnow()
        result = mongo.db[InventoryItem.collection].update_one(
            {'_id': ObjectId(item_id)},
            {'$set': update_data}
        )
        return result.modified_count > 0
    
    @staticmethod
    def delete(item_id):
        """Delete an inventory item"""
        result = mongo.db[InventoryItem.collection].delete_one({'_id': ObjectId(item_id)})
        return result.deleted_count > 0
    
    @staticmethod
    def get_low_stock():
        """Get items that are low in stock"""
        items = list(mongo.db[InventoryItem.collection].find({
            '$expr': {'$lte': ['$quantity', '$low_stock_threshold']}
        }).sort('name', 1))
        for item in items:
            item['_id'] = str(item['_id'])
            item['is_low_stock'] = True
            item['stock_status'] = 'Low Stock'
        return items
    
    @staticmethod
    def get_by_category(category):
        """Get inventory items by category"""
        items = list(mongo.db[InventoryItem.collection].find({'category': category}).sort('name', 1))
        for item in items:
            item['_id'] = str(item['_id'])
            item['is_low_stock'] = item['quantity'] <= item['low_stock_threshold']
            item['stock_status'] = 'Low Stock' if item['is_low_stock'] else 'In Stock'
        return items


class Todo:
    """Model for Todo documents in MongoDB"""
    
    collection = 'todos'
    
    PRIORITIES = ['Low', 'Medium', 'High']
    STATUSES = ['Todo', 'In Progress', 'Completed']
    
    @staticmethod
    def create(title, description='', priority='Medium', status='Todo', due_date=None, 
               tags=None, assigned_to=''):
        """Create a new todo item"""
        todo_doc = {
            'title': title,
            'description': description,
            'priority': priority,
            'status': status,
            'due_date': due_date,
            'tags': tags or [],
            'assigned_to': assigned_to,
            'completed_at': None,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        result = mongo.db[Todo.collection].insert_one(todo_doc)
        return str(result.inserted_id)
    
    @staticmethod
    def get_all(status_filter=None, priority_filter=None, tag_filter=None):
        """Get all todos with optional filtering"""
        query = {}
        if status_filter:
            query['status'] = status_filter
        if priority_filter:
            query['priority'] = priority_filter
        if tag_filter:
            query['tags'] = tag_filter
        
        todos = list(mongo.db[Todo.collection].find(query).sort([('priority', -1), ('created_at', -1)]))
        
        for todo in todos:
            todo['_id'] = str(todo['_id'])
            # Add overdue flag if due date has passed
            if todo.get('due_date') and todo['status'] != 'Completed':
                todo['is_overdue'] = todo['due_date'] < datetime.utcnow()
            else:
                todo['is_overdue'] = False
        
        return todos
    
    @staticmethod
    def get_by_id(todo_id):
        """Get a single todo by ID"""
        todo = mongo.db[Todo.collection].find_one({'_id': ObjectId(todo_id)})
        if todo:
            todo['_id'] = str(todo['_id'])
            # Add overdue flag
            if todo.get('due_date') and todo['status'] != 'Completed':
                todo['is_overdue'] = todo['due_date'] < datetime.utcnow()
            else:
                todo['is_overdue'] = False
        return todo
    
    @staticmethod
    def update(todo_id, update_data):
        """Update a todo item"""
        update_data['updated_at'] = datetime.utcnow()
        
        # If marking as completed, set completed_at
        if update_data.get('status') == 'Completed':
            update_data['completed_at'] = datetime.utcnow()
        
        result = mongo.db[Todo.collection].update_one(
            {'_id': ObjectId(todo_id)},
            {'$set': update_data}
        )
        return result.modified_count > 0
    
    @staticmethod
    def delete(todo_id):
        """Delete a todo item"""
        result = mongo.db[Todo.collection].delete_one({'_id': ObjectId(todo_id)})
        return result.deleted_count > 0
    
    @staticmethod
    def get_by_tag(tag):
        """Get todos by tag"""
        todos = list(mongo.db[Todo.collection].find({'tags': tag}).sort([('priority', -1), ('created_at', -1)]))
        for todo in todos:
            todo['_id'] = str(todo['_id'])
            if todo.get('due_date') and todo['status'] != 'Completed':
                todo['is_overdue'] = todo['due_date'] < datetime.utcnow()
            else:
                todo['is_overdue'] = False
        return todos
    
    @staticmethod
    def get_all_tags():
        """Get all unique tags from todos"""
        # Use aggregation to get all unique tags
        pipeline = [
            {'$unwind': '$tags'},
            {'$group': {'_id': '$tags'}},
            {'$sort': {'_id': 1}}
        ]
        result = list(mongo.db[Todo.collection].aggregate(pipeline))
        return [doc['_id'] for doc in result]
    
    @staticmethod
    def get_statistics():
        """Get todo statistics"""
        total = mongo.db[Todo.collection].count_documents({})
        completed = mongo.db[Todo.collection].count_documents({'status': 'Completed'})
        in_progress = mongo.db[Todo.collection].count_documents({'status': 'In Progress'})
        todo = mongo.db[Todo.collection].count_documents({'status': 'Todo'})
        
        # Count by priority
        high_priority = mongo.db[Todo.collection].count_documents({'priority': 'High', 'status': {'$ne': 'Completed'}})
        medium_priority = mongo.db[Todo.collection].count_documents({'priority': 'Medium', 'status': {'$ne': 'Completed'}})
        low_priority = mongo.db[Todo.collection].count_documents({'priority': 'Low', 'status': {'$ne': 'Completed'}})
        
        # Count overdue
        overdue = mongo.db[Todo.collection].count_documents({
            'due_date': {'$lt': datetime.utcnow()},
            'status': {'$ne': 'Completed'}
        })
        
        return {
            'total': total,
            'completed': completed,
            'in_progress': in_progress,
            'todo': todo,
            'high_priority': high_priority,
            'medium_priority': medium_priority,
            'low_priority': low_priority,
            'overdue': overdue,
            'completion_rate': round((completed / total * 100) if total > 0 else 0, 1)
        }