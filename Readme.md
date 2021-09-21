The script aims to create a new network on the Meraki Dashboard in an Organization and to configure the new network based on a template that is being configured.

# How to run
All configuration data is read from the Informations_File.xlsx file.

Before starting the Python script, change the following parameters:
- API_KEY: insert your personal Meraki API key

- xlsx_dataframe: you can change working folder on your IDE, place the script anche the xlsx file in the same folder and open the terminal or you fan add the complete path to you file. For esample: r'C:\Users\ba1090\Documents\Script\MerakiInformations_File.xlsx'.
	
- org_id: Organization ID that you are working on. You can find the Organization ID with: GET https://api.meraki.com/api/v1/organizations/
	
- template_id: ID of the template you have created on the Meraki Dashboard you can find the template ID with: GET https://api.meraki.com/api/v1/organizations/ORGANIZATION_ID/configTemplates

- time_zone: time zone of the network you are creating. For example: 'Europe/Rome'

# How to compile xlsx file
- serial: Serial ID of the new device. It must be not used.

- netname: Name of the new network.

- nettag: Tag to be added to the network.

- address: Address of the city where you will install the device.

- zipcode: Zip Code of city.

- city: City where you will install the device.

- vlan: VLAN ID of the network you are using.

- ipnet: Network to be assigned to the device.

- ipdev: IP address to be assigned to the device.
