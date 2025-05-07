# Main app package initialization

def create_app(config=None):
    """
    Application factory function that creates and configures the Flask app.
    Only imported when needed for the web API component.
    
    Args:
        config: Configuration object or string pointing to a configuration file
        
    Returns:
        Configured Flask application instance
    """
    try:
        from flask import Flask
    except ImportError:
        return None  # Flask not installed, return None
        
    app = Flask(__name__)
    
    # Load default configuration
    app.config.from_object('app.config.default')
    
    # Load environment specific configuration
    if config:
        if isinstance(config, str):
            app.config.from_pyfile(config)
        else:
            app.config.from_object(config)
    
    # Register blueprints
    # from app.views import main_bp
    # app.register_blueprint(main_bp)
    
    # Initialize extensions
    # db.init_app(app)
    # migrate.init_app(app, db)
    
    return app
