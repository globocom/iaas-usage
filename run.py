from app import app as application

if __name__ == "__main__":
    application.run(port=application.config['SERVER_PORT'])
