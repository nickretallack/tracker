import settings

def s3_save(file,record_id):
  from urllib import urlopen
  from lib import S3
  s3 = S3.AWSAuthConnection(settings.aws_key, settings.aws_secret)
  data = file.value
  #mime = data.info()
  sendable = S3.S3Object(data) # could set metadata here
  headers = {'x-amz-acl':'public-read', 'Content-Type': "image/png"}
  # quoted_url = quote(url.split('?',1)[0]) # remove query so it has a clean file extension on the end
  url = "%s/%s" % (record_id, file.filename)
  s3url = s3_url(url)
  s3.put(settings.s3_bucket, url, sendable, headers).message, s3url
  return s3url
  
def s3_url(url):
  host = "http://s3.amazonaws.com"
  return "%s/%s/%s" % (host, settings.s3_bucket, url)

def s3_get_url(id,filename):
  return s3_url("%s/%s" % (id,filename))