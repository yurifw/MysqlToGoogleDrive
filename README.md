# MysqlToS3
Dumps a mysql database to a file, zips it and uploads it to your AWS S3 Bucket

## How to get your AWS credentials
* Log in to your AWS Management Console
* Click on your username at the top-right of the page to open the drop-down menu
* Click on 'My Security Credentials'
* Click on 'Dashboard' on the left side of the page
* Click on 'My Access Keys' on the right side of the page
* Create a new Access Key
* Download it and pass it to the script

## Requirements
* python 3
* 7zip
* boto3 (installed through pip)
