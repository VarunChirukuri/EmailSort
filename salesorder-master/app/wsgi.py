import os
import logging
import yaml
import sys

from server import create_app

config_yml = yaml.load(
    open(os.path.join(os.getcwd(), "config.yml")), Loader=yaml.FullLoader)
app = create_app(config_yml)

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
log = logging.getLogger(__name__)
log.level = logging.INFO

if __name__ == "__main__":
    app.run(debug=True)
