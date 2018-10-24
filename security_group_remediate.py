#This script auto remediates newly created security groups within AWS EC2. 
import os, json, boto3, re

def lambda_handler(event, context):

    det = event['detail']
    user_id=det['userIdentity']
    remediated = True
    #Event missing info
    if 'detail' not in event or ('detail' in event and 'eventName' not in det):
        return {"Result": "Failure", "Message": "Lambda not triggered by an event"}
    #approved SG change users
    appr_user = [os.environ['admin_role'].lower(), "awscloudformationstacksetexecutionrole"]
    if user_id['type'] == 'IAMUser':
        user = user_id['userName']
        email_regex = re.compile("@.*")
        user = email_regex.sub("", user)
    if user_id['type'] == 'AssumedRole':
        user = user_id['sessionContext']['sessionIssuer']['userName']
    acct_name = boto3.client('iam').list_account_aliases()
    if (user.lower() not in appr_user):
        res = revoke_sg_in(det)

        sg = str(res['group_id'])
        ec2 = boto3.client('ec2')
        sgroups = ec2.describe_security_groups(GroupIds = [sg])
        sgname= sgroups['SecurityGroups'][0]['GroupName']
        ip_perms = json.dumps(det['requestParameters']['ipPermissions'], indent=4, separators=(',', ': '))
        if remediated == True:
            message = "Auto-Removed: Ingress rule removed from security group: "+sg+" \n\nAdded by: "+user+ " \n\nAccount: "+str(acct_name['AccountAliases'])+" \n\nSecurity Group: "+ sgname + " \n"+ip_perms
            print("REMOVING RULE from "+sgname)
            boto3.client('sns').publish(
                TargetArn = os.environ['sns_topic_arn'],
                Message = message,
                Subject = "Security Group mitigation"
                )
        else:
            message = "Could not remove the security group rule from Account: "+str(acct_name['AccountAliases'])+" \n\n"+sgname+"/"+ sg + ":\n" + json.dumps(ip_perms)
            boto3.client('sns').publish(
                TargetArn = os.environ['sns_topic_arn'],
                Message = message,
                Subject = "Security Group mitigation"
                )
    else:
        print("The event was triggered by an authorized user")


def revoke_sg_in(det):

    ip_perms = normalize_parm_names(det['requestParameters']['ipPermissions']['items'])
    try:
        response = boto3.client('ec2').revoke_security_group_ingress(
            GroupId = det['requestParameters']['groupId'],
            IpPermissions = ip_perms
            )
        remediated = True
    except Exception as e:

        remediated = False
        print("Remediation unsuccessful: "+str(e))
    res = {}

    res['group_id'] = det['requestParameters']['groupId']
    res['user_name'] = det['userIdentity']['arn']
    res['ip_permissions'] = ip_perms
    return res


def normalize_parm_names(ip_items):
    new_ip_items = []
    for ip_item in ip_items:
        new_ip_item = {
            "IpProtocol": ip_item['ipProtocol'],
            "FromPort": ip_item['fromPort'],
            "ToPort": ip_item['toPort']
        }
        ipv6_true = 'ipv6Ranges' in ip_item and ip_item['ipv6Ranges']
        if ipv6_true and 'ipRanges' in ip_item and ip_item['ipRanges']:
            ipv4_v6 = {IpRanges: [{'CidrIp': ''}, {'CidrIpv6': ''} ]}
            new_ip_items.append
            'IpRanges': [
                {
                    'CidrIp': 'string',
                    'Description': 'string'
                },
            ],
            'Ipv6Ranges': [
                {
                    'CidrIpv6': 'string',
                    'Description': 'string'
                },
        else:
            if ipv6_true:
                ip_range_list_name = 'ipv6Ranges'
                ip_address_value = 'cidrIpv6'
                ip_range_list_name_capitalized = 'Ipv6Ranges'
                ip_address_value_capitalized = 'CidrIpv6'
            else:
                ip_range_list_name = 'ipRanges'
                ip_address_value = 'cidrIp'
                ip_range_list_name_capitalized = 'IpRanges'
                ip_address_value_capitalized = 'CidrIp'
            ip_ranges = []
            for item in ip_item[ip_range_list_name]['items']:
                ip_ranges.append(
                    {ip_address_value_capitalized : item[ip_address_value]}
                    )
            new_ip_item[ip_range_list_name_capitalized] = ip_ranges
            new_ip_items.append(new_ip_item)
    return new_ip_items
