# from ast import If
import http.client, hashlib
import json
from xml.dom import NotFoundErr

from django.conf import settings
# from purchases.models.models_apis import Tracker, TrackingEvent

from purchases.models.models_metadata import Carrier

class TrackerOld:
    # def __init__(self, slug, tracking_number, created, api_key):
    #     self.meta_code = None
    #     self.message = None
    #     self.id = None
    #     self.created_at = None
    #     self.updated_at = None
    #     self.last_updated_at = None
    #     self.tracking_number = None
    #     self.slug = None
    #     self.active = None
    #     self.android = None
    #     self.custom_fields = None
    #     self.customer_name = None
    #     self.delivery_time = None
    #     self.destination_country_iso3 = None
    #     self.courier_destination_country_iso3 = None
    #     self.emails = None
    #     self.expected_delivery = None
    #     self.ios = None
    #     self.note = None
    #     self.order_id = None
    #     self.order_date = None
    #     self.order_id_path = None
    #     self.origin_country_iso3 = None
    #     self.shipment_package_count = None
    #     self.shipment_pickup_date = None
    #     self.shipment_delivery_date = None
    #     self.shipment_type = None
    #     self.shipment_weight = None
    #     self.shipment_weight_unit = None
    #     self.signed_by = None
    #     self.smses = None
    #     self.source = None
    #     self.tag = None
    #     self.subtag = None
    #     self.subtag_message = None
    #     self.title = None
    #     self.tracked_count = None
    #     self.last_mile_tracking_supported = None
    #     self.language = None
    #     self.unique_token = None
    #     self.checkpoints = None
    #     self.subscribed_smses = None
    #     self.subscribed_emails = None
    #     self.return_to_sender = None
    #     self.tracking_account_number = None
    #     self.tracking_origin_country = None
    #     self.tracking_destination_country = None
    #     self.tracking_key = None
    #     self.tracking_postal_code = None
    #     self.tracking_ship_date = None
    #     self.tracking_state = None
    #     self.order_promised_delivery_date = None
    #     self.delivery_type = None
    #     self.pickup_location = None
    #     self.pickup_note = None
    #     self.courier_tracking_link = None
    #     self.courier_redirect_link = None
    #     self.first_attempted_at = None
    #     self.on_time_status = None
    #     self.on_time_difference = None
    #     self.order_tags = None
    #     self.aftership_estimated_delivery_date = None
        
    def get(slug,tracking_number,api_key):
        conn = http.client.HTTPSConnection("api.ship24.com")

        headers = {
            'Content-Type': "application/json",
            'Authorization': "Bearer " + api_key
            }

        # if not created:                             # do not run if tracker previously created ('POST')
            ## Create payload
        payload = build_payload(tracking_number, slug="")
            # ### First, create 'tracking' tag information
            # tracking_dict = {
            #     'tracking_number':tracking_number,
            #     'slug':slug
            #     }

            # ### Second, nest the 'tracking' tag in a larger dict
            # payload_dict = {'tracking':tracking_dict}

            # ### Last, turn the nested dict into json
            # payload = json.dumps(payload_dict,indent=2)

        conn.request("POST", "/public/v1/trackers", payload, headers)
            
        # else:                                       # do request for previously created trackers ('GET')
        #     request_str = "/v4/trackings/%s/%s" % (slug,tracking_number)
        #     conn.request("GET", request_str, headers=headers)

        res = conn.getresponse()
        data = res.read()
        dataJson = json.loads(data.decode("utf-8"))

        ## Extract 'tracking' tag to save characters in following lines
        tracking = dataJson['data']['tracker']

        TrackerOld.meta_code = res.status

        if str(res.status).startswith('2'):                   # Implies that request was valid
            TrackerOld.id = tracking['trackerId']
            TrackerOld.created_at = tracking['createdAt']
            # Tracker.updated_at = tracking['updated_at']
            # Tracker.last_updated_at = tracking['last_updated_at']
            TrackerOld.tracking_number = tracking['trackingNumber']
            # Tracker.slug = tracking['slug']
            # Tracker.active = tracking['active']
            # Tracker.android = tracking['android']
            # Tracker.custom_fields = tracking['custom_fields']
            # Tracker.customer_name = tracking['customer_name']
            # Tracker.delivery_time = tracking['delivery_time']
            # Tracker.destination_country_iso3 = tracking['destination_country_iso3']
            # Tracker.courier_destination_country_iso3 = tracking['courier_destination_country_iso3']
            # Tracker.emails = tracking['emails']
            # Tracker.expected_delivery = tracking['expected_delivery']
            # Tracker.ios = tracking['ios']
            # Tracker.note = tracking['note']
            # Tracker.order_id = tracking['order_id']
            # Tracker.order_date = tracking['order_date']
            # Tracker.order_id_path = tracking['order_id_path']
            # Tracker.origin_country_iso3 = tracking['origin_country_iso3']
            # Tracker.shipment_package_count = tracking['shipment_package_count']
            # Tracker.shipment_pickup_date = tracking['shipment_pickup_date']
            # Tracker.shipment_delivery_date = tracking['shipment_delivery_date']
            # Tracker.shipment_type = tracking['shipment_type']
            # Tracker.shipment_weight = tracking['shipment_weight']
            # Tracker.shipment_weight_unit = tracking['shipment_weight_unit']
            # Tracker.signed_by = tracking['signed_by']
            # Tracker.smses = tracking['smses']
            # Tracker.source = tracking['source']
            # Tracker.tag = tracking['tag']
            # Tracker.subtag = tracking['subtag']
            # Tracker.subtag_message = tracking['subtag_message']
            # Tracker.title = tracking['title']
            # Tracker.tracked_count = tracking['tracked_count']
            # Tracker.last_mile_tracking_supported = tracking['last_mile_tracking_supported']
            # Tracker.language = tracking['language']
            # Tracker.unique_token = tracking['unique_token']
            # Tracker.checkpoints = tracking['checkpoints']
            # Tracker.subscribed_smses = tracking['subscribed_smses']
            # Tracker.subscribed_emails = tracking['subscribed_emails']
            # Tracker.return_to_sender = tracking['return_to_sender']
            # Tracker.tracking_account_number = tracking['tracking_account_number']
            # Tracker.tracking_origin_country = tracking['tracking_origin_country']
            # Tracker.tracking_destination_country = tracking['tracking_destination_country']
            # Tracker.tracking_key = tracking['tracking_key']
            # Tracker.tracking_postal_code = tracking['tracking_postal_code']
            # Tracker.tracking_ship_date = tracking['tracking_ship_date']
            # Tracker.tracking_state = tracking['tracking_state']
            # Tracker.order_promised_delivery_date = tracking['order_promised_delivery_date']
            # Tracker.delivery_type = tracking['delivery_type']
            # Tracker.pickup_location = tracking['pickup_location']
            # Tracker.pickup_note = tracking['pickup_note']
            # Tracker.courier_tracking_link = tracking['courier_tracking_link']
            # Tracker.courier_redirect_link = tracking['courier_redirect_link']
            # Tracker.first_attempted_at = tracking['first_attempted_at']
            # Tracker.on_time_status = tracking['on_time_status']
            # Tracker.on_time_difference = tracking['on_time_difference']
            # Tracker.order_tags = tracking['order_tags']
            # Tracker.aftership_estimated_delivery_date = tracking['aftership_estimated_delivery_date']

        # else:
            # Tracker.message = dataJson['meta']['message']

        return TrackerOld

    # def update(instance):
    #     pass

def build_payload(tracking_number, slug):
    ### First, create 'tracking' tag information
    tracking_dict = {
        'trackingNumber':tracking_number,
    }

    if slug:
        tracking_dict['courierCode'] = slug

    payload = json.dumps(tracking_dict,indent=2)

    return payload

def register_tracker(tracking_number:str, carrier_code:str = None) -> tuple[str,str,str,bool]:
    """Register tracker if it doesn't already exist
    
    Response is a tuple

    tracking number

    carrier as carrier_code

    message

    true/false of whether tracker was created
    """
    conn = http.client.HTTPSConnection("api.17track.net")

    headers = {
        'Content-Type': "application/json",
        '17token': settings._17TRACK_KEY
        }

    payload_dict = [{
        "number": tracking_number
    }]
    if carrier_code:
        payload_dict[0]['carrier'] = carrier_code
    
    payload = json.dumps(payload_dict)

    conn.request("POST", "/track/v2/register", payload, headers)

    res = conn.getresponse()
    dataBytes = res.read()
    dataJson = json.loads(dataBytes.decode("utf-8"))

    # code = dataJson.get('code')
    data = dataJson.get('data')
    response = False            #set to false as default value
    try:
        for row in data['accepted']:
            response = True
            message = None
            returned_carrier_code = row['carrier']
            # returned_carrier, _ = Carrier.objects.get_or_create(
            #     carrier_code = returned_carrier_code,
            #     defaults = {
            #         'name': returned_carrier_code
            #     }
            # )
            carrier_code = returned_carrier_code
            number = row['number']
        if response != True:
            number,carrier_code,message,response = get_tracker(tracking_number,carrier_code)
    except:
        raise

    tuple = (number,carrier_code,message,response)

    return tuple

REQUEST_METHODS = (
    'REGISTER',
    'GETLIST',
    'GET',
)

def tracking(request_method:REQUEST_METHODS ):
    pass

def get_tracker(tracking_number:str, carrier_code:str = None):
    conn = http.client.HTTPSConnection("api.17track.net")

    headers = {
        'Content-Type': "application/json",
        '17token': settings._17TRACK_KEY
        }

    payload_dict = {
        "number": tracking_number
    }
    if carrier_code:
        payload_dict['carrier'] = carrier_code
    
    payload = json.dumps(payload_dict)

    conn.request("POST", "/track/v2/gettracklist", payload, headers)

    res = conn.getresponse()
    dataBytes = res.read()
    dataJson = json.loads(dataBytes.decode("utf-8"))

    # code = dataJson.get('code')
    data = dataJson.get('data')
    response = False            #set to false as default value
    try:
        for row in data['accepted']:
            response = True
            message = None
            returned_carrier_code = row['carrier']
            # returned_carrier, _ = Carrier.objects.get_or_create(
            #     carrier_code = returned_carrier_code,
            #     defaults = {
            #         'name': returned_carrier_code
            #     }
            # )
            carrier = returned_carrier_code
            number = row['number']
        if response != True:
            rejected = data['rejected'][0]
            message = rejected['error']['message']
            number = rejected['number']
    except:
        raise

    tuple = (number,carrier,message,response)

    return tuple

def update_tracking_details(tracking_number:str, carrier_code:str):

    if tracking_number == None:
        return False

    conn = http.client.HTTPSConnection("api.17track.net")

    headers = {
        'Content-Type': "application/json",
        '17token': settings._17TRACK_KEY
        }

    payload_dict = [{
        "number": tracking_number,
        "carrier": carrier_code
    }]
    
    payload = json.dumps(payload_dict)

    conn.request("POST", "/track/v2/gettrackinfo", payload, headers)

    res = conn.getresponse()
    dataBytes = res.read()
    dataJson = json.loads(dataBytes.decode("utf-8"))

    # code = dataJson.get('code')
    data = dataJson.get('data')
    # response = False            #set to false as default value
    tracking = {}
    try:
        for row in data['accepted']:
            # response = True
            # message = None
            returned_carrier_code = row['carrier']
            tracking['carrier_code'] = returned_carrier_code
            tracking['tracking_number'] = row['number']
            tracking['status'] = row['track_info']['latest_status']['status']
            tracking['sub_status'] = row['track_info']['latest_status']['sub_status']
            tracking['delivery_estimate'] = row['track_info']['time_metrics']['estimated_delivery_date']['from']
            tracking['events'] = row['track_info']['tracking']['providers'][0]['events']
            tracking['events_hash'] = row['track_info']['tracking']['providers'][0]['events_hash']
            tracking['message'] = 'accepted'
            tracking['code'] = 0


        for row in data['rejected']:
            tracking['carrier_code'] = carrier_code
            tracking['number'] = tracking_number
            tracking['message'] = row['error']['message']
            tracking['code'] = row['error']['code']

        # if response != True:
        #     # rejected = data['rejected'][0]
        #     message = data['rejected'][0]['error']['message']
        #     # number = rejected['number']
        #     raise Exception(message)
    except:
        raise

    return tracking

def bulk_update_tracking_details(trackers:list[tuple]):

    if len(trackers) == 0:
        return False

    conn = http.client.HTTPSConnection("api.17track.net")

    headers = {
        'Content-Type': "application/json",
        '17token': settings._17TRACK_KEY
        }

    payload_dict = []
    for t,c in trackers:
        if t:
            payload_dict.append({
                "number": t,
                "carrier": c
            })
    
    payload = json.dumps(payload_dict)

    conn.request("POST", "/track/v2/gettrackinfo", payload, headers)

    res = conn.getresponse()
    dataBytes = res.read()
    dataJson = json.loads(dataBytes.decode("utf-8"))

    # code = dataJson.get('code')
    data = dataJson.get('data')
    # response = False            #set to false as default value
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