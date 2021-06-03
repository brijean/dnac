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
      apList.append({'hostname' : item['hostname'], 'ip' : item['managementIpAddress'], 'MAC Address' : item['macAddress'], 'WLC IP' : item['associatedWlcIp'], 'id' : item['id']})  
   return(apList)


def getPhysicalTopology(dnac):
   url = f"https://{dnac}/dna/intent/api/v1/topology/physical-topology"
   
   #initialize list to be returned
     
   headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-auth-Token": token,
     }
  
   response =  requests.get(url, headers=headers, verify=False ).json()

   return(response['response'])   

def merge_topology(input_table, topo_dict):
  merged_table = []
  for item in input_table:
    merged_table.append(item)
    neighbor_found = False
    for link in topology['links']:
      if link['source'] == item ['id']:
        #found neighbor
        neighbor_found = True
        neighbor_id = link['target']
        for node in topology['nodes']:
          if node['id'] == neighbor_id:
            merged_table[len(merged_table)-1]['neighbor'] = node['label']
            merged_table[len(merged_table)-1]['neighbor_ip'] = node['ip']
        merged_table[len(merged_table)-1]['neighbor_int'] = link['endPortName']      
    if neighbor_found == False:
        merged_table[len(merged_table)-1]['neighbor'] = None
        merged_table[len(merged_table)-1]['neighbor_ip'] = None
        merged_table[len(merged_table)-1]['neighbor_int'] = None   
  return(merged_table)

        

        


  return()


def print_csv(listOfDict, fName):
  csvColumns = listOfDict[0].keys()
  try:
     with open(fName, 'w', encoding='utf-8-sig') as csvFile:
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
   
   #get AP's and associated attributes
   ap_table = getAPList(dnac_parameters['host'])
  
   #get physical topology
   topology = getPhysicalTopology(dnac_parameters['host'])

   ap_report = merge_topology(ap_table, topology)

   #output report
   report_name = 'ap_neighbor_report.csv'
   print_csv(ap_report, 'ap_neighbor_report.csv')
