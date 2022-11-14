import hashlib
import http.client
import json
import logging

from benedict import benedict
from django.conf import settings
from django.http import JsonResponse

from purchases.exceptions import (
    TrackerInvalidApiKey,
    TrackerNotRegistered,
    TrackerPreviouslyRegistered,
    TrackerRejectedUnknownCode,
)

# from typing import TypeVar

logger = logging.getLogger(__name__)


def register_trackers(payload: list[tuple[str, str]]) -> dict[list[dict], list[dict]]:
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
        tracker_responses = tracker_request("REGISTER", payload)
    except Exception:
        raise

    accepted_list = []
    for tracker in tracker_responses["accepted"]:

        accepted = {
            "response": True,
            "message": None,
            "tracker": TrackerObject.fromregister(tracker),
        }
        accepted_list.append(accepted)

    rejected_list = []
    for tracker in tracker_responses["rejected"]:
        rejected = {
            "tracker": TrackerObject.fromregister(tracker),
            "code": tracker["error"].get("code", None),
            "message": tracker["error"].get("message", None),
        }
        try:
            if rejected["code"] == -18019901:
                raise TrackerPreviouslyRegistered(
                    rejected["tracker"].tracking_number, rejected["message"]
                )
            else:
                raise TrackerRejectedUnknownCode(
                    rejected["tracker"].tracking_number,
                    rejected["code"],
                    rejected["message"],
                )
        except TrackerPreviouslyRegistered as err:
            rejected["exception"] = err
            rejected_list.append(rejected)
        except TrackerRejectedUnknownCode:
            raise

    return {"accepted": accepted_list, "rejected": rejected_list}


REQUEST_METHODS = (
    "REGISTER",
    "GETLIST",
    "GET",
)


def tracker_request(
    request_method: REQUEST_METHODS, payload: list[tuple]
) -> JsonResponse:
    """Return data based on method from list of trackers.

    payload is a list of tuples containing (tracking_number,carrier_code)

    request_method is one of 'REGISTER,' 'GETLIST,' 'GET.'
    """
    conn = http.client.HTTPSConnection("api.17track.net")

    headers = {
        "Content-Type": "application/json",
        "17token": settings.PYTRACK_17TRACK_KEY,
    }

    payload_dict = []
    for t, c in payload:
        if t and c:
            payload_dict.append(
                {
                    "number": t,
                    "carrier": c,
                }
            )
        elif t:
            payload_dict.append(
                {
                    "number": t,
                }
            )
        else:
            raise ValueError("All trackers MUST have a tracking number.")

    payload = json.dumps(payload_dict)

    match request_method:
        case "REGISTER":
            conn.request("POST", "/track/v2/register", payload, headers)
        case "GETLIST":
            conn.request("POST", "/track/v2/gettracklist", payload, headers)
        case "GET":
            conn.request("POST", "/track/v2/gettrackinfo", payload, headers)

    res = conn.getresponse()
    dataBytes = res.read()
    dataJson = json.loads(dataBytes.decode("utf-8"))
    data = dataJson.get("data")

    return data


def update_tracking_details(trackers: list[tuple[str, str]]) -> list[dict]:
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

    data = tracker_request("GET", trackers)

    updated_trackers = []
    try:
        for row in data["accepted"]:
            tracking = {"tracker": TrackerObject.fromupdateresponse(row)}
            if tracking["tracker"].status != "NotFound":
                tracking["message"] = "accepted"
                tracking["code"] = 0
            else:
                tracking["message"] = "unknown"
                tracking["code"] = -1000
            updated_trackers.append(tracking)
        for row in data["rejected"]:
            row_b = benedict(row)
            match str(row_b["error.code"]):
                case "-18019902":
                    raise TrackerNotRegistered(
                        tracking_number=row_b["number"], message=row_b["error.message"]
                    )
    except KeyError:
        data_b = benedict(data)
        if "errors" in data_b:
            error_code = data_b["errors[0].code"]
            error_message = data_b["errors[0].message"]
            match str(error_code):
                case "-18010002":
                    raise TrackerInvalidApiKey(error_code, error_message)
    else:
        return updated_trackers


def get_generated_signature(message: bytes, secret: str):
    """17TRACK verification"""
    src = message.decode("utf-8") + "/" + secret
    digest = hashlib.sha256(src.encode("utf-8")).hexdigest()
    return digest


class TrackerObject:
    def __init__(self, payload: benedict):
        payload_benedict = benedict(payload)

        self.status = payload_benedict.get_str(["status"])
        self.sub_status = payload_benedict.get_str(["sub_status"])
        self.delivery_estimate = payload_benedict.get_datetime(["estimated_delivery"])
        self.latest_update_time = payload_benedict.get_datetime(
            ["latest_event.time_utc"]
        )
        self.providers_hash = payload_benedict.get_int(["providers_hash"])
        self.carrier_name = payload_benedict.get_str(["carrier.name"])
        self.carrier_code = payload_benedict.get_int(["carrier.code"])
        self.events_hash = payload_benedict.get_int(["events_hash"])
        self.events = payload_benedict.get_list(["events"])
        self.tracking_number = payload_benedict.get_str(["tracking_number"])

        if not self.carrier_name:
            self.carrier_name = self.carrier_code

    @classmethod
    def fromupdateresponse(cls, datadict: dict):
        d = benedict()
        i = benedict(datadict)
        d["tracking_number"] = i.get_str(["number"])
        d["status"] = i.get_str(["track_info.latest_status.status"])
        d["sub_status"] = i.get_str(["track_info.latest_status.sub_status"])
        d["delivery_estimate"] = i.get_datetime(
            ["track_info.time_metrics.estimated_delivery"]
        )
        d["latest_event.time_utc"] = i.get_datetime(
            ["track_info.latest_event.time_utc"]
        )
        d["providers_hash"] = i.get_int(["track_info.tracking.providers_hash"])
        d["carrier.name"] = i.get_str(
            ["track_info.tracking.providers[0].provider.name"]
        )
        d["carrier.code"] = i.get_int(["track_info.tracking.providers[0].provider.key"])
        d["events_hash"] = i.get_int(["track_info.tracking.providers[0].events_hash"])
        d["events"] = i.get_list(["track_info.tracking.providers[0].events"])

        return cls(d)

    @classmethod
    def fromstopresponse(cls, datadict: dict):
        d = benedict()
        i = benedict(datadict)
        d["tracking_number"] = i.get_str(["number"])
        d["carrier.code"] = i.get_int(["carrier"])

        return cls(d)

    @classmethod
    def fromregister(cls, payload: json):
        i = benedict(payload)
        d = benedict()
        d["carrier.code"] = i.get_int("carrier", default=None)
        d["tracking_number"] = i.get_str("number", default=None)

        return cls(d)
