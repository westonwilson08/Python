#This script is for adding a default deny policy to newly created AWS accounts/roles
import boto3,os,re
iam = boto3.client('iam')
denyPolicy = 'arn:aws:iam::'+str(os.environ['account'])+':policy/itsec-default-deny'
admin_role = str(os.environ['admin_role'])
appr_user = [str(admin_role), "svc_itsec-pipeline"]
security_user_regex = r"svc_itsec"

def lambda_handler(event, context):
    #User/Role that created the event
    action_user = ""
    if str(event['detail']['userIdentity']['type']) == "IAMUser":
        action_user = event['detail']['userIdentity']['userName']
        #print(str(action_user))
    elif str(event['detail']['userIdentity']['type']) == "AssumedRole":
        user_regex = r'.*\/'
        role = event['detail']['userIdentity']['arn']
        assumed_user = re.sub(user_regex, "", role)
        action_user = event['detail']['userIdentity']['sessionContext']['sessionIssuer']['userName']
        #print(str(assumed_user))
    else:
        print("Could not determine the user who performed the action. No default deny policy has been added!")
        #Send SNS notification to Security
        message = "Default Deny NOT added to User/Role: \n{0}\n\nEvent Details: \n{1}".format(unicode(action_user),unicode(event['detail']))
        boto3.client('sns').publish(
            TargetArn = os.environ['sns_topic_arn'],
            Message = message,
            Subject = "Default Deny Alert"
            )
    if str(action_user) != "":
        #Check for admin_role performing the add
        if (str(action_user) in appr_user) or re.match(security_user_regex, action_user) != None:
            print("This action was authorized by an administrator. No default deny will be applied. User: {0}").format(unicode(event['detail']['userIdentity']['arn']))
        else:
            #If a new user is created
            if event['detail']['eventName'] == 'CreateUser':
                iam.attach_user_policy(UserName=event['detail']['responseElements']['user']['userName'], PolicyArn=denyPolicy)
                print ('added user {0} to TestDenyPolicy').format(unicode(event['detail']['responseElements']['user']['userName']))
            #If a new Role is created
            if event['detail']['eventName'] == 'CreateRole':
                iam.attach_role_policy(RoleName=event['detail']['requestParameters']['roleName'], PolicyArn=denyPolicy)
                print ('added role {0} to TestDenyPolicy').format(unicode(event['detail']['requestParameters']['roleName']))
