#!/usr/bin/python3

import sys, getopt
import requests
import json
from pymisp import MISPObject

def main(argv):
    username = ''
    reg = ''
    country = ''
    url=''
    if len(sys.argv) <= 1:
        print('check.py -c <country> -r <registration> -u <username>')
        sys.exit(2)
    try:
        opts, args = getopt.getopt(argv,"hc:r:u:",["country=","registration=","username="])
    except getopt.GetoptError:
        print ('2 check.py -c <country> -r <registration> -u <username>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ('3 check.py -c <country> -r <registration> -u <username>')
            sys.exit()
        elif opt in ("-c", "--country"):
            country = arg.lower()
        elif opt in ("-r", "--registation"):
            reg = arg.upper()
        elif opt in ("-u", "--username"):
            username = arg

    #------------------------------------------------------------------------


    if (country == "fr"):
        url = "http://www.regcheck.org.uk/api/reg.asmx/CheckFrance"
    if (country == "es"):
        url = "http://www.regcheck.org.uk/api/reg.asmx/CheckSpain"

    payload = "RegistrationNumber=" + reg + "&username=" + username
    headers = {
        'Content-Type': "application/x-www-form-urlencoded",
        'cache-control': "no-cache",
        'Postman-Token': "c76f138c-59b6-492a-9be9-1a21a0c657b1"
        }

    reponse = requests.request("POST", url, data=payload, headers=headers)

    print(reponse.text)

    for item in reponse.text.split("</vehicleJson>"):
        if "<vehicleJson>" in item:
            responseJson = item [ item.find("<vehicleJson>")+len("<vehicleJson>") : ]
            
    vehicleJson = json.loads(responseJson)

    mispObject = MISPObject('vehicle')

    carDescription = vehicleJson["Description"]
    carMake = vehicleJson["CarMake"]["CurrentTextValue"]
    carModel = vehicleJson["CarModel"]["CurrentTextValue"]
    ImageUrl = vehicleJson["ImageUrl"]

    if (country == "fr"):
        IndicativeValue = vehicleJson["IndicativeValue"]["CurrentTextValue"]
        BodyStyle = vehicleJson["BodyStyle"]["CurrentTextValue"]
        RegistrationDate = vehicleJson["RegistrationDate"]
        VIN = vehicleJson["ExtendedData"]["numSerieMoteur"]
        gearbox = vehicleJson["ExtendedData"]["boiteDeVitesse"]
        dynoHP = vehicleJson["ExtendedData"]["puissanceDyn"]
        firstRegistration = vehicleJson["ExtendedData"]["datePremiereMiseCirculation"]

        mispObject.add_attribute('dyno-power', type='text', value=dynoHP)
        mispObject.add_attribute('gearbox', type='text', value=gearbox)

    if (country == "es"):
        IndicativeValue = vehicleJson["IndicativePrice"]
        firstRegistration = vehicleJson["RegistrationDate"]
        VIN = vehicleJson["VehicleIdentificationNumber"]



    mispObject.add_attribute('description', type='text', value=carDescription)
    mispObject.add_attribute('make', type='text', value=carMake)
    mispObject.add_attribute('model', type='text', value=carModel)
    mispObject.add_attribute('vin', type='text', value=VIN)
    mispObject.add_attribute('license-plate-number', type='text', value=reg)

    mispObject.add_attribute('date-first-registration', type='text', value=firstRegistration)
    mispObject.add_attribute('image-url', type='text', value=ImageUrl)

    print(mispObject.to_json())

    with open(country + '_' +reg + '.json', 'w') as outfile:  
        outfile.write(mispObject.to_json())
        
    print ("Description: " + carDescription)
    print ("Make: " + carMake)
    print ("Model: " + carModel)

    #print (reponse)

if __name__ == "__main__":
   main(sys.argv[1:])
