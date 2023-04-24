import logging

from celery import Task

from purchases.models import Carrier, Tracker

from .tracking import update_tracking_details

logger = logging.getLogger(__name__)


@Task()
def update_all_trackers():
    # Get all undelivered trackers
    undelivered_trackers = Tracker.objects.filter(received=0)

    if undelivered_trackers.count() == 0:
        logger.info("No unreceived trackers found.")
        return

    tracker_list = []
    for q in undelivered_trackers:
        d = (q.tracking_number, q.carrier.carrier_code)
        tracker_list.append(d)
    # tracker_list = (
    #     (q.tracking_number, q.carrier.carrier_code) for q in undelivered_trackers
    # )

    try:
        updated_trackers = update_tracking_details(tracker_list)
    except ValueError as err:
        logger.exception(err)

    if updated_trackers:
        tracker_objs = []
        event_update_count = 0
        for t in updated_trackers:
            t = t["tracker"]
            carrier = Carrier.objects.get(carrier_code=t.carrier_code)
            t_obj = Tracker.objects.get(
                tracking_number=t.tracking_number, carrier=carrier
            )
            t_obj.status = t.status
            t_obj.sub_status = t.sub_status
            t_obj.delivery_estimate = t.delivery_estimate
            t_obj.events = t.events

            events_hash = t.events_hash

            if t_obj.events_hash != str(events_hash):
                event_update_count += 1
                _, _ = t_obj.create_events(t.events)
                t_obj.events_hash = t.events_hash

            tracker_objs.append(t_obj)

        update_count = Tracker.objects.bulk_update(
            tracker_objs,
            ["status", "sub_status", "delivery_estimate", "events", "events_hash"],
        )

        if update_count == 0:
            logger.info("No updates found.")
        elif update_count == 1:
            logger.info(f"{update_count:d} object updated.")
        else:
            logger.info(f"{update_count:d} objects updated.")
