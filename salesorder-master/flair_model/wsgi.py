import predictor as myapp
import logging

# This is just a simple wrapper for gunicorn to find your app.
# If you want to change the algorithm file, simply change "predictor" above to the
# new file.

app = myapp.app

logging.basicConfig(level=logging.DEBUG)


