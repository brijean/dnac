import requests
import json



def get_token(dnac_params):  
   url = f"https://{dnac_params['host']}/dna/system/api/v1/auth/token"

   headers = {
      "Content-Type": "application/json",
   }

   requests.packages.urllib3.disable_warnings()
   response =  requests.post(url, auth=(dnac_params['user'], dnac_params['pw']), verify=False).json()
   #print(response)
   return response["Token"]

#if __name__ == "__main__":
 #  token = get_token()
   #print(token)