from flask import render_template, request, redirect, url_for, flash
from app.main import main_bp, media_bp
from app.models.mongo_models import Application, Task, Pet, InventoryItem, Todo
from bson.errors import InvalidId
from datetime import datetime, timedelta

@main_bp.route('/')
@main_bp.route('/applications')
def index():
    """Display list of all applications"""
    applications = Application.get_all()
    return render_template('main/index.html', applications=applications)


@main_bp.route('/applications/add', methods=['GET', 'POST'])
def add_application():
    """Add a new application"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        repo_url = request.form.get('repo_url', '').strip()
        local_directory = request.form.get('local_directory', '').strip()
        tags = request.form.get('tags', '').strip()
        notes = request.form.get('notes', '').strip()
        
        # Validate required fields
        if not name:
            flash('Application name is required', 'danger')
            return redirect(url_for('main.add_application'))
        
        # Process tags
        tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()] if tags else []
        
        # Create the application
        try:
            app_id = Application.create(name, description, repo_url, tag_list, notes, local_directory)
            flash(f'Application "{name}" added successfully!', 'success')
            return redirect(url_for('main.application_detail', app_id=app_id))
        except Exception as e:
            flash(f'Error adding application: {str(e)}', 'danger')
            return redirect(url_for('main.add_application'))
    
    return render_template('main/add_application.html')


@main_bp.route('/applications/<app_id>')
def application_detail(app_id):
    """Display application details and tasks"""
    try:
        application = Application.get_by_id(app_id)
        if not application:
            flash('Application not found', 'danger')
            return redirect(url_for('main.index'))
        
        tasks = Task.get_by_app_id(app_id)
        return render_template('main/application_detail.html', 
                             application=application, 
                             tasks=tasks,
                             task_statuses=Task.STATUSES)
    except InvalidId:
        flash('Invalid application ID', 'danger')
        return redirect(url_for('main.index'))


@main_bp.route('/applications/<app_id>/tasks/add', methods=['POST'])
def add_task(app_id):
    """Add a new task to an application"""
    title = request.form.get('title', '').strip()
    status = request.form.get('status', 'Not Started')
    notes = request.form.get('notes', '').strip()
    git_branch = request.form.get('git_branch', '').strip()
    
    if not title:
        flash('Task title is required', 'danger')
        return redirect(url_for('main.application_detail', app_id=app_id))
    
    try:
        Task.create(app_id, title, status, notes, git_branch)
        flash('Task added successfully!', 'success')
    except Exception as e:
        flash(f'Error adding task: {str(e)}', 'danger')
    
    return redirect(url_for('main.application_detail', app_id=app_id))


@main_bp.route('/tasks/<task_id>/update', methods=['POST'])
def update_task(task_id):
    """Update a task"""
    try:
        task = Task.get_by_id(task_id)
        if not task:
            flash('Task not found', 'danger')
            return redirect(url_for('main.index'))
        
        update_data = {
            'title': request.form.get('title', task['title']).strip(),
            'status': request.form.get('status', task['status']),
            'notes': request.form.get('notes', task['notes']).strip(),
            'git_branch': request.form.get('git_branch', task['git_branch']).strip()
        }
        
        if Task.update(task_id, update_data):
            flash('Task updated successfully!', 'success')
        else:
            flash('Error updating task', 'danger')
        
        return redirect(url_for('main.application_detail', app_id=task['app_id']))
    except InvalidId:
        flash('Invalid task ID', 'danger')
        return redirect(url_for('main.index'))


@main_bp.route('/tasks/<task_id>/delete', methods=['POST'])
def delete_task(task_id):
    """Delete a task"""
    try:
        task = Task.get_by_id(task_id)
        if not task:
            flash('Task not found', 'danger')
            return redirect(url_for('main.index'))
        
        app_id = task['app_id']
        
        if Task.delete(task_id):
            flash('Task deleted successfully!', 'success')
        else:
            flash('Error deleting task', 'danger')
        
        return redirect(url_for('main.application_detail', app_id=app_id))
    except InvalidId:
        flash('Invalid task ID', 'danger')
        return redirect(url_for('main.index'))


@main_bp.route('/applications/<app_id>/delete', methods=['POST'])
def delete_application(app_id):
    """Delete an application"""
    try:
        if Application.delete(app_id):
            flash('Application deleted successfully!', 'success')
        else:
            flash('Error deleting application', 'danger')
    except InvalidId:
        flash('Invalid application ID', 'danger')
    
    return redirect(url_for('main.index'))


@main_bp.route('/applications/<app_id>/update', methods=['POST'])
def update_application(app_id):
    """Update an application"""
    try:
        application = Application.get_by_id(app_id)
        if not application:
            flash('Application not found', 'danger')
            return redirect(url_for('main.index'))
        
        update_data = {
            'name': request.form.get('name', application['name']).strip(),
            'description': request.form.get('description', application['description']).strip(),
            'repo_url': request.form.get('repo_url', application['repo_url']).strip(),
            'local_directory': request.form.get('local_directory', application.get('local_directory', '')).strip(),
            'notes': request.form.get('notes', application.get('notes', '')).strip()
        }
        
        # Process tags
        tags = request.form.get('tags', '')
        update_data['tags'] = [tag.strip() for tag in tags.split(',') if tag.strip()] if tags else []
        
        if Application.update(app_id, update_data):
            flash('Application updated successfully!', 'success')
        else:
            flash('Error updating application', 'danger')
            
        return redirect(url_for('main.application_detail', app_id=app_id))
    except InvalidId:
        flash('Invalid application ID', 'danger')
        return redirect(url_for('main.index'))


@main_bp.route('/dashboard')
def dashboard():
    """Display the status dashboard"""
    applications = Application.get_all()
    pets = Pet.get_all()
    inventory_items = InventoryItem.get_all()
    todo_stats = Todo.get_statistics()
    
    # Calculate application statistics
    total_apps = len(applications)
    total_tasks = sum(app['total_tasks'] for app in applications)
    completed_tasks = sum(app['completed_tasks'] for app in applications)
    in_progress_tasks = sum(len(app.get('in_progress_tasks', [])) for app in applications)
    
    # Calculate overall completion percentage
    overall_completion = (
        round((completed_tasks / total_tasks) * 100) 
        if total_tasks > 0 else 0
    )
    
    # Calculate pet statistics
    total_pets = len(pets)
    pets_by_species = {}
    pets_needing_checkup = []
    
    for pet in pets:
        species = pet.get('species', 'Unknown')
        pets_by_species[species] = pets_by_species.get(species, 0) + 1
        
        # Check if pet needs a checkup (more than 1 year since last checkup)
        if pet.get('last_checkup_date'):
            days_since_checkup = (datetime.utcnow() - pet['last_checkup_date']).days
            if days_since_checkup > 365:  # More than 1 year
                pets_needing_checkup.append(pet)
        else:
            # No checkup date recorded
            pets_needing_checkup.append(pet)
    
    # Calculate inventory statistics
    total_inventory_items = len(inventory_items)
    low_stock_items = [item for item in inventory_items if item['is_low_stock']]
    total_inventory_value = sum(item['quantity'] * item['price_per_unit'] for item in inventory_items)
    
    # Items expiring soon (within 30 days)
    expiring_soon = []
    for item in inventory_items:
        if item.get('expiration_date'):
            days_until_expiry = (item['expiration_date'] - datetime.utcnow()).days
            if 0 <= days_until_expiry <= 30:
                expiring_soon.append(item)
    
    # Sort applications by different criteria
    most_active = sorted(applications, 
                        key=lambda x: x.get('updated_at', x.get('created_at')), 
                        reverse=True)[:5]
    
    return render_template('main/dashboard.html',
                         applications=applications,
                         total_apps=total_apps,
                         total_tasks=total_tasks,
                         completed_tasks=completed_tasks,
                         in_progress_tasks=in_progress_tasks,
                         overall_completion=overall_completion,
                         most_active=most_active,
                         pets=pets,
                         total_pets=total_pets,
                         pets_by_species=pets_by_species,
                         pets_needing_checkup=pets_needing_checkup,
                         inventory_items=inventory_items,
                         total_inventory_items=total_inventory_items,
                         low_stock_items=low_stock_items,
                         total_inventory_value=total_inventory_value,
                         expiring_soon=expiring_soon,
                         todo_stats=todo_stats)


# Pet Routes
@main_bp.route('/pets')
def pets_index():
    """Display list of all pets"""
    pets = Pet.get_all()
    return render_template('main/pets/index.html', pets=pets)


@main_bp.route('/pets/add', methods=['GET', 'POST'])
def add_pet():
    """Add a new pet"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        species = request.form.get('species', '').strip()
        breed = request.form.get('breed', '').strip()
        age = request.form.get('age', '').strip()
        weight = request.form.get('weight', '').strip()
        color = request.form.get('color', '').strip()
        gender = request.form.get('gender', 'Unknown')
        microchip_id = request.form.get('microchip_id', '').strip()
        registration_number = request.form.get('registration_number', '').strip()
        photo_url = request.form.get('photo_url', '').strip()
        vet_info = request.form.get('vet_info', '').strip()
        medical_conditions = request.form.get('medical_conditions', '').strip()
        allergies = request.form.get('allergies', '').strip()
        medications = request.form.get('medications', '').strip()
        feeding_schedule = request.form.get('feeding_schedule', '').strip()
        special_notes = request.form.get('special_notes', '').strip()
        vaccination_dates = request.form.get('vaccination_dates', '').strip()
        
        # Handle last_checkup_date
        last_checkup_str = request.form.get('last_checkup_date', '').strip()
        last_checkup_date = None
        if last_checkup_str:
            try:
                last_checkup_date = datetime.strptime(last_checkup_str, '%Y-%m-%d')
            except ValueError:
                flash('Invalid date format for last checkup', 'danger')
                return redirect(url_for('main.add_pet'))
        
        # Validate required fields
        if not name:
            flash('Pet name is required', 'danger')
            return redirect(url_for('main.add_pet'))
        
        if not species:
            flash('Pet species is required', 'danger')
            return redirect(url_for('main.add_pet'))
        
        # Create the pet
        try:
            pet_id = Pet.create(name, species, breed, age, weight, color, gender,
                               microchip_id, registration_number, photo_url, vet_info,
                               medical_conditions, allergies, medications, last_checkup_date,
                               feeding_schedule, special_notes, vaccination_dates)
            flash(f'Pet "{name}" added successfully!', 'success')
            return redirect(url_for('main.pet_detail', pet_id=pet_id))
        except Exception as e:
            flash(f'Error adding pet: {str(e)}', 'danger')
            return redirect(url_for('main.add_pet'))
    
    return render_template('main/pets/add_pet.html', 
                         species_options=Pet.SPECIES, 
                         gender_options=Pet.GENDERS)


@main_bp.route('/pets/<pet_id>')
def pet_detail(pet_id):
    """Display pet details"""
    try:
        pet = Pet.get_by_id(pet_id)
        if not pet:
            flash('Pet not found', 'danger')
            return redirect(url_for('main.pets_index'))
        
        # Get inventory items associated with this pet
        all_inventory = InventoryItem.get_all()
        pet_inventory = [item for item in all_inventory if pet_id in item.get('for_pets', [])]
        
        return render_template('main/pets/pet_detail.html', 
                             pet=pet, 
                             pet_inventory=pet_inventory,
                             species_options=Pet.SPECIES,
                             gender_options=Pet.GENDERS)
    except InvalidId:
        flash('Invalid pet ID', 'danger')
        return redirect(url_for('main.pets_index'))


@main_bp.route('/pets/<pet_id>/update', methods=['POST'])
def update_pet(pet_id):
    """Update a pet"""
    try:
        pet = Pet.get_by_id(pet_id)
        if not pet:
            flash('Pet not found', 'danger')
            return redirect(url_for('main.pets_index'))
        
        # Handle last_checkup_date
        last_checkup_str = request.form.get('last_checkup_date', '').strip()
        last_checkup_date = pet.get('last_checkup_date')
        if last_checkup_str:
            try:
                last_checkup_date = datetime.strptime(last_checkup_str, '%Y-%m-%d')
            except ValueError:
                flash('Invalid date format for last checkup', 'danger')
                return redirect(url_for('main.pet_detail', pet_id=pet_id))
        elif last_checkup_str == '':
            last_checkup_date = None
        
        update_data = {
            'name': request.form.get('name', pet['name']).strip(),
            'species': request.form.get('species', pet['species']).strip(),
            'breed': request.form.get('breed', pet.get('breed', '')).strip(),
            'age': request.form.get('age', pet.get('age', '')).strip(),
            'weight': request.form.get('weight', pet.get('weight', '')).strip(),
            'color': request.form.get('color', pet.get('color', '')).strip(),
            'gender': request.form.get('gender', pet.get('gender', 'Unknown')),
            'microchip_id': request.form.get('microchip_id', pet.get('microchip_id', '')).strip(),
            'registration_number': request.form.get('registration_number', pet.get('registration_number', '')).strip(),
            'photo_url': request.form.get('photo_url', pet.get('photo_url', '')).strip(),
            'vet_info': request.form.get('vet_info', pet.get('vet_info', '')).strip(),
            'medical_conditions': request.form.get('medical_conditions', pet.get('medical_conditions', '')).strip(),
            'allergies': request.form.get('allergies', pet.get('allergies', '')).strip(),
            'medications': request.form.get('medications', pet.get('medications', '')).strip(),
            'last_checkup_date': last_checkup_date,
            'feeding_schedule': request.form.get('feeding_schedule', pet.get('feeding_schedule', '')).strip(),
            'special_notes': request.form.get('special_notes', pet.get('special_notes', '')).strip(),
            'vaccination_dates': request.form.get('vaccination_dates', pet.get('vaccination_dates', '')).strip()
        }
        
        if Pet.update(pet_id, update_data):
            flash('Pet updated successfully!', 'success')
        else:
            flash('Error updating pet', 'danger')
        
        return redirect(url_for('main.pet_detail', pet_id=pet_id))
    except InvalidId:
        flash('Invalid pet ID', 'danger')
        return redirect(url_for('main.pets_index'))


@main_bp.route('/pets/<pet_id>/delete', methods=['POST'])
def delete_pet(pet_id):
    """Delete a pet"""
    try:
        pet = Pet.get_by_id(pet_id)
        if not pet:
            flash('Pet not found', 'danger')
            return redirect(url_for('main.pets_index'))
        
        if Pet.delete(pet_id):
            flash(f'Pet "{pet["name"]}" deleted successfully!', 'success')
        else:
            flash('Error deleting pet', 'danger')
        
        return redirect(url_for('main.pets_index'))
    except InvalidId:
        flash('Invalid pet ID', 'danger')
        return redirect(url_for('main.pets_index'))


# Inventory Routes
@main_bp.route('/inventory')
def inventory_index():
    """Display list of all inventory items"""
    items = InventoryItem.get_all()
    low_stock_items = [item for item in items if item['is_low_stock']]
    return render_template('main/inventory/index.html', 
                         items=items, 
                         low_stock_count=len(low_stock_items),
                         datetime=datetime,
                         timedelta=timedelta)


@main_bp.route('/inventory/add', methods=['GET', 'POST'])
def add_inventory():
    """Add a new inventory item"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        category = request.form.get('category', 'Other')
        quantity = request.form.get('quantity', '0')
        unit = request.form.get('unit', 'pieces')
        low_stock_threshold = request.form.get('low_stock_threshold', '5')
        price_per_unit = request.form.get('price_per_unit', '0.0')
        supplier = request.form.get('supplier', '').strip()
        usage_notes = request.form.get('usage_notes', '').strip()
        
        # Handle dates
        purchase_date_str = request.form.get('purchase_date', '').strip()
        expiration_date_str = request.form.get('expiration_date', '').strip()
        
        purchase_date = None
        expiration_date = None
        
        if purchase_date_str:
            try:
                purchase_date = datetime.strptime(purchase_date_str, '%Y-%m-%d')
            except ValueError:
                flash('Invalid purchase date format', 'danger')
                return redirect(url_for('main.add_inventory'))
        
        if expiration_date_str:
            try:
                expiration_date = datetime.strptime(expiration_date_str, '%Y-%m-%d')
            except ValueError:
                flash('Invalid expiration date format', 'danger')
                return redirect(url_for('main.add_inventory'))
        
        # Handle for_pets (multiple pets can be selected)
        for_pets = request.form.getlist('for_pets')
        
        # Convert numeric fields
        try:
            quantity = int(quantity)
            low_stock_threshold = int(low_stock_threshold)
            price_per_unit = float(price_per_unit)
        except ValueError:
            flash('Invalid numeric values provided', 'danger')
            return redirect(url_for('main.add_inventory'))
        
        # Validate required fields
        if not name:
            flash('Item name is required', 'danger')
            return redirect(url_for('main.add_inventory'))
        
        # Create the inventory item
        try:
            item_id = InventoryItem.create(name, description, category, quantity, unit,
                                         low_stock_threshold, price_per_unit, supplier,
                                         purchase_date, expiration_date, for_pets, usage_notes)
            flash(f'Inventory item "{name}" added successfully!', 'success')
            return redirect(url_for('main.inventory_detail', item_id=item_id))
        except Exception as e:
            flash(f'Error adding inventory item: {str(e)}', 'danger')
            return redirect(url_for('main.add_inventory'))
    
    # Get pets for the form
    pets = Pet.get_all()
    return render_template('main/inventory/add_inventory.html', 
                         category_options=InventoryItem.CATEGORIES,
                         unit_options=InventoryItem.UNITS,
                         pets=pets)


@main_bp.route('/inventory/<item_id>')
def inventory_detail(item_id):
    """Display inventory item details"""
    try:
        item = InventoryItem.get_by_id(item_id)
        if not item:
            flash('Inventory item not found', 'danger')
            return redirect(url_for('main.inventory_index'))
        
        # Get pets associated with this item  
        associated_pets = []
        if item.get('for_pets'):
            for pet_id in item['for_pets']:
                pet = Pet.get_by_id(pet_id)
                if pet:
                    associated_pets.append(pet)
        
        # Get all pets for updating associations
        all_pets = Pet.get_all()
        
        return render_template('main/inventory/inventory_detail.html', 
                             item=item, 
                             associated_pets=associated_pets,
                             all_pets=all_pets,
                             category_options=InventoryItem.CATEGORIES,
                             unit_options=InventoryItem.UNITS,
                             datetime=datetime)
    except InvalidId:
        flash('Invalid inventory item ID', 'danger')
        return redirect(url_for('main.inventory_index'))


@main_bp.route('/inventory/<item_id>/update', methods=['POST'])
def update_inventory(item_id):
    """Update an inventory item"""
    try:
        item = InventoryItem.get_by_id(item_id)
        if not item:
            flash('Inventory item not found', 'danger')
            return redirect(url_for('main.inventory_index'))
        
        # Handle dates
        purchase_date_str = request.form.get('purchase_date', '').strip()
        expiration_date_str = request.form.get('expiration_date', '').strip()
        
        purchase_date = item.get('purchase_date')
        expiration_date = item.get('expiration_date')
        
        if purchase_date_str:
            try:
                purchase_date = datetime.strptime(purchase_date_str, '%Y-%m-%d')
            except ValueError:
                flash('Invalid purchase date format', 'danger')
                return redirect(url_for('main.inventory_detail', item_id=item_id))
        elif purchase_date_str == '':
            purchase_date = None
            
        if expiration_date_str:
            try:
                expiration_date = datetime.strptime(expiration_date_str, '%Y-%m-%d')
            except ValueError:
                flash('Invalid expiration date format', 'danger')
                return redirect(url_for('main.inventory_detail', item_id=item_id))
        elif expiration_date_str == '':
            expiration_date = None
        
        # Handle for_pets
        for_pets = request.form.getlist('for_pets')
        
        # Convert numeric fields
        try:
            quantity = int(request.form.get('quantity', item['quantity']))
            low_stock_threshold = int(request.form.get('low_stock_threshold', item['low_stock_threshold']))
            price_per_unit = float(request.form.get('price_per_unit', item['price_per_unit']))
        except ValueError:
            flash('Invalid numeric values provided', 'danger')
            return redirect(url_for('main.inventory_detail', item_id=item_id))
        
        update_data = {
            'name': request.form.get('name', item['name']).strip(),
            'description': request.form.get('description', item.get('description', '')).strip(),
            'category': request.form.get('category', item.get('category', 'Other')),
            'quantity': quantity,
            'unit': request.form.get('unit', item.get('unit', 'pieces')),
            'low_stock_threshold': low_stock_threshold,
            'price_per_unit': price_per_unit,
            'supplier': request.form.get('supplier', item.get('supplier', '')).strip(),
            'purchase_date': purchase_date,
            'expiration_date': expiration_date,
            'for_pets': for_pets,
            'usage_notes': request.form.get('usage_notes', item.get('usage_notes', '')).strip()
        }
        
        if InventoryItem.update(item_id, update_data):
            flash('Inventory item updated successfully!', 'success')
        else:
            flash('Error updating inventory item', 'danger')
        
        return redirect(url_for('main.inventory_detail', item_id=item_id))
    except InvalidId:
        flash('Invalid inventory item ID', 'danger')
        return redirect(url_for('main.inventory_index'))


@main_bp.route('/inventory/<item_id>/delete', methods=['POST'])
def delete_inventory(item_id):
    """Delete an inventory item"""
    try:
        item = InventoryItem.get_by_id(item_id)
        if not item:
            flash('Inventory item not found', 'danger')
            return redirect(url_for('main.inventory_index'))
        
        if InventoryItem.delete(item_id):
            flash(f'Inventory item "{item["name"]}" deleted successfully!', 'success')
        else:
            flash('Error deleting inventory item', 'danger')
        
        return redirect(url_for('main.inventory_index'))
    except InvalidId:
        flash('Invalid inventory item ID', 'danger')
        return redirect(url_for('main.inventory_index'))


# Todo Routes
@main_bp.route('/todos')
def todos_index():
    """Display list of all todos with filtering options"""
    status_filter = request.args.get('status')
    priority_filter = request.args.get('priority')
    tag_filter = request.args.get('tag')
    
    todos = Todo.get_all(status_filter=status_filter, priority_filter=priority_filter, tag_filter=tag_filter)
    stats = Todo.get_statistics()
    all_tags = Todo.get_all_tags()
    
    return render_template('main/todos/index.html', 
                         todos=todos,
                         stats=stats,
                         status_filter=status_filter,
                         priority_filter=priority_filter,
                         tag_filter=tag_filter,
                         priorities=Todo.PRIORITIES,
                         statuses=Todo.STATUSES,
                         all_tags=all_tags,
                         datetime=datetime)


@main_bp.route('/todos/add', methods=['GET', 'POST'])
def add_todo():
    """Add a new todo item"""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        priority = request.form.get('priority', 'Medium')
        status = request.form.get('status', 'Todo')
        assigned_to = request.form.get('assigned_to', '').strip()
        tags = request.form.get('tags', '').strip()
        
        # Handle due date
        due_date_str = request.form.get('due_date', '').strip()
        due_date = None
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
            except ValueError:
                flash('Invalid due date format', 'danger')
                return redirect(url_for('main.add_todo'))
        
        # Process tags
        tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()] if tags else []
        
        # Validate required fields
        if not title:
            flash('Todo title is required', 'danger')
            return redirect(url_for('main.add_todo'))
        
        # Create the todo
        try:
            todo_id = Todo.create(title, description, priority, status, due_date, tag_list, assigned_to)
            flash(f'Todo "{title}" added successfully!', 'success')
            return redirect(url_for('main.todo_detail', todo_id=todo_id))
        except Exception as e:
            flash(f'Error adding todo: {str(e)}', 'danger')
            return redirect(url_for('main.add_todo'))
    
    return render_template('main/todos/add_todo.html',
                         priorities=Todo.PRIORITIES,
                         statuses=Todo.STATUSES)


@main_bp.route('/todos/<todo_id>')
def todo_detail(todo_id):
    """Display todo details"""
    try:
        todo = Todo.get_by_id(todo_id)
        if not todo:
            flash('Todo not found', 'danger')
            return redirect(url_for('main.todos_index'))
        
        return render_template('main/todos/todo_detail.html',
                             todo=todo,
                             priorities=Todo.PRIORITIES,
                             statuses=Todo.STATUSES,
                             datetime=datetime)
    except InvalidId:
        flash('Invalid todo ID', 'danger')
        return redirect(url_for('main.todos_index'))


@main_bp.route('/todos/<todo_id>/update', methods=['POST'])
def update_todo(todo_id):
    """Update a todo item"""
    try:
        todo = Todo.get_by_id(todo_id)
        if not todo:
            flash('Todo not found', 'danger')
            return redirect(url_for('main.todos_index'))
        
        # Handle due date
        due_date_str = request.form.get('due_date', '').strip()
        due_date = todo.get('due_date')
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
            except ValueError:
                flash('Invalid due date format', 'danger')
                return redirect(url_for('main.todo_detail', todo_id=todo_id))
        elif due_date_str == '':
            due_date = None
        
        # Process tags
        tags = request.form.get('tags', '')
        tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()] if tags else []
        
        update_data = {
            'title': request.form.get('title', todo['title']).strip(),
            'description': request.form.get('description', todo.get('description', '')).strip(),
            'priority': request.form.get('priority', todo['priority']),
            'status': request.form.get('status', todo['status']),
            'due_date': due_date,
            'tags': tag_list,
            'assigned_to': request.form.get('assigned_to', todo.get('assigned_to', '')).strip()
        }
        
        if Todo.update(todo_id, update_data):
            flash('Todo updated successfully!', 'success')
        else:
            flash('Error updating todo', 'danger')
        
        return redirect(url_for('main.todo_detail', todo_id=todo_id))
    except InvalidId:
        flash('Invalid todo ID', 'danger')
        return redirect(url_for('main.todos_index'))


@main_bp.route('/todos/<todo_id>/delete', methods=['POST'])
def delete_todo(todo_id):
    """Delete a todo item"""
    try:
        todo = Todo.get_by_id(todo_id)
        if not todo:
            flash('Todo not found', 'danger')
            return redirect(url_for('main.todos_index'))
        
        if Todo.delete(todo_id):
            flash(f'Todo "{todo["title"]}" deleted successfully!', 'success')
        else:
            flash('Error deleting todo', 'danger')
        
        return redirect(url_for('main.todos_index'))
    except InvalidId:
        flash('Invalid todo ID', 'danger')
        return redirect(url_for('main.todos_index'))


@main_bp.route('/todos/<todo_id>/quick-update', methods=['POST'])
def quick_update_todo(todo_id):
    """Quick update todo status from list view"""
    try:
        todo = Todo.get_by_id(todo_id)
        if not todo:
            flash('Todo not found', 'danger')
            return redirect(url_for('main.todos_index'))
        
        new_status = request.form.get('status', todo['status'])
        
        update_data = {'status': new_status}
        
        if Todo.update(todo_id, update_data):
            flash(f'Todo status updated to {new_status}!', 'success')
        else:
            flash('Error updating todo status', 'danger')
        
        return redirect(url_for('main.todos_index'))
    except InvalidId:
        flash('Invalid todo ID', 'danger')
        return redirect(url_for('main.todos_index'))

from flask import send_from_directory, current_app, abort
import os
from pathlib import Path
from datetime import datetime

@media_bp.route('/media/')
@media_bp.route('/media/<path:subpath>')
def media_browser(subpath=''):
    """Browse media files and directories"""
    media_root = Path('/app/main/media_files')
    current_path = media_root / subpath
    
    # Security check: ensure we're not going outside media_root
    try:
        current_path = current_path.resolve()
        if not str(current_path).startswith(str(media_root)):
            abort(403)
    except:
        abort(404)
    
    if not current_path.exists():
        abort(404)
    
    if current_path.is_file():
        # If it's a file, serve it
        directory = str(current_path.parent.relative_to(media_root))
        if directory == '.':
            directory = ''
        return send_from_directory(str(current_path.parent), current_path.name)
    
    # It's a directory, list contents
    items = []
    for item in sorted(current_path.iterdir()):
        relative_path = item.relative_to(media_root)
        
        if item.is_file():
            stat = item.stat()
            items.append({
                'name': item.name,
                'path': str(relative_path).replace('\\', '/'),
                'is_dir': False,
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime),
                'extension': item.suffix.lower()
            })
        else:
            items.append({
                'name': item.name,
                'path': str(relative_path).replace('\\', '/'),
                'is_dir': True,
                'size': None,
                'modified': None,
                'extension': None
            })
    
    # Create breadcrumb navigation
    breadcrumbs = []
    if subpath:
        parts = subpath.split('/')
        for i, part in enumerate(parts):
            breadcrumbs.append({
                'name': part,
                'path': '/'.join(parts[:i+1])
            })
    
    return render_template('main/media_browser.html',
                         items=items,
                         current_path=subpath,
                         breadcrumbs=breadcrumbs)

@media_bp.route('/media/<path:filename>')
def serve_image(filename):
    media_root = Path('/app/main/media_files')
    file_path = media_root / filename
    
    # Security check
    try:
        file_path = file_path.resolve()
        if not str(file_path).startswith(str(media_root)):
            abort(403)
    except:
        abort(404)
    
    if not file_path.exists() or not file_path.is_file():
        abort(404)
    
    return send_from_directory(str(file_path.parent), file_path.name)
