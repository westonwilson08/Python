#############################################
#                                           #
############### Version 1_5 #################
#                                           #
#############################################

#This script is intended to ingest VPC Flow logs, decorate them, and forward them to a centralized AWS account. 
import boto3,logging,json,gzip,urllib,time,os,geocoder,ipaddress
from StringIO import StringIO

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client('s3')
ec2 = boto3.client('ec2')
security_groups = ec2.describe_security_groups()
interfaces = ec2.describe_network_interfaces()
#print(security_groups)
#print(interfaces)
ec2.meta.events._unique_id_handlers['retry-config-ec2']['handler']._checker.__dict__['_max_attempts'] = 10
def lambda_handler(event, context):
    #print event
    #set the name of the S3 bucket
    bucketS3 = os.environ['account_number']+"-"+os.environ['bucket_region']+"-"+"flowlogs"
    folderS3 = 'AWSLogs'
    prefixS3 = 'flowlogs_'
    now = time.localtime(time.time())
    info = ''
    #capture the CloudWatch log data
    outEvent = str(event['awslogs']['data'])
    #decode and unzip the log data
    outEvent = gzip.GzipFile(fileobj=StringIO(outEvent.decode('base64','strict'))).read()
    #convert the log data from JSON into a dictionary
    cleanEvent = json.loads(outEvent)
    #print(cleanEvent)
    #create a temp file
    tempFile = open('/tmp/file', 'w+')
    parsedTime = str(now[0]) + "-" + str(now[1]) + "-" + str(now[2]) + "_" + str(now[3])+ str(now[4]) + str(now[5])
    #Create the S3 file key
    key = folderS3 + '/' + prefixS3 + parsedTime + ".log"
    #loop through the events line by line
    for t in cleanEvent['logEvents']:
        #Transform the data and store it in the temp file.
        info = ("CEF:0|AWS CloudWatch|FlowLogs|1.0|acct=" + str(t['extractedFields']['account_id']) + "|src=" + str(t['extractedFields']['srcaddr']) + "|spt=" + str(t['extractedFields']['srcport']) + "|dst=" + str(t['extractedFields']['dstaddr']) + "|dpt=" + str(t['extractedFields']['dstport'])+ "|proto=" + str(t['extractedFields']['protocol'])+ "|start=" + str(t['extractedFields']['start'])+ "|end=" + str(t['extractedFields']['end'])+ "|out=" + str(t['extractedFields']['bytes']) + "|action=" + str(t['extractedFields']['action']) + "|status=" + str(t['extractedFields']['log_status']))
        #Check for public IP addresses
        if (ipaddress.ip_address(t['extractedFields']['srcaddr']).is_global):
            g = geocoder.ip(t['extractedFields']['srcaddr'])
            info += "|country=" + str(g.country)+"|city=" + str(g.city)+"|lat/lng=" + str(g.latlng)+"\n"
        else:
            info += "|country=NA|city=NA|lat/lng=NA"
        #Check matched Security Group
        if (str(t['extractedFields']['action']).lower() == 'accept'):
            print(t)
            interface_groups = ''
            for network_interface in interfaces['NetworkInterfaces']:
                #print(network_interface['NetworkInterfaceId'])
                if network_interface['NetworkInterfaceId'] == t['extractedFields']['interface_id']:
                    interface_groups = network_interface['Groups']
                    #print(network_interface['Groups'])

            for s_group in security_groups['SecurityGroups']:
                #find the security group associated with the interface
                for i_group in interface_groups:
                    #print(i_group)
                    #find the matching security group
                    if s_group['GroupId'] == i_group['GroupId']:
                        info += ("securitygroup=" + str(s_group['GroupId'])+"\n")
                        print("SecurityGroup: {0}".format(unicode(s_group['GroupId'])))
        tempFile.write(info)

    #close the temp file
    tempFile.close()
    #write the files to s3
    s3Results = s3.upload_file('/tmp/file', bucketS3, key)
    print s3Results

    response = s3.put_object_acl(
    AccessControlPolicy={
        'Grants': [
            {
                'Grantee': {
                    'EmailAddress': '',
                    'Type': 'AmazonCustomerByEmail',
                },
                'Permission': 'FULL_CONTROL'
            },
        ],
        'Owner': {
            'DisplayName': os.environ['admin_name'],
            'ID': os.environ['admin_id']
        }
    },
    Bucket=bucketS3,
    Key=key
)
