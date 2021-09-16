
# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
# * The script aims to create a new network on the Meraki Dashboard in the        *
# * Amplifon Organization and to configure the new network based on the country   *
# * template that is being configured.                                            *
# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *

import pandas as pd
import meraki
import time
from datetime import datetime

API_KEY = 'API_KEY'
dashboard = meraki.DashboardAPI(API_KEY)

now = datetime.now()
dt_string = now.strftime('%Y-%m-%d_%H-%M-%S')
file_name = 'log_file_Amplifon_' + dt_string + '.txt'
log_file = open(file_name, 'wt')

# chiudere il file excel per farlo leggere
xlsx_dataframe = pd.read_excel (r'Informations_File.xlsx')
xlsx_dict = xlsx_dataframe.to_dict(orient='records')

# Prametri organizzazione e template configurazione
org_id = 'XXXXXXXXXXXX' # Amplifon-New (GET https://api.meraki.com/api/v1/organizations/)
template_id = 'XXXXXXXXX' # template ES (GET https://api.meraki.com/api/v1/organizations/782500435255623681/configTemplates)

index = 0

for i in xlsx_dict: # i prende il valore della riga da 0 a fine-1 di xlsx_dict 
    # crea una nuova network
    print('- Creating network',i['netname'])
    response = dashboard.organizations.createOrganizationNetwork(
        organizationId = org_id, 
        name = i['netname'],
        productTypes = ['appliance'],
        timeZone = 'Europe/Brussels',
        tags = [i['nettag']] # array
    )
    print('- Created network',response['id'], 'with name',response['name'])

    # salva l'ID della network creata
    network_new = response['id'] 

    # bind della network al template da assegnare
    response = dashboard.networks.bindNetwork(
            networkId = network_new,
            configTemplateId = template_id
    )
    print('- Network',i['netname'],'binded to template')

    # aggiunta del device alla network
    response = dashboard.networks.claimNetworkDevices(
        networkId = network_new,
        serials = [i['serial']] # array
    )
    print('- Device',i['serial'],'added to network',i['netname'])

    # configurazione dettagli device
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
            time.sleep(15)
            print('* Retry read device',i['serial'],'informations in network',i['netname'])
            print('* Total progress:',str(int(index/len(xlsx_dict)*100)))
            pass
    response = dashboard.devices.updateDevice(
        serial = i['serial'],
        name = i['netname']+' - MX64W',
        address = i['address']+', '+str(i['zipcode'])+' '+i['city']
        # verificare se possibile modificare porta WAN2
    )
    print(i['serial'], ',', i['netname']+' - MX64W', i['address'], str(i['zipcode']), i['city'])

    # configurazione IP VLAN appliance
    response = dashboard.appliance.updateNetworkApplianceVlan(
        networkId = network_new,
        vlanId = i['vlan'],
        subnet = i['ipnet'],
        applianceIp = i['ipdev']
    )
    print('- VLAN '+str(i['vlan']), 'with network',i['ipnet'], 'and IP',i['ipdev'])

    index+=1
    print('- Network',i['netname'],'with device',i['serial'], 'and IP', i['ipnet'], i['ipdev'],'completed\n\n')
    print('- Total progress:',index,"-",str(int(index/len(xlsx_dict)*100)),"%")
    now = datetime.now()
    dt_string = now.strftime('%d/%m/%Y %H:%M:%S')
    log_file.write(dt_string+' '+i['netname']+' '+i['serial']+' '+i['ipnet']+' '+i['ipdev']+' '+i['address']+' '+str(i['zipcode'])+' '+i['city']+'\n')

log_file.close()
