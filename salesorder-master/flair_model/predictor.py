
# This is the file that implements a flask server to do inferences. It's the file that you will modify to
# implement the scoring for your own algorithm.

from __future__ import print_function

import os
import json
import sys
import signal
import traceback
from flask import Flask,jsonify,request
import requests
import json
from flair.data import Sentence
from flair.models import SequenceTagger
import flask
import boto3

import flair, torch
#flair.device = torch.device('cuda:0')

prefix = ''
model_path='/opt/ml/model'

# A singleton for holding the model. This simply loads the model and holds it.
# It has a predict function that does a prediction based on the model and the input data.

class ScoringService(object):
    model = None                # Where we keep the model when it's loaded    

    @classmethod
    def get_model(cls):
        """Get the model object for this instance, loading it if it's not already loaded."""
        if cls.model == None:                       
            model = SequenceTagger.load(os.path.join(model_path,'best-model.pt'))
            print('model loaded')
        return model 

    @classmethod
    def predict(cls, input):
        """For the input, do the predictions and return them.
        Args:
            input (a pandas dataframe): The data on which to do the predictions. There will be
                one prediction per row in the dataframe"""
        clf =cls.get_model()
        print(clf)
        s = Sentence(input)
        print(clf.predict(s))
        print(s.to_dict(tag_type='ner'))
        #return json.dumps(s.to_dict(tag_type='ner'))
        return s.to_dict(tag_type='ner')

# The flask app for serving predictions
app = flask.Flask(__name__)

@app.route('/ping', methods=['GET'])
def ping():
    """Determine if the container is working and healthy. In this sample container, we declare
    it healthy if we can load the model successfully."""
    #health = ScoringService.get_model() is not None  # You can insert a health check here
    #status = 200 if health else 404
    #return flask.Response(response='Sales Order Flair Model app is running!', status=status, mimetype='application/json')
    app.logger.info("Processing ping request")
    return flask.Response(response='Sales Order Flair Model app is running!', status=200, mimetype='application/json')

@app.route('/invocations', methods=['POST'])
def transformation():
    """Do an inference on a single batch of data. In this sample server, we take data as CSV, convert
    it to a pandas data frame for internal use and then convert the predictions back to CSV (which really
    just means one prediction per line, since there's a single column.
    """   
    app.logger.info("Processing invication request")
    if flask.request.content_type == 'application/json':
        data = None
        data = request.json
        try:
            # Do the prediction            
            predictions = ScoringService.predict(data["text"])                        
            entities = predictions['entities']            
            temp =predictions
            tex = temp['text']
            entlist=[]
            bilouentity=[]
            i=0
            for ent in entities:
                i+=1                
                entSplit = ent['type'].split("-")
                if(len(entSplit)==1 or entSplit[0]=='B'):
                    bilouentity.append(ent)                    
                elif(entSplit[0]=='I'):
                    bilouentity.append(ent)
                elif entSplit[0]=='L':
                    bilouentity.append(ent)                    
                    bilouentity[0]['end_pos']=ent['end_pos']
                    text = ""
                    bilouentity[0]['text']=tex[bilouentity[0]['start_pos']:bilouentity[0]['end_pos']]
                    bilouentity[0]['type']= entSplit[1]
                    temp = list(bilouentity[0])                    
                    entlist.append(bilouentity[0])            
                    bilouentity=[]                    
                elif(entSplit[0]=='U'):                    
                    if( len(bilouentity) ==1):
                        entlist.append(bilouentity[0])
                    bilouentity=[]
                    ent['type']=entSplit[1]
                    entlist.append(ent)
            predictions['entities']=entlist        
            resp = json.dumps(predictions)
            return flask.Response(response=resp, status=200, mimetype='application/json')
        except Exception as e:
            app.logger.error("An error is occured while processing invocation request {}".format(e))
            return flask.Response(response=str(e), status=500, mimetype='text/plain')
    else:
        return flask.Response(response='This predictor only supports JSON data', status=415, mimetype='text/plain')   
