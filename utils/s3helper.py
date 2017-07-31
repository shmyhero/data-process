import boto3


class S3(object):

    @staticmethod
    def list_all_buckets():
        s3 = boto3.resource('s3')
        for bucket in s3.buckets.all():
            yield bucket

    def __init__(self, bucket_name):
        s3 = boto3.resource('s3')
        self.bucket = s3.Bucket(name = bucket_name)

    def list_objects(self):
        for obj in self.bucket.objects.all():
            yield obj.key

    def upload_file(self, file_path, key):
        """
        upload file to s3
        usage sample: upload_file('/Users/tradehero/Documents/sql.sql', 'da/raw/sql.sql')
        :param file_path:
        :param key:
        :return:
        """
        data = open(file_path, 'rb')
        self.bucket.put_object(Key = key, Body=data)

    def download_file(self, key, local_file_path):
        """
        usage sample: download_file('da/raw/sql2.sql', '/Users/tradehero/Documents/sql2.sql')
        :param key:
        :param local_file_path:
        :return:
        """
        self.bucket.download_file(key, local_file_path)


#if __name__ =='__main__':
#    from common.configmgr import ConfigMgr
#    s3 = S3(ConfigMgr.get_s3_config()['bucket'])
    #print list(s3.list_objects())
    #s3.upload_file('/Users/tradehero/python-projects/data-process/data/2017-07-19.zip', 'da/raw/2017-07-19.zip')



