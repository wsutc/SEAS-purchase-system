# from ast import If
import http.client
import json

class Tracker:
    def __init__(self, slug, tracking_number):
        self.active = False

    def create(self, slug, tracking_number, api_key):

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

        self.meta_code = dataJson['meta']['code']
        self.message = dataJson['meta']['message']

        if self.meta_code == 201:
            self.active = tracking['active'],
            self.expected_delivery = tracking['expected_delivery'],
            self.slug = tracking['slug'],
            self.link = tracking['courier_tracking_link']
            self.status = tracking['tag']
        else:
            self.active = None
            self.expected_delivery = None
            self.new_slug = None
            self.link = None
            self.status = None
        
        return self.meta_code
        # meta-code = 

        # tracker = {
        #     "meta-code":meta_code,
        #     "active":active,
        #     "expected_delivery":expected_delivery,
        #     "slug":new_slug,
        #     "link":link,
        #     "status":status
        # }

        # return tracker

    def update(self, slug, tracking_number, api_key):
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

        self.meta_code = dataJson['meta']['code']
        self.message = dataJson['meta']['code']

        self.active = tracking['active']
        self.expected_delivery = tracking['expected_delivery']
        self.slug = tracking['slug']
        self.link = tracking['courier_tracking_link']
        self.status = tracking['tag']

        # tracker = {
        #     "meta-code":dataJson['meta']['code'],
        #     "active":tracking['active'],
        #     "expected_delivery":tracking['expected_delivery'],
        #     "slug":tracking['slug'],
        #     "link":tracking['courier_tracking_link'],
        #     "status":tracking['tag']
        # }

        return self.meta_code