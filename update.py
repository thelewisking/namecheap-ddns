import requests
from os.path import join, dirname
from dotenv import dotenv_values, set_key
import logging
from datetime import datetime

today = datetime.today()
log_date = today.strftime("%Y-%m-%d")
log_location = join(dirname(__file__),"log")
logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(levelname)s %(lineno)d: %(message)s', datefmt='%d-%b-%y %H:%M:%S',filename=f"{log_location}/{log_date}.log",filemode="a+")

# sites to get external IP:
# from testing these nicely return the external ip
ip_sites = [
    "https://dynamicdns.park-your-domain.com/getip",
    "http://ipinfo.io/ip",
    "http://ifconfig.me/ip",
    "http://icanhazip.com",
    "http://ident.me",
    ]

# DDNS for Namecheap using web requests
# Namecheap has a guide referencing DDClient as a DDNS however it doesn't work well with multiple domains

# Collect external IP
# Check against .cache file
# If different, iterate through .env domains and update via http request

# Expected XML response:
# <?xml version="1.0" encoding="utf-16"?>
# <interface-response>
#   <Command>SETDNSHOST</Command>
#   <Language>eng</Language>
#   <IP>127.0.0.1</IP>
#   <ErrCount>0</ErrCount>
#   <errors />
#   <ResponseCount>0</ResponseCount>
#   <responses />
#   <Done>true</Done>
#   <debug><![CDATA[]]></debug>
# </interface-response>

# Dotenv format

# cached_ip="127.0.0.1"
# domain1="namecheap ddns key"
# domain2="namecheap ddns key"
# etc


def load_dotenv(path:str) -> dict: # dotenv stores the cached ip and domains
    logging.debug("dotenv loaded")
    return dotenv_values(path)


def get_external_ip(ip_sites:list) -> str: # http call to find external ipv4
    for site in ip_sites:
        logging.debug(f"trying {site}")
        external_ip = requests.get(site)
        if external_ip.status_code == 200:
            ip = external_ip.content.decode().strip()
            logging.debug(f"response successful, IP found to be {ip}")
            return ip
        logging.debug("site failed, trying next site...")

    logging.warning("sites list exhausted, raising error")
    raise ValueError("unable to obtain external ipv4 address")


def update_domains(domains:dict,updated_ip) -> dict: # calls api to update to new ip
    errors = {}
    for domain,api_key in domains.items():
        
        error_bool = True
        errors_count = 1

        logging.debug(f"attempting to update {domain}")
        url = "https://dynamicdns.park-your-domain.com/update"
        call = requests.get(url=url,data={
            "host":"@",
            "domain":domain,
            "password":api_key,
            "ip":updated_ip
            })
        if call.status_code == 200:
            logging.debug(f"call successful for {domain}")
            call_output = call.content.decode().split("\n")
            errors_count = int([num for num in call_output[5] if num.isnumeric()][0]) # slices are based on expected XML response
            if "true" in call_output[9]:
                error_bool = False
            else:
                error_bool = True
            
        if errors_count > 0 or not error_bool:
                logging.warning(f"{domain}: error detected: {errors_count} or general failure: {error_bool}")
                errors[domain] = call_output
        return errors


def log_actions(records:dict): # logs errors and successes for the domains
    if len(records)>0:
        for record,error in records.items():
            logging.warning(f"ERROR {record} ISSUES UPDATING IP")
            logging.warning(f"ERROR LOG:\n{error}")


def main(): 
    dotenv_path = join(dirname(__file__),".env")
    environment_dict = load_dotenv(dotenv_path)

    domains = {key: environment_dict[key] for key in environment_dict.keys() if key != "cached_ip"}
    logging.debug("domains list constructed")

    cached_ip = environment_dict["cached_ip"]
    external_ip = get_external_ip(ip_sites)

    if external_ip != cached_ip:
        logging.info(f"external ip is different! attempting domain update from {cached_ip} to {external_ip}")
        set_key(dotenv_path,"cached_ip",external_ip)
        logging.debug(f"ip cache updated to {external_ip}")
        complete = update_domains(domains,external_ip)
        log_actions(complete)

    else:
        logging.info("cached IP is correct, no actions needed")


if __name__ == "__main__":
    main()

