import http.client, hashlib
import json
from typing import TypeVar

from django.conf import settings
from django.http import JsonResponse

from purchases.exceptions import TrackerPreviouslyRegistered, TrackerRejectedUnknownCode

# def register_tracker(tracking_number:str, carrier_code:str = None) -> tuple[str,str,str,bool]:
#     """Register tracker if it doesn't already exist
    
#     Response is a tuple

#     tracking number

#     carrier as carrier_code

#     message

#     true/false of whether tracker was created
#     """
#     try:
#         tracker_response = tracker_request('REGISTER',[(tracking_number,carrier_code)])
#     except:
#         raise

#     data = next(iter(tracker_response['accepted'] or []), None)
#     error = next(iter(tracker_response['rejected'] or []), None)['error']
#     code = error['code']
#     if data:
#         response = True
#         message = None
#         carrier_code = data['carrier']
#         number = data['number']
#     elif code == -18019901:
#         response = False
#         message = code,error['message']
#         carrier_code = None
#         number = None
#     else:
#         response = False
#         message = code,error['message']
#         carrier_code = None
#         number = None

#     return number, carrier_code, message, response

# T = TypeVar('T',(str,str,str,bool))

def register_trackers(payload:list[tuple[str,str]]) -> dict[list[dict],list[dict]]:
    """Register trackers if they doesn't already exist
    
    Argument:

    List of tuples in form of (tracking_number, carrier_code)

    Response is a list of tuples

    tracking number

    carrier as carrier_code

    message

    true/false of whether tracker was created
    """
    try:
        tracker_responses = tracker_request('REGISTER',payload)
    except:
        raise
    accepted_list = []
    for tracker in tracker_responses['accepted']:
        accepted = {}
        accepted['response'] = True
        accepted['message'] = None
        accepted['carrier_code'] = tracker['carrier']
        accepted['number'] = tracker['number']
        accepted_list.append(accepted)

    rejected_list = []
    for tracker in tracker_responses['rejected']:
        rejected = {}
        rejected['number'] = tracker.get('number',None)
        rejected['code'] = tracker['error'].get('code',None)
        rejected['message'] = tracker['error'].get('message',None)
        try:
            if rejected['code'] == -18019901:
                raise TrackerPreviouslyRegistered(rejected['number'], rejected['message'])
            else:
                raise TrackerRejectedUnknownCode(rejected['number'], rejected['code'], rejected['message'])
        except TrackerPreviouslyRegistered as err:
            rejected['exception'] = err
            rejected_list.append(rejected)
        except TrackerRejectedUnknownCode as err:
            raise
        
    return {'accepted':accepted_list, 'rejected':rejected_list}

REQUEST_METHODS = (
    'REGISTER',
    'GETLIST',
    'GET',
)

def tracker_request(request_method:REQUEST_METHODS, payload:list[tuple]) -> JsonResponse:
    """Return data based on method from list of trackers.
    
    payload is a list of tuples containing (tracking_number,carrier_code)

    request_method is one of 'REGISTER,' 'GETLIST,' 'GET.'
    """
    conn = http.client.HTTPSConnection("api.17track.net")

    headers = {
        'Content-Type': "application/json",
        '17token': settings._17TRACK_KEY
        }

    payload_dict = []
    for t,c in payload:
        if t and c:
            payload_dict.append({
                "number": t,
                "carrier": c,
            })
        elif t:
            payload_dict.append({
                "number": t,
            })
        else:
            raise ValueError("All trackers MUST have a tracking number.")
    
    payload = json.dumps(payload_dict)

    match request_method:
        case 'REGISTER':
            conn.request("POST", "/track/v2/register", payload, headers)
        case 'GETLIST':
            conn.request("POST", "/track/v2/gettracklist", payload, headers)
        case 'GET':
            conn.request("POST", "/track/v2/gettrackinfo", payload, headers)

    res = conn.getresponse()
    dataBytes = res.read()
    dataJson = json.loads(dataBytes.decode("utf-8"))
    data = dataJson.get('data')

    return data

def update_tracking_details(trackers:list[tuple[str,str]]) -> list[dict]:
    """Return a dictionary of updated tracking information.

    Arguments:

    trackers:

    List of tuples in form of (tracking_number, carrier_code)

    e.g.

    [
        ('1Zxxxxxxx','100002'),
        ('1Zyyyyyyy','100002')
    ]
    
    """

    if len(trackers) == 0:
        return False

    try:
        data = tracker_request('GET',trackers)
    except ValueError:
        raise

    updated_trackers = []
    try:
        for row in data['accepted']:
            tracking = {}
            tracking['carrier_code'] = row['carrier']
            tracking['tracking_number'] = row['number']
            tracking['status'] = row['track_info']['latest_status']['status']
            tracking['sub_status'] = row['track_info']['latest_status']['sub_status']
            tracking['delivery_estimate'] = row['track_info']['time_metrics']['estimated_delivery_date']['from']
            tracking['events'] = row['track_info']['tracking']['providers'][0]['events']
            tracking['events_hash'] = row['track_info']['tracking']['providers'][0]['events_hash']
            tracking['message'] = 'accepted'
            tracking['code'] = 0
            updated_trackers.append(tracking)
    except:
        raise

    return updated_trackers

def get_generated_signature(message:bytes,secret:str):
    """17TRACK verification"""
    src = message.decode('utf-8') + "/" + secret
    digest = hashlib.sha256(src.encode('utf-8')).hexdigest()
    return digest