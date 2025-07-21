from flask import Blueprint

# Create the main blueprint
main_bp = Blueprint('main', __name__, template_folder='templates')

# Import routes at the end to avoid circular imports
from app.main import routes