import requests
from authenticate import get_token
from pprint import pprint
import json
import csv
import time
from dnac_config import process_args
import sys


def getAPList(dnac):
   url = f"https://{dnac}/dna/intent/api/v1/network-device?family=Unified AP"
   
   apList =[]
   headers = {
       "Content-Type": "application/json",
       "Accept": "application/json",
       "X-auth-Token": token,
   }
   response =  requests.get(url, headers=headers, verify=False ).json()

   #iterate through response to get list of ips
   for item in response['response']:
      apList.append(item['managementIpAddress'])
   return(apList)


def getAPNeighborDetails(dnac,apIPList):
   url = f"https://{dnac}/dna/intent/api/v1/device-enrichment-details"
   
   #initialize list to be returned
   ap_neighbor_table = []
   sum_api_calls = 0

   for ip in apIPList:
     headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-auth-Token": token,
        "entity_type": "ip_address",
        "entity_value": ip
     }
  
     
     #adding some sleep time to see if we can get around DNAC API Rate Limiting
     if len(apIPList) > 5 :
         time.sleep(13)
     sum_api_calls = sum_api_calls + 1
     print("This is the:", sum_api_calls, "get\n")
     response =  requests.get(url, headers=headers, verify=False ).json()

     if type(response) is dict and 'error' in response:
       print(response['error'])
       return()
     else:
        device = (response[0]["deviceDetails"])
     
     #get relevant AP attribures
     ap_neighbor_row = {'hostname': device['hostname'], 'IP Address': device['managementIpAddress'], 'MAC Address': device['macAddress'].lower(), 'WLC IP': device['associatedWlcIp']}
     
     #iterate through nodes and links tables to find CDP neighbor information
     topo_dict = device['neighborTopology'][0]
     for table_id, table_info in topo_dict.items():
       if table_id == 'nodes':
         for item in table_info:
           if item['additionalInfo']['macAddress'] != None and item['additionalInfo']['macAddress'].lower() == ap_neighbor_row['MAC Address'].lower():
              #found the AP's ID
              ap_id = item['id']
           if item['family'] == 'Switches and Hubs':
              ap_neighbor_row['neighbor'] = item['name']
              ap_neighbor_row['neighbor_ip'] = item['ip']
              #found the cdp neighbor switch ip
              switch_id = item['id']
       elif table_id == 'links':
         for item in table_info:
            if item['target'] == switch_id and item['source'] == ap_id:
               ap_neighbor_row['neighbor_int'] = item['targetInterfaceName']
         ap_neighbor_table.append(ap_neighbor_row)
   return(ap_neighbor_table)   

def print_csv(listOfDict, fName):
  csvColumns = listOfDict[0].keys()
  try:
     with open(fName, 'w') as csvFile:
        writer = csv.DictWriter(csvFile, fieldnames=csvColumns)
        writer.writeheader()
        for row in listOfDict:
           writer.writerow(row)
  except IOError:
         print("I/O error")
  csvFile.close()
  return()

if __name__ == "__main__":
   #authenticate to target DNAC and get token
   dnac_parameters = process_args(sys.argv)
   token = get_token(dnac_parameters)
   
   #get target AP list for report
   ap_list = getAPList(dnac_parameters['host'])
   #run ap neighbor report on ap_list
   ap_neighbor_report = getAPNeighborDetails(dnac_parameters['host'],ap_list)

   #output report
   report_name = 'ap_neighbor_report.csv'
   print_csv(ap_neighbor_report, 'ap_neighbor_report.csv')