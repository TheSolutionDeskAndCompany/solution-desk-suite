import logging
from app import create_app

# Configure logging for debugging
logging.basicConfig(level=logging.DEBUG)

app = create_app()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
