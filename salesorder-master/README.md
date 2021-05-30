# Entity Extractor
The code base is use to extract information from a text document. The NLP machine learning model is built using flair framework .

The below folders has approperiate script which helps to invoke the model and extract entities
## flair_model
* the folder contains the AWS SageMaker(SM) service related script which use to run the model once deployed into SM service (For ref, https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-dg.pdf)
    * nginx.config - contains nginx web server related configurations
    * predictor.py - the script will load the ML model and extract entities/informat
    * serve - it starts nginx and gunicorn with the correct configurations
    * train - use to train model in AWS instance
    * wsgi.py - this will starts the flask application 

## app
* the folder contains flask application script which use to invoke the SM model from the captain container    
    * templates - the folder contains the index page html tags    
    * server.py - contains ML invocation and token based accessibilty script
    * utils.py - contains utility functions to perform invocation operations like remove special chars from given request text
    * entrypoint.sh - the shell script starts the gunicorn service    
    * wsgi.py - this will starts the flask application 

* .captain.yml - the captain yaml file helps to configure the application name, DNS and SM model data URL 
- .drone.yml - the drone yaml file helps to configure drone in order to build and deploy the application in captain container
- Dockerfile - specify the docker base image and install required packages. This will deploy the "app" folder flask application 
- SM.Dockerfile - specify the docker base image and deploy it into AWS SM as hosting service
- requirements.txt - contains list of packages which require to run the application
