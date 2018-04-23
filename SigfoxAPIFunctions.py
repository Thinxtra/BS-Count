import requests
import json
from requests.auth import HTTPBasicAuth
from SigfoxCredentials import Credentials
import time
import calendar
from struct import unpack
# Author : Adrian Tchordjallian <adrian.tchordjallian@thinxtra.com>


test = Credentials()

#################
#JSON PROCESSING#
#################


def json_load_byteified(file_handle):
    return _byteify(
        json.load(file_handle, object_hook=_byteify),
        ignore_dicts=True
    )


def json_loads_byteified(json_text):
    return _byteify(
        json.loads(json_text, object_hook=_byteify),
        ignore_dicts=True
    )


def _byteify(data, ignore_dicts = False):
    # if this is a unicode string, return its string representation
    if isinstance(data, unicode):
        return data.encode('utf-8')
    # if this is a list of values, return list of byteified values
    if isinstance(data, list):
        return [ _byteify(item, ignore_dicts=True) for item in data ]
    # if this is a dictionary, return dictionary of byteified keys and values
    # but only if we haven't already byteified it
    if isinstance(data, dict) and not ignore_dicts:
        return {
            _byteify(key, ignore_dicts=True): _byteify(value, ignore_dicts=True)
            for key, value in data.iteritems()
        }
    # if it's anything else, return it in its original form
    return data

#################


def _url(path):
    return 'https://backend.sigfox.com/api/'+path


def get_devices_by_devType(devType_id, limit=100, zone='AU'):
    if limit > 100:
        realLimit = 100
    else:
        realLimit = limit

    flagPage = 1
    allMessages = []
    url = _url('/devicetypes/'+devType_id+ '/devices?') + 'limit=' + str(limit)
    flagPage = 1
    while flagPage:
        messages =  json.loads(requests.get(url, auth=HTTPBasicAuth(test.user[zone], test.password[zone])).text)
#        print(messages)
        try:
            for item in messages['data']:
                allMessages = allMessages + [item['id']]
        
            if not messages['paging']:
                flagPage = 0
            else:
                url = messages['paging']['next']
        except:
            flagPage = 0
            
    return allMessages

def get_device_info(sfid, zone='AU'):
    url = _url('/devices/'+ sfid)
    return json.loads(requests.get(url, auth=HTTPBasicAuth(test.user[zone], test.password[zone])).text)


def get_basestation_by_id(id_sf):
    """
    Gets the Basestation from the Sigfox ID
    :param id_sf:
    :return: the base station object
    """
    return json_loads_byteified(requests.get(_url('/basestations/'+id_sf), auth=HTTPBasicAuth(test.user, test.password)).text)


def get_coordinates_by_id(id_sf):
    bs = get_basestation_by_id(id_sf)
    coordinates = [bs['latitude'], bs['longitude']]
    return coordinates

def get_all_deviceTypes(zone='AU'):
    url = _url('devicetypes/')
    
    flagPage = 1
    while flagPage:
        messages =  json.loads(requests.get(url, auth=HTTPBasicAuth(test.user[zone], test.password[zone])).text)
#        print(messages)
        try:
            allMessages = allMessages + messages['data']
        
            if not messages['paging']:
                flagPage = 0
            else:
                url = messages['paging']['next']
        except:
            flagPage = 0
            
    return allMessages

def get_messages_by_id_and_time(id_sf, tstart, tend = 0, limit=100, zone='AU'):
    if limit > 100:
        realLimit = 100
    else:
        realLimit = limit

    flagPage = 1
    allMessages = []
    url = (_url('/devices/'+id_sf+ '/messages')
    + '?before='+str(int(tend))
    + '&since=' + str(int(tstart))
    + '&limit='+str(realLimit)
    + '&oob=TRUE'
    + '&cbStatus=true'
    + '&dlkAnswerStatus=true')
    
    while flagPage:
        messages =  json.loads(requests.get(url, auth=HTTPBasicAuth(test.user[zone], test.password[zone])).text)
#        print(messages)
        try:
            allMessages = allMessages + messages['data']
        
            if not messages['paging']:
                flagPage = 0
            else:
                url = messages['paging']['next']
        except:
            flagPage = 0
            
    return allMessages
    
def checkEmptyMessage(message):
    if 'not found' in message['message']:
        return 1
    else:
        return 0

def decodeMessage(messages, platform):
    output = messages
        
    for message in output:
        if 'Olga' == platform:    
            message['battery'] = unpack('<B', message['data'][0:2].decode('hex'))[0]
            message['temperature'] = unpack('<B', message['data'][2:4].decode('hex'))[0]
            message['lat'] = unpack('<f', message['data'][4:12].decode('hex'))[0]
            message['long'] = unpack('<f', message['data'][12:20].decode('hex'))[0]
            
        message['numBS'] = len(message['rinfos'])
        
    return output
    
def analyze_missedMessage(messages):    
    currentSeq = messages[0]['seqNumber']
    missedMsgIdx = []
    missedMsgTime = []
    
    for idx in range(1,len(messages)):
        messageSeq = messages[idx]['seqNumber'] + 1
        if currentSeq != messageSeq:
            missedMsgIdx.append(idx)
            missedMsgTime.append([messages[idx-1]['time'], messages[idx]['time']])

        currentSeq = messages[idx]['seqNumber']
        
    count  = (messages[0]['seqNumber']- messages[len(messages)-1]['seqNumber'] - len(messages) + 1)
    
    return missedMsgIdx, count
    

def format_messages_by_id_and_time(id_sf, tstart, tend = 0):
    messageList = get_messages_by_id_and_time(id_sf, tstart, tend)
    
    listBS = {'tap':[],'lat':[],'lon':[],'x':[],'y':[],'z':[]}
    allMessage = []
    for i in messageList:
        perMessage = {'time':[],'listBS':[]}
        perMessage['time'] = i['time']
        for ii in i['rinfos']:
            message = {'rssi':[],'tap':[],'lat':[],'lon':[],'x':[],'y':[],'z':[]}
            message['rssi'] = ii['rssi']
            message['tap'] = ii['tap']

            if message['tap'] not in listBS['tap']:
                coord = get_coordinates_by_id(message['tap'])
                message['lat'] = coord[0]
                message['lon'] = coord[1]
                deg = []                
                deg.append(coord[0])
                deg.append(coord[1])
                xyz = geoconvert.deg2xyz(deg)
                message['x'] = xyz[0]
                message['y'] = xyz[1]
                message['z'] = xyz[2]
                listBS['tap'].append(message['tap'])
                listBS['lat'].append(coord[0])
                listBS['lon'].append(coord[1])
                listBS['x'].append(xyz[0])
                listBS['y'].append(xyz[1])
                listBS['z'].append(xyz[2])
            else:
                index = listBS['tap'].index(message['tap'])
                message['lat'] = listBS['lat'][index]
                message['lon'] = listBS['lon'][index]
                message['x'] = listBS['x'][index]
                message['y'] = listBS['y'][index]
                message['z'] = listBS['z'][index]
                
            perMessage['listBS'].append(message)
            
        allMessage.append(perMessage)

    return allMessage


def toTime(epoch):
    return str(time.localtime(epoch).tm_mday) + ' ' +\
            calendar.month_name[time.localtime(epoch).tm_mon][:3] + ' ' +\
            str(time.localtime(epoch).tm_year)[2:] + ' ' +\
            str(time.localtime(epoch).tm_hour) + ' ' +\
            str(time.localtime(epoch).tm_min) + ' ' +\
            str(time.localtime(epoch).tm_sec)
            
            
def toEpoch(char):
    return time.mktime(time.strptime(char, "%d %b %y %H %M %S"))