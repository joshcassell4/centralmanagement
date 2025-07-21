#!/usr/bin/env python
"""
Development server runner for the Central Application Management Dashboard
"""
from app import create_app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)