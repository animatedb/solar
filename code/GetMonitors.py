#!/usr/bin/env python3
import requests
import json
import sys

# This reads Sonoff power monitoring plugs that have Tasmota installed.
# This uses the HTTP web responses from each plug and uses the Status sensor
# command (StatusSNS) which is the Status command number 10.
# This gets the total amount of energy that went through the plug.

# The following shows the Sonoff modules from the response of the Modules command.
# url = 'http://<ip>/cm?cmnd=Modules'
##"1":"Sonoff Basic",
##"2":"Sonoff RF",
##"3":"Sonoff SV",
##"4":"Sonoff TH",
##"5":"Sonoff Dual",
##"6":"Sonoff Pow",
##"7":"Sonoff 4CH",
##"8":"Sonoff S2X",
##"9":"Slampher",
##"10":"Sonoff Touch",
##"11":"Sonoff LED",
##"19":"Sonoff Dev",
##"21":"Sonoff SC",
##"22":"Sonoff BN-SZ",
##"23":"Sonoff 4CH Pro",
##"25":"Sonoff Bridge",
##"26":"Sonoff B1",
##"28":"Sonoff T1 1CH",
##"29":"Sonoff T1 2CH",
##"30":"Sonoff T1 3CH",
##"39":"Sonoff Dual R2",
##"41":"Sonoff S31",
##"43":"Sonoff Pow R2",
##"44":"Sonoff iFan02",
##"70":"Sonoff L1",
##"74":"Sonoff D1",
##"71":"Sonoff iFan03",

# Status names:
# 1:"StatusPRM"         Parameters - baud rate, uptime, boot count, save count
# 2:"StatusFWR"         Firmware - build, cpu freq, sdk
# 3:"StatusLOG"         Logging - where/how often to log
# 4:"StatusMEM"         Memory - flash info, drivers, sensors
# 5:"StatusNET"         Network IP, Gateway(router)
# 6:"StatusMQTT"        MGTT info
# 7:"StatusTIM"         Time - nows time zone, sunrise, sunset, etc?
# 8:"StatusSNS"         Sensor info, "Total":f.f
# 9:"StatusPTH"         Power thresholds
# 10:"StatusSNS"        Sensor info, "Total":f.f
# 11:"StatusSTS"        State
# 12:"Status???"        [200]

space = '%20'
url = 'http://10.0.0.98/cm?cmnd=Status+' + space + str(10)
portAddresses = [
    ('10.0.0.98', 'Solar'),
    ('10.0.0.60', 'Car'),
    ('10.0.0.204', 'Living'),
    ('10.0.0.184', 'Bath')
    ]

def getMonitors():
    responses = []
    for ip, name in portAddresses:
        StatusCmdNumber = 10    # command "StatusSNS"
        command = 'cm?cmnd=Status+' + space + str(StatusCmdNumber)
        response = requests.get('http://' + ip + '/' + command)
        if '200' in str(response):
            content = json.loads(response.content)
            value = content['StatusSNS']['ENERGY']['Total']
        else:
            raise ValueError('Bad response from ' + ip)
        responses.append((name, value))

    headers = []
    values = []
    for name, value in responses:
        headers.append(name)
        values.append(str(value))
    lines = []
    lines.append('\t'.join(headers) + '\n')
    lines.append('\t'.join(values) + '\n')
    sys.stdout.writelines(lines)
#    with open('getMonitors.txt', 'w') as file:
#        file.writelines(lines)

getMonitors()
