# config.py

import os

class Config:
    # Base configuration that applies to all environments
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    # Configuration specific to local development (e.g., SQLite)
    DEBUG = True
    # For SQLite:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///data.db'

class ProductionConfig(Config):
    # Configuration specific to a production environment (e.g., SQL Server)
    DEBUG = False # Never run with DEBUG=True in production!
    # For SQL Server (Windows Authentication Example):
   
   #SQLALCHEMY_DATABASE_URI = (
   #     r'mssql+pyodbc:///?odbc_connect='
   #     r'DRIVER={ODBC Driver 17 for SQL Server};'
   #     r'SERVER=host.docker.internal;' # e.g., 'localhost\SQLEXPRESS'
   #    r'DATABASE=DrinkServiceDB;'
   #     r'trusted_connection=yes;'
   #)
    

    # Or for SQL Server (SQL Server Authentication Example):
    #SQLALCHEMY_DATABASE_URI = (
    #     'mssql+pyodbc://flask_user:StrongPassword123@localhost/DrinkServiceDB?'
    #     'driver=ODBC+Driver+17+for+SQL+Server'
    #)


    SQLALCHEMY_DATABASE_URI = (
        'mssql+pyodbc://flask_user:StrongPassword123@host.docker.internal,1433/DrinkServiceDB?'
        'driver=ODBC+Driver+17+for+SQL+Server'
    )



# Dictionary to map environment names to their respective configurations
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    # Add other environments like 'testing' if needed
}