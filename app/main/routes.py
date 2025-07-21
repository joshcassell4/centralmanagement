from flask import render_template, request, redirect, url_for, flash
from app.main import main_bp
from app.models.mongo_models import Application, Task
from bson.errors import InvalidId

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
            app_id = Application.create(name, description, repo_url, tag_list, notes)
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
    
    # Calculate overall statistics
    total_apps = len(applications)
    total_tasks = sum(app['total_tasks'] for app in applications)
    completed_tasks = sum(app['completed_tasks'] for app in applications)
    
    # Calculate overall completion percentage
    overall_completion = (
        round((completed_tasks / total_tasks) * 100) 
        if total_tasks > 0 else 0
    )
    
    # Sort applications by different criteria
    most_active = sorted(applications, 
                        key=lambda x: x.get('updated_at', x.get('created_at')), 
                        reverse=True)[:5]
    
    return render_template('main/dashboard.html',
                         applications=applications,
                         total_apps=total_apps,
                         total_tasks=total_tasks,
                         completed_tasks=completed_tasks,
                         overall_completion=overall_completion,
                         most_active=most_active)