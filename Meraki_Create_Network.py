
# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
# * The script aims to create a new network on the Meraki Dashboard in an *
# * Organization and to configure the new network based on a template     *
# * that is being configured.                                             *
# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *

import pandas as pd
import meraki
import time
from datetime import datetime

# insert your API key
API_KEY = 'API_KEY'
dashboard = meraki.DashboardAPI(API_KEY)

now = datetime.now()
dt_string = now.strftime('%Y-%m-%d_%H-%M-%S')

# log file with: netname, serial, ipnet, ipdev, address, zipcode and city
file_name = 'log_file_' + dt_string + '.txt'
log_file = open(file_name, 'wt')

# log file with: netname and network_new
file_name_netID = 'network_ID_' + dt_string + '.txt'
log_file_netID = open(file_name_netID, 'wt')

# import excel file with informations
xlsx_dataframe = pd.read_excel (r'Informations_File.xlsx')
xlsx_dict = xlsx_dataframe.to_dict(orient='records')

# organization, template id and time_zone
org_id = 'XXXXXXXXXXXX' # find organization ID with: GET https://api.meraki.com/api/v1/organizations/
template_id = 'XXXXXXXXXXXX' # find the template ID with: GET https://api.meraki.com/api/v1/organizations/ORGANIZATION_ID/configTemplates
time_zone = 'Europe/Rome' # time zone to be configured on the new network

index = 0

for i in xlsx_dict: # for every row in the excel file: 

    # creating a new network
    print('- Creating network',i['netname'])
    response = dashboard.organizations.createOrganizationNetwork(
        organizationId = org_id, 
        name = i['netname'],
        productTypes = ['appliance'],
        timeZone = time_zone,
        tags = [i['nettag']] # array
    )
    print('- Created network',response['id'], 'with name',response['name'])

    # saving the new network ID
    network_new = response['id'] 

    # binding the new network to the template
    response = dashboard.networks.bindNetwork(
            networkId = network_new,
            configTemplateId = template_id
    )
    print('- Network',i['netname'],'binded to template')

    # adding the device to the network
    response = dashboard.networks.claimNetworkDevices(
        networkId = network_new,
        serials = [i['serial']] # array
    )
    print('- Device',i['serial'],'added to network',i['netname'])

    # checking if the device is correctly added to the network
    control = 0
    while control < 1 :
        try:
            response = dashboard.devices.getDevice(
                serial = i['serial']
            )
            control = 1
            print('- Device',i['serial'],'read normally')
        except:
            print('* Device',i['serial'],'not found in network',i['netname'],'\n*** Sleep 15 seconds ***')
            # if you are in stuck in this loop, go on the new network in the Meraki Dashboard
            # and change name manually to the new device
            time.sleep(15)
            print('* Retry read device',i['serial'],'informations in network',i['netname'])
            print('* Total progress:',str(int(index/len(xlsx_dict)*100)))
            pass
    # configuring name and address on the device
    response = dashboard.devices.updateDevice(
        serial = i['serial'],
        name = i['netname']+' - MX64W',
        address = i['address']+', '+str(i['zipcode'])+' '+i['city']
    )
    print(i['serial'], ',', i['netname']+' - MX64W', i['address'], str(i['zipcode']), i['city'])

    # configuring IP on the appliance vlan
    response = dashboard.appliance.updateNetworkApplianceVlan(
        networkId = network_new,
        vlanId = i['vlan'],
        subnet = i['ipnet'],
        applianceIp = i['ipdev']
    )
    print('- VLAN '+str(i['vlan']), 'with network',i['ipnet'], 'and IP',i['ipdev'])

    # printing statistics
    index+=1
    print('- Network',i['netname'],'with device',i['serial'], 'and IP', i['ipnet'], i['ipdev'],'completed\n\n')
    print('- Total progress:',index,"of",len(xlsx_dict),'-',str(int(index/len(xlsx_dict)*100)),"%")
    now = datetime.now()
    dt_string = now.strftime('%d/%m/%Y %H:%M:%S')

    # log file with: netname, serial, ipnet, ipdev, address, zipcode and city
    log_file.write(dt_string+' '+i['netname']+' '+i['serial']+' '+i['ipnet']+' '+i['ipdev']+' '+i['address']+' '+str(i['zipcode'])+' '+i['city']+'\n')

    # log file with: netname and network_new
    log_file_netID.write(i['netname']+','+network_new+'\n')

log_file.close()
log_file_netID.close()
