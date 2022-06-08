import http.client
import json

def create_tracker(slug, tracking_number):

    conn = http.client.HTTPSConnection("api.aftership.com")

    tracking_dict = {
        'tracking_number':tracking_number,
        'slug':slug
        }

    payload_dict = {'tracking':json.dumps(tracking_dict)}

    payload_dump = json.dumps(payload_dict)

    payload = "{\n  \"tracking\": {\n    \"tracking_number\": \"" + tracking_number + " \",\n    \"slug\": \"" + slug + "\",\n    \"title\": \"Title Name\",\n    \"smses\": [\n      \"+18555072509\",\n      \"+18555072501\"\n    ],\n    \"emails\": [\n      \"karl.wooster@wsu.edu\",\n      \"another_email@yourdomain.com\"\n    ],\n    \"order_id\": \"ID 1234\",\n    \"order_number\": \"1234\",\n    \"order_id_path\": \"http://www.aftership.com/order_id=1234\",\n    \"custom_fields\": {\n      \"product_name\": \"iPhone Case\",\n      \"product_price\": \"USD19.99\"\n    },\n    \"language\": \"en\",\n    \"order_promised_delivery_date\": \"2019-05-20\",\n    \"delivery_type\": \"pickup_at_store\",\n    \"pickup_location\": \"Flagship Store\",\n    \"pickup_note\": \"Reach out to our staffs when you arrive our stores for shipment pickup\"\n  }\n}"

    headers = {
        'Content-Type': "application/json",
        'aftership-api-key': "dcbad674-9232-4bd1-b3fb-eceac9cad026"
        }

    conn.request("POST", "/v4/trackings", payload, headers)

    res = conn.getresponse()
    data = res.read()
    dataJson = json.loads(data.decode("utf-8"))

    tracking = dataJson['data']['tracking']

    tracker = {
        "meta-code":dataJson['meta']['code'],
        "active":tracking['active'],
        "expected_delivery":tracking['expected_delivery'],
        "slug":tracking['slug'],
        "link":tracking['courier_tracking_link']
    }

    return tracker

def update_tracker(slug, tracking_number):
    conn = http.client.HTTPSConnection("api.aftership.com")

    headers = {
        'Content-Type': "application/json",
        'aftership-api-key': "dcbad674-9232-4bd1-b3fb-eceac9cad026"
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
        "link":tracking['courier_tracking_link']
    }

    return tracker