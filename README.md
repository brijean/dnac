#This script builds a report of Access points, their IP address, WLC IP Address and associated CDP Neigbhor
#The output of the script is a CSV file with the following structure:

#hostname,IP Address,MAC Address,WLC IP,neighbor,neighbor_ip,neighbor_int


#usage
usage: get_devicelist.py [-h] dnac dnac_user dnac_pw

#positional arguments:
 dnac        FQDN or IP address of target controller.
 dnac_user   DNAC username
 dnac_pw     DNAC password

#optional arguments:
  -h, --help  show this help message and exit
