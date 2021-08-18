import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database


# TODO IMPLEMENT DATABASE URL
host = "velda-sandbox.postgres.database.azure.com"
dbname = "fyyur"
user = "velda_admin@velda-sandbox"
password = "" # get from azure
sslmode = "require"
port = '5432'

# Please change your password as necessary
# user = "postgres"
# password = "xyz"
# host = "localhost"
# port = '5432'
# dbname = "fyyur"
SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://{}:{}@{}:{}/{}?sslmode=require".format(user, password, host, port, dbname)

