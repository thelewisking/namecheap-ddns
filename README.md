```
# namecheap-ddns

A Python DDNS to iterate through a .env file containing domain list and ddns keys from namecheap.

11/09/2023 - initial commit
12/09/2023 - logic fix for error reporting

todo:
add .env option for specifiying domain, perhaps domain=host:ddns_key ?

# Expected XML response
#------------------------------
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
#------------------------------
# cached_ip="127.0.0.1"
# domain1="namecheap ddns key"
# domain2="namecheap ddns key"
# etc
```
