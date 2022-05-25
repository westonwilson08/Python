import requests
from requests.auth import HTTPBasicAuth
import json
#Purpose of this script is to send large number of events to a MID Server in ServiceNow to immitate
i = 0

headers = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}
data = {"records": [{"source": "Simulated", "node": "nameofnode", "type": "High Virtual Memory", "resource": "C", "severity": "5", "description": "Virtual memory usage exceeds 98%", "ci_type": "cmdb_ci_app_server_tomcat", "additional_info": "{\"name\": \"My Airlines\"}"}, {"source": "Simulated", "node": "01.myairlines.com", "type": "High CPU Utilization", "resource": "D:", "severity": "5", "description": "CPU on 01.my.com at 60%"}]}

alert_data = {"records": [{"source": "IBM Netcool", "node": "somenode", "type": "Purple", "metric_name": "Purple-Alert", "event_class": "Purple connector", "message_key": "Purple", "severity": "2", "description": "172.31.54.35:Purple Event", "additional_info": "{\"u_event_objectid\":\"15855\",\"u_item_name\":\"Test-Ping\",\"u_item_interfaceid\":\"3\",\"u_event_source\":\"0\",\"u_host_host\":\"172.31.54.35\",\"u_event_object\":\"0\",\"u_item_templateid\":\"0\",\"u_item_lastvalue\":\"0\",\"u_event_acknowledged\":\"0\",\"u_trigger_priority\":\"4\",\"u_eventid\":\"70\",\"u_item_itemid\":\"28540\",\"u_item_key_\":\"icmpping\",\"u_event_name\":\"ICMP Server\",\"u_event_clock\":\"1551196283\",\"u_trigger_triggerid\":\"15855\",\"u_trigger_expression\":\"{172.31.54.35:icmpping.last()}=0\",\"u_trigger_description\":\"PING Fail - ICMP Server\",\"u_hostid\":\"10262\",\"u_item_interface_port\":\"10050\",\"u_item_interface_ip\":\"172.31.54.35\",\"u_trigger_value\":\"1\",\"u_item_type\":\"simple check\",\"u_item_applications_name\":\"TEST-ICMP\",\"u_event_value\":\"1\"}"}]}

while i < 5:
    #Send Events to MID Server
    response = requests.post("http://mid.server.ip:80/api/mid/em/jsonv2", auth=HTTPBasicAuth("MidServer", "[name]"), headers=headers, data=json.dumps(data))
    i = i + 1

response = requests.post("http://mid.server.ip:80/api/mid/em/jsonv2", auth=HTTPBasicAuth("MidServer", "[name]"), headers=headers, data=json.dumps(alert_data))

i=0

while i < 5:
    #Send Events to MID Server
    response = requests.post("http://mid.server.ip:80/api/mid/em/jsonv2", auth=HTTPBasicAuth("MidServer", "[name]"), headers=headers, data=json.dumps(data))
    i = i + 1

#print(response)
