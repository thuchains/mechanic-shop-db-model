#Application Factory Pattern
from flask import Flask
from .models import db
from .extensions import ma, limiter, cache
from .blueprints.customers import customers_bp
from .blueprints.mechanics import mechanics_bp
from .blueprints.service_tickets import service_tickets_bp



def create_app(config_name): #Defines a factory function >> creates and returns a Flask app
    app = Flask(__name__) #Creates Flask app instance
    app.config.from_object(f"config.{config_name}")

    db.init_app(app)
    ma.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)

    
    #register blueprints
    app.register_blueprint(customers_bp, url_prefix='/customers')
    app.register_blueprint(mechanics_bp, url_prefix='/mechanics')
    app.register_blueprint(service_tickets_bp, url_prefix='/service_tickets')

    limiter.init_app(app)
    cache.init_app(app)


    return app