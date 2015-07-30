                                # Get an s3 object from specified bucket and key
                                print "Getting source object from S3"
                                conn = boto.connect_s3()
                                # define source_bucket and connect to it
                                source_bucket="mybucket"
                                b = conn.get_bucket(source_bucket)
                                k = boto.s3.key.Key(b)
                                # get contents of provided key to file
                                source_key="mykey"
                                k.key = source_key
                                k.get_contents_to_filename('/tmp/object')

                                print "Invok executable"
                                cmd = 'md5sum /tmp/object'
                                process = subprocess.Popen(cmd,shell=True,stdout = subprocess.PIPE, stderr = subprocess.PIPE)
                                process_out,process_err = process.communicate()
                                rc = process.returncode
                                if (rc != 0):
                                        print "nonzero exit code from cmdline process"
                                        return Response("Command Line Process Returned Nonzero Code", status=500)


	            		# post output to s3 object
	                        print "placing output at s3 destination"
                                output_text="some-text"
                                dest_bucket="some-bucket"
				b = conn.get_bucket(dest_bucket)
				k = boto.s3.key.Key(b)
                                dest_key_prefix="some-keypath"
                                dest_key_suffix="suffix"
				k.key = "{0}/{1}.txt".format(dest_key_prefix, dest_key_suffix))
				k.set_contents_from_string(output_text)
