import os, sys, argparse

def dnac_values():
  #next version will give option of setting values in environment variables
  DNAC=os.environ.get('DNAC')
  DNAC_PORT=os.environ.get('DNAC_PORT')
  DNAC_USER=os.environ.get('DNAC_USER')
  DNAC_PASSWORD=os.environ.get('DNAC_PASSWORD')

  DNAC_PARAMS = {'host': DNAC, 'port': DNAC_PORT, 'user': DNAC_USER, 'password': DNAC_PASSWORD}
  return(DNAC_PARAMS)


def process_args(arguments):
  parser = argparse.ArgumentParser()
  parser.add_argument("dnac", help = "FQDN or IP address of target controller.")
  parser.add_argument("dnac_user", help= "DNAC username")
  parser.add_argument("dnac_pw", help = "DNAC password")
  args = parser.parse_args()
  dnac_args = {'host': args.dnac, 'user': args.dnac_user, 'pw': args.dnac_pw}
  return(dnac_args)

#if __name__ == "__main__":
  # dnac_arguments = process_args(sys.argv)
  # print(dnac_arguments)
   #DNAC = dnac_values()
#   print(DNAC)