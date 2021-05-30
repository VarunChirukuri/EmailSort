#!/bin/sh

cd /opt/program

#!/bin/sh
exec gunicorn -b 0.0.0.0:8080 wsgi:app
