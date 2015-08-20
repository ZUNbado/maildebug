from main import app as application

application.config.from_object('config.ProductionConfig')
