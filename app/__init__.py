from flask import Flask
from flask_pymongo import PyMongo
from dotenv import load_dotenv
import os

# Initialize extensions
mongo = PyMongo()

def create_app():
    """Create and configure the Flask application"""
    # Load environment variables
    load_dotenv()
    
    # Create Flask app
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['MONGO_URI'] = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/app_management')
    
    # Initialize extensions with app
    mongo.init_app(app)
    
    # Register blueprints
    from app.main import main_bp, media_bp  
    app.register_blueprint(main_bp)
    app.register_blueprint(media_bp)    
    
    # Custom template filters
    @app.template_filter('format_file_size')
    def format_file_size_filter(size):
        """Format file size in human readable format"""
        if size is None:
            return ''
        if size == 0:
            return '0 B'
        
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        unit_index = 0
        size = float(size)
        
        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1
        
        if unit_index == 0:
            return f'{int(size)} {units[unit_index]}'
        else:
            return f'{size:.2f} {units[unit_index]}'
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return render_template('errors/500.html'), 500
    
    return app

# Import at the end to avoid circular imports
from flask import render_template