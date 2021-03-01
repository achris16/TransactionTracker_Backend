"""
appserver.py
- creates an application instance and runs the dev server
"""

if __name__ == '__main__':
    from app import create_app
    app = create_app()
    app.run()

