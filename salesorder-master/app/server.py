import flask
from flask import Flask, jsonify, request
import os
import boto3
import logging
import json
import re
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity,
    jwt_refresh_token_required, create_refresh_token, )
import datetime
import yaml

from utils import pre_processing, remove_special_chars, post_processing

log = logging.getLogger(__name__)

def create_app(config_yml):
    app = Flask(__name__, instance_relative_config=True)
    config_yml = config_yml

    app.config['JWT_SECRET_KEY'] = config_yml["app"]["secret_key"]
    jwt = JWTManager(app)  # intialize JWT to create token key
    log.info("Booting the application")

    # initialize the SageMaker service to access the deployed model configuration
    def initialize_aws():
        """
            Initialize the AWS client
        """
        log.info("Initialize the AWS client")
        runtime = None
        try:
            runtime = boto3.client(config_yml["AWS"]["SM"]["service"], region_name=config_yml["AWS"]["SM"]["region"])
        except Exception as exp:
            log.error("An error is occured while initialize the AWS client service {}".format(exp))

        return runtime

    def invoke_aws_sm(payload):
        """
            Invoke SM endpoint to extract the entities
        """
        isSuccess = True
        _model_resp = None
        try:
            runtime = initialize_aws()
            # get the name of SM endpoint which is available from the kubernet environment variable
            _endpoint_name = os.environ[config_yml["AWS"]["SM"]["endpoint"]]
            # Retry to connect the AWS client service
            if runtime is None:
                initialize_aws()
            _model_resp = runtime.invoke_endpoint(EndpointName=_endpoint_name, ContentType=config_yml["app"]["content_type"], Body=json.dumps(payload))
        except Exception as exp:   
            isSuccess = False
            log.error("An error is occured while processing invocation request {}".format(exp))        
        
        return isSuccess, _model_resp
    
    @app.route("/")
    def index():
        return "The ML model will extract entities from a document. The ML model is built using Flair NLP framework" 
    
    @app.route("/health")
    def health():
        log.info("Processing healthcheck request")
        return jsonify("healthy")

    @app.route('/login', methods=['POST'])
    def login():
        username = request.json.get('username', None)
        password = request.json.get('password', None)
        if username != config_yml["app"]["login_user"] or password != config_yml["app"]["login_pwd"]:
            return jsonify({"msg": "Bad username or password"}), 401
        # We can now pass this complex object directly to the
        # create_access_token method. This will allow us to access the
        # properties of this object in the user_claims_loader function,
        # and get the identity of this object from the
        # user_identity_loader function.
        access_token = create_access_token(identity=username, fresh=True)
        refresh_token = create_refresh_token(username)
        return {
            'access_token': access_token,
            'refresh_token': refresh_token
        }, 200

    @app.route('/refresh', methods=['POST'])
    @jwt_refresh_token_required
    def refresh():
        """
            To create refersh token in order to post the data securely
        """
        current_user = get_jwt_identity()
        expires = datetime.timedelta(days=1)
        ret = {
            'access_token': create_access_token(identity=current_user, expires_delta=expires)
        }
        return jsonify(ret), 200

    @app.route('/invocations', methods=['POST'])
    @jwt_required
    def transformation():
        """Do an inference on a setence.
        """        
        try:
            # the api should accept json as input type
            if flask.request.content_type == config_yml["app"]["content_type"]:
                data = None
                #print("*******************")
                #print("request {}".format(request))
                data = request.json
                log.info("requested data {}".format(data))
                #print("requested data {}".format(data))
                _file_content = remove_special_chars(data["text"])
                #print("after special chars removed data {}".format(_file_content))
                # replace newline in order to convert into a single line
                _text = pre_processing(_file_content)
                _text = _text.replace("\n", " ").replace("\n\n", " ")
                _payload = {"text": _text}
                _filename = data["filename"]
                _customername = data["customername"]
                _batch = data["batch"]
                
                # call SM endpoint
                isSuccess, _model_resp = invoke_aws_sm(_payload)
                # retry to invoke the endpoint if getting any error (possible error is "unable to locate credentials") 
                # zenhub issue #55
                if not isSuccess:
                    return flask.Response(response='Unable to connect SageMaker endpoint. Please contact admin', status=400, mimetype='text/plain')    
                    
                log.info("ML model response {}".format(_model_resp))
                #print("ML model response {}".format(_model_resp))
                #print("After AWS SM call")
                #print("*******************")
                if _model_resp:
                    #print("Before model resp decode")
                    _predicted_entities = json.loads(
                        _model_resp['Body'].read().decode())
                    #_hil_format_entities = convert_prediction_result_to_hil_format(_predicted_entities, _file_content, _batch, _filename)

                    #resp_entity = json.dumps(_hil_format_entities)
                    #print("After model resp decode")
                    _predicted_entities = post_processing(_predicted_entities)
                    _predicted_entities["text"] = _file_content
                    _predicted_entities["filename"] = _filename
                    _predicted_entities["customername"] = _customername
                    _predicted_entities["batch"] = _batch
                    resp_entity = json.dumps(_predicted_entities)
                    return flask.Response(response=resp_entity, status=200, mimetype=config_yml["app"]["content_type"])
                else:
                    return flask.Response(response="NO entities extracted by the Model", status=200, mimetype=config_yml["app"]["content_type"])
            else:
                return flask.Response(response='This predictor only supports JSON data', status=415, mimetype='text/plain')
        except Exception as e:
            #print("An error is occured while processing invocation {}".format(e))
            log.error(
                "An error is occured while processing invocation request {}".format(e))
            return flask.Response(response='Error Occured {}'.format(e), status=300, mimetype='text/plain')    
    
    return app
