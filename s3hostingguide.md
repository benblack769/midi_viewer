Static file hosting with s3:

Set for static website hosting.
https://docs.aws.amazon.com/AmazonS3/latest/dev/EnableWebsiteHosting.html

Bucket permissions:
https://docs.aws.amazon.com/AmazonS3/latest/dev/WebsiteAccessPermissionsReqd.html

{
  "Version":"2012-10-17",
  "Statement":[{
	"Sid":"PublicReadGetObject",
        "Effect":"Allow",
	  "Principal": "*",
      "Action":["s3:GetObject"],
      "Resource":["arn:aws:s3:::example-bucket/*"
      ]
    }
  ]
}

To upload files to website:

install aws command line tools:

	sudo apt install awscli

initialize credentials:

	aws credentials

Copy all files:

	aws s3 sync <local_folder> s3://<bucket_name>/<s3_folder>
