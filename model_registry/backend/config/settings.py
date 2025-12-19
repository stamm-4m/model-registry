import os

ENV = os.getenv('ENV', 'development')
DEBUG = ENV == 'development'
PORT = int(os.getenv('PORT', 8050))
