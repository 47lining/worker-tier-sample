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
        - S3_Input_Bucket
        - S3_Input_Key
        - S3_Output_Bucket
        - S3_Output_Prefix

        actions:
        - locally materialize S3 object referenced in "S3_Input_Bucket" and "S3_Input_Key" accessor
        - run local process to compute MD5 Checksum for object
        - Post Checksum Result to output object at S3 path specified by "S3_Output_Bucket" and "S3_Output_Prefix" combined with basename of "S3_Input_Key"

        example:
        - S3_Input_Bucket "tdw-inputs"
        - S3_Input_Key "poc/test1"
        - S3_Output_Bucket "tdw-outputs"
        - S3_Output_Prefix "poc"

        produces "tdw-outputs/poc/test1"
        
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
                        if not request.json.has_key('S3_Input_Bucket') or not request.json.has_key('S3_Input_Key') or not request.json.has_key('S3_Output_Bucket') or not request.json.has_key('S3_Output_Prefix'):
                                response = Response("Malformed Request", status=500)
                        else:
                                S3_Input_Bucket = request.json["S3_Input_Bucket"]
                                S3_Input_Key = request.json["S3_Input_Key"]
                                S3_Output_Bucket = request.json["S3_Output_Bucket"]
                                S3_Output_Prefix = request.json["S3_Output_Prefix"]

                                print "S3_Input_Bucket", S3_Input_Bucket
                                print "S3_Input_Key", S3_Input_Key
                                print "S3_Output_Bucket", S3_Output_Bucket
                                print "S3_Output_Prefix", S3_Output_Prefix

                                # Process the work

                                # Get an s3 object from specified bucket and key
                                print "Getting source object from S3"
                                conn = boto.connect_s3()
                                # define source_bucket and connect to it
                                b = conn.get_bucket(S3_Input_Bucket)
                                k = boto.s3.key.Key(b)
                                # get contents of provided key to file
                                k.key = S3_Input_Key
                                k.get_contents_to_filename('/tmp/object')

                                print "Compute MD5 Checksum using local process"
                                cmd = 'md5sum /tmp/object'
                                process = subprocess.Popen(cmd,shell=True,stdout = subprocess.PIPE, stderr = subprocess.PIPE)
                                process_out,process_err = process.communicate()
                                rc = process.returncode
                                if (rc != 0):
                                        print "nonzero exit code from cmdline process"
                                        return Response("Command Line Process Returned Nonzero Code", status=500)

	            		# post output to s3 object
	                        print "placing output at s3 destination"
                                dest_bucket="some-bucket"
				b = conn.get_bucket(S3_Output_Bucket)
				k = boto.s3.key.Key(b)
                                dest_key_prefix=S3_Output_Prefix
                                dest_key_suffix=os.path.basename(S3_Input_Key)
				k.key = "{0}/{1}.txt".format(dest_key_prefix, dest_key_suffix)
				k.set_contents_from_string(process_out)

	                        print "returning OK status"
	            		response = Response("", status=200)

                except Exception as ex:
                        print "received exception"
                        logging.exception('Error processing message: %s' % request.json)
                        response = Response(ex.message, status=500)

        return response

if __name__ == '__main__':
	application.run(host='0.0.0.0')
