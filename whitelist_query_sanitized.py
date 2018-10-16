import json
import re
import time
import sys

#Enter your Windows credentials for authenticating through the Proxy.
proxy_username = ''
proxy_password = '' #example Pa$$w0rd ascii hex encoded
proxy = 'http://'+proxy_username+':'+proxy_password+'@proxy.global.com:8080'
proxy_auth = {
    'http': 'http://'+proxy_username+':'+proxy_password+'@proxy.global.com:8080',
    'https': 'http://'+proxy_username+':'+proxy_password+'@proxy.global.com:8080'
    }
#Enter your Symantec Management Center credentials (html escaping works). This should be your admin account.
username = ''
password = '' #example Pa$$w0rd ascii hex encoded

#Import or install and import necessary packages.
def install_and_import(package):
    import importlib
    try:
        importlib.import_module(package)
    except ImportError:
        import pipenv
        pipenv.main(['install', '-v', '--proxy', proxy, '--trusted-host', 'pypi.org', '--trusted-host', 'pypi.python.org', '--trusted-host', 'files.pythonhosted.org', package])
    finally:
        globals()[package] = importlib.import_module(package)
        print('Successfully imported: '+str(package))

install_and_import('requests')
install_and_import('bs4')
install_and_import('urllib3')
from requests.auth import HTTPBasicAuth

auth = HTTPBasicAuth(username, password)


'''
Python script to check OSINT information on a proxy whitelist request.

Input of website url to be whitelisted.
Outputs returned results from the BlueCoats, Symantec site review, Norton McAfee, VirusTotal, Zulu Zscaler, and SSL Labs.

The formatted information returned last can be pasted into ServiceNow tickets.
'''
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

print("====================================================")
whitelist_website = raw_input("Please enter the website URL to be whitelisted: ")
sn_ticket = raw_input("Please enter the full ticket number for ServiceNow (enter if no ticket): ")

#Start SSL Labs scan first
ssl_lab = requests.get('https://api.ssllabs.com/api/v2/analyze', params={'host': whitelist_website, 'startNew': 'on', 'ignoreMismatch': 'on'}, proxies=proxy_auth, verify=False)

#Get a list of proxy policies
response = requests.get('https://symantecserver:8082/api/policies', auth=auth, verify=False)

response_json = json.loads(response.text)

print("====================================================")
#Print the list of policies
#for object in response_json:
#    print (object['referenceId'])
#print("====================================================")
#Take user input for which policy to check against
#selected_policy = raw_input("Please select a policy to check or modify: (Enter Prod_User)")
selected_policy = ''
if selected_policy == '':
    selected_policy="Prod_User"

#Find the UUID of the selected policy
for object in response_json:
    if str(object['referenceId']) == selected_policy:
        selected_uuid = object['uuid']

#Find all hosts with the selected policy applied
policy_targets = requests.get('https://symantecserver:8082/api/policies/'+selected_uuid+'/targets', auth=auth, verify=False)
policy_targets_json = json.loads(policy_targets.text)

#Print a list of target machines
print("====================================================")
for target in policy_targets_json:
    print (target['device']['name'])

#Accept user input for the target machine
print("====================================================")
target_proxy = str(policy_targets_json[0]['device']['name'])#raw_input('Please select a target proxy to check: (default '+str(policy_targets_json[0]['device']['name'])+') ')

#if target_proxy == '':
    #target_proxy = str(policy_targets_json[0]['device']['name'])
print("Using "+target_proxy)

#Find the UUID of the target machine
for target in policy_targets_json:
    if str(target['device']['name']) == target_proxy:
        target_uuid = target['uuid']

#Get a preview of the policy
policy_preview = requests.get('https://symantecserver:8082/api/policies/'+selected_uuid+'/targets/'+target_uuid+'/preview', auth=auth, verify=False)

#Find indices of each definition in the policy
define_category = [(a.start(), a.end()) for a in list(re.finditer(r'define((.*?)\n*)+end', policy_preview.text))]


print('*********************')

#Check if policy contains categories or conditions
if (policy_preview.text).find(r'define category') != -1:
    category_defined = True
else:
    category_defined = False

i=0
all_categories = []
#Loop through the indices of each category definition
for category in define_category:
    #category is in the format (1, 23)
    cat = policy_preview.text[category[0]:category[1]]
    if cat.find(whitelist_website) != -1:
        if category_defined == True:
            if re.match(r'define category', cat):
                cat_definition = re.match(r'define category.*\n', cat)
            else:
                break
        else:
            cat_definition = re.match(r'define.*\n', cat)
        if cat_definition:
            print_cat_def = True
        cat_sites = re.findall(r'.*'+whitelist_website+'.*\n', cat)

        #print(cat_sites)
        if print_cat_def:
            if cat_definition.group(0) not in cat_sites:
                #print (cat_definition.group(0))
                #Get the name of the category
                cat_definition_formatted = (cat_definition.group(0)).replace('define category ', '')
                print(cat_definition_formatted)
                all_categories.insert(i, cat_definition_formatted)
                for site in cat_sites:
                    site = re.sub(r'\\n', '', site)
                    print (site)
                print ('end\n*********************')
                i+=1


#perform a reputation search
print("")
print("")
print("")
print("||||||||||||||||||||||||||||||||||||||||||||||||||||")
print("|||||||||||||||||||  Results  ||||||||||||||||||||||")
print("||||||||||||||||||||||||||||||||||||||||||||||||||||")

#If the site is found
result_text = ""
all_categories_string = ''.join(str(category) for category in all_categories)

if i>0:
    print("{0} categories contain the website {1}:".format(unicode(i),unicode(whitelist_website)))
    for category in all_categories:
        print(category)
    result_text="{0} categories contain the website {1}:\n{2}.".format(unicode(i),unicode(whitelist_website),unicode(all_categories_string))
else:
    print("The website {0} was NOT FOUND within the {1} policy.".format(unicode(whitelist_website),unicode(selected_policy)))
    result_text="The website {0} was NOT FOUND within the {1} policy.".format(unicode(whitelist_website),unicode(selected_policy))
print("")
print("====================================================")
#Get Symantec Category review
with requests.Session() as sy_request:
    symantec_response = sy_request.post("https://sitereview.bluecoat.com/resource/lookup", proxies=proxy_auth, headers={"User-Agent": "Mozilla/5.0", "Content-Type": "application/json"}, data=json.dumps({"url": str(whitelist_website), "captcha":""}))
    if symantec_response.status_code == 200:
        symantec_decoded = symantec_response.content.decode("UTF-8").encode(sys.stdout.encoding, 'ignore')
        symantec_soup = BeautifulSoup(symantec_decoded, 'html.parser')
        symantec_category = symantec_soup.find('categorization')
        #symantec_category = symantec_soup.find('name')
        #symantec_category_name = symantec_category.find('name')
        #found_category = symantec_category_name.get_text()
        #
        symantec_formatted = re.findall(r'[a-zA-Z\s\\\/]+', symantec_category.get_text())
        #categorization = symantec_decoded['categorization']
        print("Symantec Category(s): ")
        symantec_cat = ""
        for category in symantec_formatted:
            print(category)
            symantec_cat+= category
    else:
        print("Symantec Category lookup failed:")
        print(symantec_response)


#Get Norton Results
with requests.Session() as norton_request:
    norton_response = norton_request.get('https://safeweb.norton.com/report/show?url='+whitelist_website, proxies=proxy_auth, verify=False)
    if norton_response.status_code == 200:
        norton_soup = BeautifulSoup(norton_response.content, 'html.parser')
        location = norton_soup.find('img', attrs={'style': 'display:inline'})
        location = re.sub(r'.*\/images\/flags\/', '', str(location))
        location = re.sub(r'\.gif.*', '', str(location))
        norton_rating = norton_soup.find('div', attrs={'class': 'row-fluid borderTop'})
        norton_rating = re.sub(r'((.|\n)*)<h4>', '', str(norton_rating))
        norton_rating = re.sub(r'\n{2,4}', '\n', str(norton_rating))
        norton_rating = re.sub('\t', '', str(norton_rating))
        norton_rating = re.sub(r'(<.*?>)', '', str(norton_rating))

        print("====================================================")
        norton_location = str(location).upper()
        print('Norton Results -- Location: '+ norton_location)
        print (norton_rating)
        norton_link = 'https://safeweb.norton.com/report/show?url='+whitelist_website
        print('URL: '+norton_link)
    else:
        print("Norton lookup failed: ")
        print(norton_response.status_code)
        norton_location = "Results were not returned!!!"
        norton_rating = "Results were not returned!!!"

#Get McAfee Results
with requests.Session() as mcafee_request:
    mcafee_response = mcafee_request.get('https://www.mcafee.com/enterprise/en-us/threat-intelligence.websitetc.html?vid='+whitelist_website, proxies=proxy_auth, verify=False)
    if mcafee_response.status_code == 200:
        mcafee_soup = BeautifulSoup(mcafee_response.content, 'html.parser')
        mcafee_rating = mcafee_soup.find('div', attrs={'class': 'threeFourth'})
        mcafee_rating = re.sub(r'((.|\n)*)title=', '', str(mcafee_rating))
        mcafee_rating = re.sub(r'\/((.|\n)*)', '', str(mcafee_rating))

        print("====================================================")
        mcafee_link = 'https://www.mcafee.com/enterprise/en-us/threat-intelligence.websitetc.html?vid='+whitelist_website
        print('McAfee Risk: ' + mcafee_rating)
        print('URL: '+mcafee_link)
        print("")
        print("")
    else:
        print("McAfee lookup failed: ")
        print(mcafee_response.status_code)
        mcafee_rating = "Results were not returned!!!"

#Get VirusTotal Results
vt_apikey = ''
with requests.Session() as vt_request:
    vt_req = vt_request.post('https://virustotal.com/vtapi/v2/url/scan', data={'apikey': vt_apikey, 'url': whitelist_website}, proxies=proxy_auth, verify=False)
    if vt_req.status_code == 200:
        #Wait for response
        print('Waiting for response from VirusTotal...')
        time.sleep(10)
        vt_response = vt_request.post('https://virustotal.com/vtapi/v2/url/report', params={'apikey': vt_apikey, 'resource': whitelist_website}, proxies=proxy_auth, verify=False)
        if vt_response.status_code == 200:
            vt_json = json.loads(vt_response.text)
            print("====================================================")
            print('VirusTotal Results: ')
            vt_total = ('Total sites scanned: ' + str(vt_json['total']))
            vt_malicious = (str(vt_json['positives']) + ' site(s) found '+ whitelist_website + ' malicious.')
            print (vt_total)
            print (vt_malicious)
            vt_link = vt_json['permalink']
            print('URL: '+vt_link)
            print("")
            print("")
        else:
            print("VirusTotal Response failed:")
            print(vt_response)
            vt_total = "Results were not returned!!!"
            vt_malicious = "Results were not returned!!!"
    else:
        print("VirusTotal Submission failed:")
        print(vt_req)
        vt_total = "Results were not returned!!!"
        vt_malicious = "Results were not returned!!!"

#Get Zulu Zscaler Results
with requests.Session() as zulu_session:
    zulu = 'https://zulu.zscaler.com'
    print('Waiting on Zulu Zscaler results. This may take a couple of minutes...')

    zulu_get = zulu_session.get(zulu, proxies=proxy_auth, verify=False)
    if zulu_get.status_code == 200:
        zulu_soup = BeautifulSoup(zulu_get.text, 'html.parser')
        zulu_csrf = zulu_soup.find('input', attrs={'name': 'csrf_token'})
        zulu_csrf = re.sub(r'.*value="', '', str(zulu_csrf))
        zulu_csrf = re.sub(r'"/>', '', str(zulu_csrf))
        data={'url': whitelist_website, 'csrf_token': zulu_csrf}
        time.sleep(10)
        zulu_post = zulu_session.post(zulu, data=data, cookies=zulu_session.cookies, proxies=proxy_auth, verify=False)
        if zulu_post.status_code == 200:
            zulu_post_soup = BeautifulSoup(zulu_post.content, 'html.parser')
            zulu_results = zulu_post_soup.get_text().encode(sys.stdout.encoding, errors='replace')
            zulu_results = re.sub(r'(.|\n)*Test Results', '', str(zulu_results))
            zulu_results = re.match(r'(.|\n)*100', str(zulu_results))
            zulu_results = zulu_results.group(0)
            print("====================================================")
            print("Zulu Zscaler Results: ")
            print(zulu_results)
        else:
            print("Zulu Zscaler POST failed")
            print(zulu_post)

    else:
        print("Zulu Zscaler GET failed:")
        print(zulu_get)
        print('')
        print('')
        zulu_results = "Results were not returned!!!"

#Get SSL Labs Report
with requests.Session() as ssllabs_session:
    ssl_result = ''
    ssl_lab_response = ssllabs_session.get('https://api.ssllabs.com/api/v2/analyze', params={'host': whitelist_website, 'ignoreMismatch': 'on'}, proxies=proxy_auth, verify=False)
    #ssl_grade_a = ["A", "A+"]
    ssl_grade = []
    if ssl_lab_response.status_code == 200:
        ssl_response = json.loads(ssl_lab_response.text)
        def get_ssl_result(ssl_response):
            for endpoint in ssl_response['endpoints']:
                if endpoint['statusMessage'] == 'Ready':
                    ssl_grade.append(endpoint['grade'])
        print('Getting SSL Labs report...')

        i=0
        if ssl_response['status'] == 'READY' or ssl_response['status'] == 'IN_PROGRESS':
            if ssl_response['endpoints'][0]['statusMessage'] == 'Ready':
                get_ssl_result(ssl_response)
            while len(ssl_grade) <= 0 and i<10:
                time.sleep(30)
                ssl_lab_response = ssllabs_session.get('https://api.ssllabs.com/api/v2/analyze', params={'host': whitelist_website, 'ignoreMismatch': 'on'}, proxies=proxy_auth, verify=False)
                ssl_response = json.loads(ssl_lab_response.text)
                get_ssl_result(ssl_response)
                i+=1
            ssl_result = ssl_grade

        if ssl_response['status'] == 'ERROR':
            ssl_result = ssl_response['statusMessage']
        print("====================================================")
        print ('SSL Labs Results: ')
    #if type(ssl_result) == type([]):
    #    for result in ssl_result:
    #        print (result)
    #else:
        print (ssl_result)
    else:
        print("SSL Labs failed:")
        print(ssl_lab_response)
        ssl_results = "Response not returned!!!"


print("====================================================")
print(" The following output will be posted in ServiceNow  ")
print("====================================================")
sn_worknotes = result_text+"\n"+ "\nSymantec Category: " + str(symantec_formatted) + "\nNorton Review - Location: "+ norton_location+"\n"+norton_rating+"\nMcAfee Risk: "+mcafee_rating+"\nVirusTotal Results: "+vt_total + "\n"+vt_malicious+"\nZulu Zscaler Results:"+zulu_results+"\n\nSSL Labs Result: "+ str(ssl_result)
sn_worknotes = sn_worknotes.replace('\n', '\\n')
sn_worknotes = sn_worknotes.replace('\t', '')
sn_worknotes = sn_worknotes.replace('"', '')
sn_worknotes = '[code]Please review this request and move it to the Whitelisting team or access management if approved. <br />'+sn_worknotes+'[/code]'
sn_worknotes = sn_worknotes.replace('\\"', '"')
sn_worknotes = sn_worknotes.replace('\\n', '<br />')
sn_worknotes = sn_worknotes.replace('\<br />', '<br />')
print (sn_worknotes)
if sn_ticket != '':
    sn_user = '' #Need to use Service Account
    sn_password = ''
    headers = {"Content-Type":"application/json","Accept":"application/json"}
    sn_query = False
    #Check for the type of ticket that was provided
    if re.match('inc', sn_ticket.lower()):
        sn_endpoint = 'https://env.service-now.com/api/now/table/incident'
        sn_query = True
    elif re.match('task', sn_ticket.lower()):
        sn_endpoint = 'https://env.service-now.com/api/now/table/sc_task'
        sn_query = True
    else:
        print('Cannot find the ticket "'+sn_ticket+'" within the incident or task table')
    if sn_query:
        #Get ServiceNow ticket information and format it
        with requests.Session() as sn_request:
            sn_response = sn_request.get((sn_endpoint+'?sysparm_query=^number='+sn_ticket+'&sysparm_limit=1'), auth=(sn_user, sn_password), proxies=proxy_auth, verify=False)
            sn_json = json.loads(sn_response.text)
            sn_sys_id = sn_json['result'][0]['sys_id']

        sn_worknotes = result_text+"\n"+ "\nSymantec Category: " + str(symantec_formatted) + "\nNorton Review - Location: "+ norton_location+"\n"+norton_rating+"\nMcAfee Risk: "+mcafee_rating+"\nVirusTotal Results: "+vt_total + "\n"+vt_malicious+"\nZulu Zscaler Results:"+zulu_results+"\nSSL Labs Result: "+ str(ssl_result)
        sn_worknotes = sn_worknotes.replace('\n', '\\n')
        sn_worknotes = sn_worknotes.replace('\t', '')
        sn_worknotes = sn_worknotes.replace('"', '')
        #sn_worknotes = sn_worknotes.replace(r'((u\')|\]|\[|\')+', '')
        #print (sn_worknotes)
        sn_worknotes_json = json.dumps('{"work_notes": "[code]Please review this request and move it to the Whitelisting team or access management if approved. <br />'+sn_worknotes+'[/code]", "assigned_to": "a4b0e6540fd2b500d55ae498b1050e9d", "state": 1}') #Append worknotes and assign task to specific user.
        sn_worknotes_json = sn_worknotes_json[1:-1]
        sn_worknotes_json = sn_worknotes_json.replace('\\"', '"')
        sn_worknotes_json = sn_worknotes_json.replace('\\n', '<br />')
        sn_worknotes_json = sn_worknotes_json.replace('\<br />', '<br />')
        #print (sn_worknotes_json)
        #Submit data to the ServiceNow ticket
        with requests.Session() as sn_update:
            sn_put = sn_update.put((sn_endpoint+'/'+sn_sys_id), auth=(sn_user, sn_password), data=sn_worknotes_json, headers=headers, proxies=proxy_auth, verify=False)
            if sn_put.status_code == 200:
                print("The information gathered has been successfully submitted to the requested ServiceNow ticket. The ticket has been moved on to Manager for approval")
            else:
                print("There was a problem submitting the ticket to ServiceNow. Please add the results manually.")
