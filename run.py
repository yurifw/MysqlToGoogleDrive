#!/usr/bin/env python3

import boto3
import os
import argparse
import json
import subprocess
from datetime import datetime

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Dumps a mysql database to a'\
								'file, zips it and uploads it to Google Drive.')
	parser.add_argument('-c', '--config', required=False, help='path to a config file')
	parser.add_argument('-d', '--database', required=False, help='database name')
	parser.add_argument('-u', '--user', required=False, help='mysqldump user')
	parser.add_argument('-p', '--password', required=False, help='mysqldump password')
	parser.add_argument('-o', '--output', required=False, default='',
	 										help='output path for dump file')
	parser.add_argument('-r', '--prefix', required=False, default='',
												help='prefix for dumpfile name')
	parser.add_argument('-z', '--zip-password', required=False, default='',
												help='password to the file')
	parser.add_argument('-s', '--s3-credentials', required=False,
											help='path to the AWS access key')
	parser.add_argument('-b', '--bucket', required=False,
											help='S3 bucket to receive the file')
	parser.add_argument('-f', '--folder', required=False, default='',
							help='path of the destination folder in your bucket')
	parser.add_argument('-k', '--keep', action='store_true', default=False,
							help='if passed, keeps the compressed file')


	dump_command = "mysqldump --databases {database} --user {user} -p{pwd}" \
											"--add-drop-database > {output}"

	args = parser.parse_args()
	config = {}
	if args.config is not None:
		with open(args.config, 'r') as f:
			config = json.loads(f.read())
	else:
		for key in vars(args):
			config[key] = getattr(args, key)

	timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
	file_name = '%s%sdump.sql' % (config['prefix'], timestamp)
	file_path = os.path.join(config['output'], file_name)

	cmd = dump_command.format(database = config['database'],
								user = config['user'],
								pwd=config['password'],
								output=file_path)


	process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
	process.wait()
	zip_command = "zip -D %s.zip %s" % (file_path, file_path)
	pwd_comand = '' if len(config['zip_password'])<1 else ' -p%s' % config['zip_password']
	zipped_file = "%s.7z" % file_path
	zip_command = "7z a%s %s %s" % (pwd_comand, zipped_file, file_path)
	process = subprocess.Popen(zip_command, shell=True, stdout=subprocess.PIPE)
	process.wait()
	process = subprocess.Popen("rm %s" % file_path, shell=True, stdout=subprocess.PIPE)
	process.wait()

	access_key = ''
	secret_key = ''
	with open(config['s3_credentials'], 'r') as c:
		l =c.readlines()
		access_key = l[0].strip().split('=')[1]
		secret_key = l[1].strip().split('=')[1]
	s3 = boto3.client('s3', aws_access_key_id=access_key,
                      aws_secret_access_key=secret_key)

	s3_name = os.path.join(config['folder'], zipped_file.split(os.path.sep)[-1])
	s3.upload_file(zipped_file, config['bucket'], s3_name)

	if not config['keep']:
		process = subprocess.Popen("rm %s" % zipped_file, shell=True, stdout=subprocess.PIPE)
		process.wait()
