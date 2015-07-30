# Copyright 2013. Amazon Web Services, Inc. All Rights Reserved.
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import json
import subprocess

import flask
from flask import request, Response

import boto
import os

# Create and configure the Flask app
application = flask.Flask(__name__)
application.config.from_object('default_config')
application.debug = application.config['FLASK_DEBUG'] in ['true', 'True']
application.debug = True

version = "v1"
print "startup application-poc " + version

@application.route('/poc', methods=['POST'])
def process_poc():
	"""
        Template for worker instance processing

        inputs:
        - contained in json

        actions:
        - to be taken by worker
	"""

        print "in process_poc " + version
        print "received headers:"
        print request.headers
        print "received data:"
        print request.data
	response = None

        try:
                json_value=request.json
        except Exception as ex:
                print "received exception attempting to access json request"
                logging.exception('Exception message: %s' % ex.message)
                raise ex
                
   	if json_value is None:
                print "No JSON Request Found"
		# Expect application/json request
		response = Response("", status=415)
	else:
		message = dict()
                print "found JSON: ", request.json

                try:
                        # process input parameters
                        if not request.json.has_key('key1') or	not request.json.has_key('key2') or not request.json.has_key('key3') or not request.json.has_key('key4'):
                                response = Response("Malformed Request", status=500)
                        else:
                                key1 = request.json["key1"]
                                key2 = request.json["key2"]
                                key3 = request.json["key3"]
                                key4 = request.json["key4"]

                                print "key1", key1
                                print "key2", key2
                                print "key3", key3
                                print "key4", key4

                                # Process the work


	                        print "returning OK status"
	            		response = Response("", status=200)

                except Exception as ex:
                        print "received exception"
                        logging.exception('Error processing message: %s' % request.json)
                        response = Response(ex.message, status=500)

        return response

if __name__ == '__main__':
	application.run(host='0.0.0.0')
