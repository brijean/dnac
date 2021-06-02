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
     skip_flag = False
     no_neighbor = False
     ap_neighbor_row = {}
     if ip == '128.107.234.18':
        print("\nTime for some debug\n")
     
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
     print("Getting details for:", ip, "\n")
     response =  requests.get(url, headers=headers, verify=False ).json()

    # if type(response) is dict and ('error' in response or 'not have valid permissions' in response):
     if 'message' in response:
       print (response['message'])
       return()
     elif 'error' in response in response:
       print(response['error'])
       return()
     elif 'errorDescription' in response:
       print(response['errorDescription'])
       skip_flag = True
     elif len(response[0]['deviceDetails']['neighborTopology']) < 1:
        no_neighbor = True
#     else:
#        device = (response[0]["deviceDetails"])
     
     if skip_flag == True:
       ap_neighbor_row['hostname'] = None
       ap_neighbor_row['IP Address'] = ip
       ap_neighbor_row['MAC Address'] = None
       ap_neighbor_row['WLC IP'] = None
       ap_neighbor_row['neighbor_ip'] = None
       ap_neighbor_row['neighbor_int'] = None        
     else:
       device = (response[0]["deviceDetails"])
       #get relevant AP attributes
       ap_neighbor_row = {'hostname': device['hostname'], 'IP Address': device['managementIpAddress'], 'MAC Address': device['macAddress'].lower(), 'WLC IP': device['associatedWlcIp']}
       if no_neighbor == False:     
         #iterate through nodes and links tables to find CDP neighbor information
         topo_dict = device['neighborTopology'][0]
         if 'nodes' in topo_dict and 'links' in topo_dict:
           for table_id, table_info in topo_dict.items():
             if table_id == 'nodes':
               for item in table_info:
                 #initialize switch_id
                 switch_found = False
                 if item['additionalInfo']['macAddress'] != None and item['additionalInfo']['macAddress'].lower() == ap_neighbor_row['MAC Address'].lower():
                   #found the AP's ID
                   ap_id = item['id']
                 if item['family'] == 'Switches and Hubs':
                   ap_neighbor_row['neighbor'] = item['name']
                   ap_neighbor_row['neighbor_ip'] = item['ip']
                   #found the cdp neighbor switch ip
                   switch_found = True
                   switch_id = item['id']
             elif table_id == 'links':
               for item in table_info:
                 if switch_found:
                   if item['target'] == switch_id and item['source'] == ap_id:
                     ap_neighbor_row['neighbor_int'] = item['targetInterfaceName']
             if switch_found == False:
               #no switch neighbor information avaiable
               ap_neighbor_row['neighbor'] = None
               ap_neighbor_row['neighbor_ip'] = None
               ap_neighbor_row['neighbor_int'] = None
       else:
         ap_neighbor_row['neighbor'] = None
         ap_neighbor_row['neighbor_ip'] = None
         ap_neighbor_row['neighbor_int'] = None
     ap_neighbor_table.append(ap_neighbor_row.copy())
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
   if len(ap_list) >= 1:
      ap_neighbor_report = getAPNeighborDetails(dnac_parameters['host'],ap_list)
      #produce AP Neighbor report
      report_name = 'ap_neighbor_report.csv'
      #print report to a CSV file
      print_csv(ap_neighbor_report, 'ap_neighbor_report.csv')
   else:
      print("There no APs in inventory on", dnac_parameters['host'])

