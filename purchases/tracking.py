from ast import If
import http.client
import json

def create_tracker(slug, tracking_number, api_key):

    conn = http.client.HTTPSConnection("api.aftership.com")

    tracking_dict = {
        'tracking_number':tracking_number,
        'slug':slug
        }

    payload_dict = {'tracking':tracking_dict}

    payload = json.dumps(payload_dict,indent=2)

    headers = {
        'Content-Type': "application/json",
        'aftership-api-key': api_key
        }

    conn.request("POST", "/v4/trackings", payload, headers)

    res = conn.getresponse()
    data = res.read()
    dataJson = json.loads(data.decode("utf-8"))

    tracking = dataJson['data']['tracking']

    meta_code = dataJson['meta']['code']

    if meta_code == 201:
        active = tracking['active'],
        expected_delivery = tracking['expected_delivery'],
        new_slug = tracking['slug'],
        link = tracking['courier_tracking_link']
        status = tracking['tag']
    else:
        active = None
        expected_delivery = None
        new_slug = None
        link = None
        status = None
    

    tracker = {
        "meta-code":meta_code,
        "active":active,
        "expected_delivery":expected_delivery,
        "slug":new_slug,
        "link":link,
        "status":status
    }

    return tracker

def update_tracker(slug, tracking_number, api_key):
    conn = http.client.HTTPSConnection("api.aftership.com")

    headers = {
        'Content-Type': "application/json",
        'aftership-api-key': api_key
        }

    request_str = "/v4/trackings/%s/%s" % (slug,tracking_number)

    conn.request("GET", request_str, headers=headers)

    res = conn.getresponse()
    data = res.read()
    dataJson = json.loads(data.decode("utf-8"))

    tracking = dataJson['data']['tracking']

    tracker = {
        "meta-code":dataJson['meta']['code'],
        "active":tracking['active'],
        "expected_delivery":tracking['expected_delivery'],
        "slug":tracking['slug'],
        "link":tracking['courier_tracking_link'],
        "status":tracking['tag']
    }

    return tracker