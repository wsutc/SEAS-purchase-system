# from ast import If
import http.client
import json

class Tracker:
    def __init__(self, slug, tracking_number, created, api_key):
        self.meta_code = None
        self.message = None
        self.id = None
        self.created_at = None
        self.updated_at = None
        self.last_updated_at = None
        self.tracking_number = None
        self.slug = None
        self.active = None
        self.android = None
        self.custom_fields = None
        self.customer_name = None
        self.delivery_time = None
        self.destination_country_iso3 = None
        self.courier_destination_country_iso3 = None
        self.emails = None
        self.expected_delivery = None
        self.ios = None
        self.note = None
        self.order_id = None
        self.order_date = None
        self.order_id_path = None
        self.origin_country_iso3 = None
        self.shipment_package_count = None
        self.shipment_pickup_date = None
        self.shipment_delivery_date = None
        self.shipment_type = None
        self.shipment_weight = None
        self.shipment_weight_unit = None
        self.signed_by = None
        self.smses = None
        self.source = None
        self.tag = None
        self.subtag = None
        self.subtag_message = None
        self.title = None
        self.tracked_count = None
        self.last_mile_tracking_supported = None
        self.language = None
        self.unique_token = None
        self.checkpoints = None
        self.subscribed_smses = None
        self.subscribed_emails = None
        self.return_to_sender = None
        self.tracking_account_number = None
        self.tracking_origin_country = None
        self.tracking_destination_country = None
        self.tracking_key = None
        self.tracking_postal_code = None
        self.tracking_ship_date = None
        self.tracking_state = None
        self.order_promised_delivery_date = None
        self.delivery_type = None
        self.pickup_location = None
        self.pickup_note = None
        self.courier_tracking_link = None
        self.courier_redirect_link = None
        self.first_attempted_at = None
        self.on_time_status = None
        self.on_time_difference = None
        self.order_tags = None
        self.aftership_estimated_delivery_date = None
        
    def get(slug,tracking_number,created,api_key):
        conn = http.client.HTTPSConnection("api.aftership.com")

        headers = {
            'Content-Type': "application/json",
            'aftership-api-key': api_key
            }

        if not created:                             # do not run if tracker previously created ('POST')
            ## Create payload
            payload = build_payload(slug, tracking_number)
            # ### First, create 'tracking' tag information
            # tracking_dict = {
            #     'tracking_number':tracking_number,
            #     'slug':slug
            #     }

            # ### Second, nest the 'tracking' tag in a larger dict
            # payload_dict = {'tracking':tracking_dict}

            # ### Last, turn the nested dict into json
            # payload = json.dumps(payload_dict,indent=2)

            conn.request("POST", "/v4/trackings", payload, headers)
            
        else:                                       # do request for previously created trackers ('GET')
            request_str = "/v4/trackings/%s/%s" % (slug,tracking_number)
            conn.request("GET", request_str, headers=headers)

        res = conn.getresponse()
        data = res.read()
        dataJson = json.loads(data.decode("utf-8"))

        ## Extract 'tracking' tag to save characters in following lines
        tracking = dataJson['data']['tracking']

        Tracker.meta_code = dataJson['meta']['code']

        if str(Tracker.meta_code).startswith('2'):                   # Implies that request was valid
            Tracker.id = tracking['id']
            Tracker.created_at = tracking['created_at']
            Tracker.updated_at = tracking['updated_at']
            Tracker.last_updated_at = tracking['last_updated_at']
            Tracker.tracking_number = tracking['tracking_number']
            Tracker.slug = tracking['slug']
            Tracker.active = tracking['active']
            Tracker.android = tracking['android']
            Tracker.custom_fields = tracking['custom_fields']
            Tracker.customer_name = tracking['customer_name']
            Tracker.delivery_time = tracking['delivery_time']
            Tracker.destination_country_iso3 = tracking['destination_country_iso3']
            Tracker.courier_destination_country_iso3 = tracking['courier_destination_country_iso3']
            Tracker.emails = tracking['emails']
            Tracker.expected_delivery = tracking['expected_delivery']
            Tracker.ios = tracking['ios']
            Tracker.note = tracking['note']
            Tracker.order_id = tracking['order_id']
            Tracker.order_date = tracking['order_date']
            Tracker.order_id_path = tracking['order_id_path']
            Tracker.origin_country_iso3 = tracking['origin_country_iso3']
            Tracker.shipment_package_count = tracking['shipment_package_count']
            Tracker.shipment_pickup_date = tracking['shipment_pickup_date']
            Tracker.shipment_delivery_date = tracking['shipment_delivery_date']
            Tracker.shipment_type = tracking['shipment_type']
            Tracker.shipment_weight = tracking['shipment_weight']
            Tracker.shipment_weight_unit = tracking['shipment_weight_unit']
            Tracker.signed_by = tracking['signed_by']
            Tracker.smses = tracking['smses']
            Tracker.source = tracking['source']
            Tracker.tag = tracking['tag']
            Tracker.subtag = tracking['subtag']
            Tracker.subtag_message = tracking['subtag_message']
            Tracker.title = tracking['title']
            Tracker.tracked_count = tracking['tracked_count']
            Tracker.last_mile_tracking_supported = tracking['last_mile_tracking_supported']
            Tracker.language = tracking['language']
            Tracker.unique_token = tracking['unique_token']
            Tracker.checkpoints = tracking['checkpoints']
            Tracker.subscribed_smses = tracking['subscribed_smses']
            Tracker.subscribed_emails = tracking['subscribed_emails']
            Tracker.return_to_sender = tracking['return_to_sender']
            Tracker.tracking_account_number = tracking['tracking_account_number']
            Tracker.tracking_origin_country = tracking['tracking_origin_country']
            Tracker.tracking_destination_country = tracking['tracking_destination_country']
            Tracker.tracking_key = tracking['tracking_key']
            Tracker.tracking_postal_code = tracking['tracking_postal_code']
            Tracker.tracking_ship_date = tracking['tracking_ship_date']
            Tracker.tracking_state = tracking['tracking_state']
            Tracker.order_promised_delivery_date = tracking['order_promised_delivery_date']
            Tracker.delivery_type = tracking['delivery_type']
            Tracker.pickup_location = tracking['pickup_location']
            Tracker.pickup_note = tracking['pickup_note']
            Tracker.courier_tracking_link = tracking['courier_tracking_link']
            Tracker.courier_redirect_link = tracking['courier_redirect_link']
            Tracker.first_attempted_at = tracking['first_attempted_at']
            Tracker.on_time_status = tracking['on_time_status']
            Tracker.on_time_difference = tracking['on_time_difference']
            Tracker.order_tags = tracking['order_tags']
            Tracker.aftership_estimated_delivery_date = tracking['aftership_estimated_delivery_date']

        else:
            Tracker.message = dataJson['meta']['message']

        return Tracker

    # def update(instance):
    #     pass

def build_payload(slug, tracking_number):
    ### First, create 'tracking' tag information
    tracking_dict = {
        'tracking_number':tracking_number,
        'slug':slug
    }

    ### Second, nest the 'tracking' tag in a larger dict
    payload_dict = {'tracking':tracking_dict}

    ### Last, turn the nested dict into json
    payload = json.dumps(payload_dict,indent=2)

    return payload