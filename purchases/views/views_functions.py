import csv
import datetime as dt
import io
import json
import logging
from functools import partial

from benedict import benedict
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import mail_admins
from django.db.transaction import atomic, non_atomic_requests
from django.http import (
    FileResponse,
    HttpRequest,
    HttpResponse,
    HttpResponseForbidden,
    JsonResponse,
)
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from furl import furl
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm, inch
from reportlab.pdfgen import canvas
from reportlab.platypus import PageTemplate, SimpleDocTemplate, Table, TableStyle
from reportlab.platypus.frames import Frame
from reportlab.platypus.paragraph import Paragraph

from purchases.exceptions import TrackerInvalidApiKey, TrackerNotRegistered
from purchases.models import (
    Balance,
    Carrier,
    PurchaseRequest,
    SimpleProduct,
    Status,
    Tracker,
    TrackingWebhookMessage,
    Vendor,
)
from purchases.tracking import (
    TrackerObject,
    get_generated_signature,
    update_tracking_details,
)
from web_project.helpers import login_exempt, redirect_to_next, truncate_string

# from web_project.timer import Timer

logger = logging.getLogger(__name__)


# Create your views here.


def update_pr_status(request: HttpRequest, slug: str, *args, **kwargs) -> HttpResponse:
    new_status = request.GET.get("status")

    redirect_url = redirect_to_next(request, "purchaserequest_detail", slug=slug)

    return_redirect = redirect(redirect_url)

    if not new_status:
        messages.info(_("existing status chosen, no changes made."))
        return return_redirect

    status = Status.objects.filter(pk=new_status).first()

    qs = PurchaseRequest.objects.filter(slug=slug)

    count = qs.count()

    if count == 1:
        qs.update(status=status)
        messages.add_message(
            request,
            messages.SUCCESS,
            message=f"{qs.first()}'s status updated to '{status.name.title()}.'",
        )

    else:
        logger.warning(
            f"Slug {slug} returned too many/too few results: {count}; no records updated.",  # noqa: E501
        )
        messages.add_message(
            request,
            messages.ERROR,
            message=f"Slug returned too many/too few results: {count}; no records updated.",  # noqa: E501
        )

    return return_redirect


def flush_old_webhooks(days_offset: int) -> int:
    deleted, _ = TrackingWebhookMessage.objects.filter(
        received_at__lte=timezone.now() - dt.timedelta(days=days_offset),
    ).delete()

    return deleted


@login_exempt
@csrf_exempt
@require_POST
@non_atomic_requests
def tracking_webhook(request):
    if request.method == "HEAD":
        response = HttpResponse(
            "Message successfully received.",
            content_type="text/plain",
        )
        return response

    try:
        secret = settings.PYTRACK_17TRACK_KEY

    except AttributeError:
        logger.warning("Tracking API Key not set.", exc_info=1)

    else:
        given_token = request.headers.get("sign", "")

        if (token := get_generated_signature(request.body, secret)) != given_token:
            logger.warning(
                f"Invalid tracking webhook request received | token: {token}",
            )
            mail_admins(
                subject="SEAS-Purchase-System: Invalid Tracking Webhook",
                message=f"Token does not match signature: {given_token}",
            )

            return HttpResponseForbidden(
                "Inconsistency in response signature.",
                content_type="text/plain",
            )

        payload = json.loads(request.body)

        TrackingWebhookMessage.objects.create(
            received_at=timezone.now(),
            payload=payload,
        )

        try:
            success, message = process_webhook_payload(payload)

            if success:
                logger.info(message)

            else:
                logger.warning(message)

        except ObjectDoesNotExist:
            logger.error("No object matching payload found", exc_info=1)
            mail_admins(
                subject="Unrecognized Webhook Payload",
                message=payload,
            )

    finally:
        count = flush_old_webhooks(days_offset=7)

        if count > 0:
            logger.info(f"Webhook Messages Deleted: {count}")

        else:
            logger.info("No Webhook Messages Deleted.")

    return HttpResponse("Message successfully received.", content_type="text/plain")


@atomic
def process_webhook_payload(payload: dict) -> str:
    event_type = payload.get("event")

    if event_type == "TRACKING_UPDATED":
        payload_obj = TrackerObject.fromupdateresponse(payload.get("data"))

        try:
            carrier, _ = Carrier.objects.get_or_create(
                carrier_code=payload_obj.carrier_code,
                defaults={"name": payload_obj.carrier_name},
            )

            tracker, _ = Tracker.objects.get_or_create(
                tracking_number=payload_obj.tracking_number,
                carrier=carrier,
            )

        except ObjectDoesNotExist:
            raise

        if tracker.events_hash != str(payload_obj.events_hash):
            _, _ = tracker.create_events(payload_obj.events)

        success = tracker.update_tracker_fields(payload_obj)

        tracker_success = f"Tracker {tracker} successfully updated."

        tracker_failure = f"No updates made to tracker {tracker}."

        return success, tracker_success if success else tracker_failure

    elif event_type == "TRACKING_STOPPED":  # noqa: RET505
        payload_obj = TrackerObject.fromstopresponse(payload.get("data"))

        try:
            carrier = Carrier.objects.get(carrier_code=payload_obj.carrier_code)

            tracker = Tracker.objects.get(
                tracking_number=payload_obj.tracking_number,
                carrier=carrier,
            )

        except ObjectDoesNotExist:
            raise

        stop = tracker.stop()

        success_message = f"Tracker {tracker} successfully stopped."

        failure_message = "No trackers stopped."

        return stop, success_message if stop else failure_message

    return None


# def generate_csv(model, filename, column_headers, column_value_objects):
#     qs = model.objects.all()

#     response = HttpResponse(
#         content_type="text/scv",
#         headers={
#             "Content-Disposition": f"attachment; filename={filename}",
#         },
#     )

#     # column_headers = [column.fiel]

#     writer = csv.writer(response)
#     writer.writerow(column_headers)


def generate_csv_prs(request):
    qs_purchase_request = PurchaseRequest.objects.all()

    current_datetime = dt.datetime.now()
    export_filename = f"csv_export_{current_datetime.strftime('%Y%m%d-%H%M%S')}"

    response_pr = HttpResponse(
        content_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={export_filename}_pr.csv",  # noqa: E501
        },
    )

    pr_writer = csv.writer(response_pr)
    pr_writer.writerow(
        [
            "Number",
            "Requisitioner",
            "Created Date",
            "Vendor",
            "Status",
            "Subtotal",
            "Shipping",
            "Sales Tax",
            "Grand Total",
            "Justification",
            "Special Instructions",
        ],
    )
    for purchase_request in qs_purchase_request:
        pr_writer.writerow(
            [
                purchase_request.number,
                purchase_request.requisitioner,
                purchase_request.created_date.date(),
                purchase_request.vendor.natural_key(),
                purchase_request.status.natural_key(),
                purchase_request.subtotal,
                purchase_request.shipping,
                purchase_request.sales_tax,
                purchase_request.grand_total,
                purchase_request.justification,
                purchase_request.instruction,
            ],
        )

    return response_pr


def generate_csv_vendors(request):
    qs_vendor = Vendor.objects.all()

    current_datetime = dt.datetime.now()
    export_filename = f"csv_export_{current_datetime.strftime('%Y%m%d-%H%M%S')}"

    response_vd = HttpResponse(
        content_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={export_filename}_vendor.csv",  # noqa: E501
        },
    )

    vendor_writer = csv.writer(response_vd)
    vendor_writer.writerow(
        [
            "Name",
            "URL",
            "Email",
            "Phone Number",
        ],
    )
    for vendor in qs_vendor:
        vendor_writer.writerow(
            [
                vendor.name,
                vendor.website,
                vendor.email,
                vendor.phone,
            ],
        )

    return response_vd


def generate_csv_items(request):
    qs_items = SimpleProduct.objects.all()

    current_datetime = dt.datetime.now()
    export_filename = f"csv_export_{current_datetime.strftime('%Y%m%d-%H%M%S')}"

    response_items = HttpResponse(
        content_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={export_filename}_items.csv",  # noqa: E501
        },
    )

    items_writer = csv.writer(response_items)
    items_writer.writerow(
        [
            "Name",
            "Vendor",
            "Part/MFG Number",
            "Link",
            "Manufacturer",
            "Price",
            "Quantity",
            "Taxable",
            "Purchase Request",
        ],
    )

    for item in qs_items:
        items_writer.writerow(
            [
                item.name,
                item.vendor.natural_key(),
                item.identifier,
                item.link,
                item.manufacturer,
                item.unit_price,
                item.quantity,
                item.taxable,
                item.purchase_request.natural_key(),
            ],
        )

    return response_items


def generate_pr_pdf(request, slug):
    purchase_request = PurchaseRequest.objects.get(slug=slug)

    buffer = io.BytesIO()

    def header(canvas: canvas, doc, content):
        """Creates header from flowable?"""

        canvas.saveState()

        w, h = content.wrap(doc.width, doc.topMargin)

        content.drawOn(
            canvas,
            doc.leftMargin,
            doc.height + doc.bottomMargin + doc.topMargin - h,
        )

        canvas.restoreState()

    def footer(canvas: canvas, doc, content):
        """Creates footer from flowable?"""

        canvas.saveState()

        w, h = content.wrap(doc.width, doc.bottomMargin)

        content.drawOn(canvas, doc.leftMargin, h)

        canvas.restoreState()

    def header_and_footer(canvas: canvas, doc, header_content, footer_content):
        """Need to build both header AND footer in same function"""

        header(canvas, doc, header_content)

        footer(canvas, doc, footer_content)

    styles = getSampleStyleSheet()

    styles_title = styles["Title"]

    styles_title.name = "Header-Title"

    styles_title.fontSize = 40

    styles_title.textColor = colors.HexColor("#CA1237")

    # Set header styles

    styles.add(styles_title)

    # style_header_normal = styles['Normal']

    # style_header_title = styles['Title']

    # style_header_title.fontSize = 40

    # Set footer styles

    # style_footer_normal = styles['Normal']

    filename = purchase_request.number + ".pdf"

    doc = SimpleDocTemplate(buffer, pagesize=letter, title=purchase_request.number)

    doc.leftMargin = doc.rightMargin = 1 * cm

    # doc.rightMargin = 42

    doc.width = doc.pagesize[0] - doc.leftMargin - doc.rightMargin

    frame = Frame(
        doc.leftMargin,
        doc.bottomMargin,
        doc.width,
        doc.height,
        id="normal",
    )  # , showBoundary=1)

    header_content = Paragraph(purchase_request.number, styles["Header-Title"])

    footer_content = Paragraph("This is a footer", styles["Normal"])

    template = PageTemplate(
        id="test",
        frames=frame,
        onPage=partial(
            header_and_footer,
            header_content=header_content,
            footer_content=footer_content,
        ),
    )

    doc.addPageTemplates([template])

    elements = []

    # Define purchase request information table

    info_column_widths = [0.9 * inch, 2.4 * inch, 0.9 * inch, 2.4 * inch]

    vendor = purchase_request.vendor

    address_line = ""

    if hasattr(vendor.state, "abbreviation"):
        address_line += str(vendor.state.abbreviation)

        if city := vendor.city:
            address_line = str(city) + ", " + address_line + " " + str(vendor.zip)

            if street2 := vendor.street2:
                address_line = str(street2) + "\n" + address_line

            if street1 := vendor.street1:
                address_line = str(street1) + "\n" + address_line

    info_data = [
        [
            "Needed By",
            purchase_request.need_by_date,
            "Requestor",
            purchase_request.requisitioner.user.get_full_name(),
        ],
        [
            "Vendor",
            purchase_request.vendor.name,
            "Email",
            purchase_request.requisitioner.user.email,
        ],
        [
            "Address",
            address_line,
            "Phone",
            purchase_request.requisitioner.phone,
        ],
        ["", "", "Department", purchase_request.requisitioner.department.code],
        ["Phone", purchase_request.vendor.phone],
        ["Email", purchase_request.vendor.email],
        ["Website", purchase_request.vendor.website],
    ]

    info_table = Table(info_data, info_column_widths)

    info_table.setStyle(
        TableStyle(
            [
                # ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
                # ('ALIGN',(0,0),(-1,0),'CENTER'),
                # ('LINEBELOW',(0,0),(-1,-1),0.5,colors.black),
                # ('FONTNAME',(0,1),(-1,0),'Helvetica'),
                # ('ALIGN',(1,1),(-3,-1),'CENTER'),
                ("ALIGN", (0, 0), (0, -1), "RIGHT"),
                ("VALIGN", (0, 2), (1, 2), "TOP"),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("ALIGN", (2, 0), (2, -1), "RIGHT"),
                ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
                ("SPAN", (0, 2), (0, 3)),
                ("SPAN", (1, 2), (1, 3)),
                # ('ROWBACKGROUNDS',(0,1),(-1,-5),[colors.aliceblue,colors.white]),
                # ('BOX',(0,0),(-1,-1),0.5,colors.black),
                ("SPAN", (2, 4), (-1, -1)),
                # ('INNERGRID',(0,0),(-1,-5),0.1,colors.darkgray),
                # ('BOX',(-3,-4),(-1,-1),0.5,colors.black),
                # ('ALIGN',(-3,-4),(-1,-1),'RIGHT'),
                # ('LINEABOVE',(-3,-1),(-1,-1),0.1,colors.darkgray),
                # ('SPAN',(0,-4),(3,-1)),
                # ('SPAN',(-3,-4),(-2,-4))
            ],
        ),
    )

    elements.append(info_table)

    # Define Table

    data = [
        [
            "Description",
            "Identifier",
            "Vendor ID",
            "QTY",
            "Unit",
            "Price",
            "Ext. Price",
        ],
    ]

    # Create rows for each item

    data = append_as_list(data, item_rows(purchase_request))

    # Create rows showing subtotal, shipping, tax, and grand total

    total_rows = [
        ["", "", "", "", "", "Subtotal", purchase_request.subtotal],
        ["", "", "", "", "", "Shipping", purchase_request.shipping],
        ["", "", "", "", "", "Tax", purchase_request.sales_tax],
        ["", "", "", "", "", "Grand Total", purchase_request.grand_total],
    ]

    data = append_as_list(data, total_rows)

    # Create a 'standardized width' [sw] that is 1% of the doc.width

    sw = doc.width / 100

    # Use the sw to generate a table that is exactly the same width as doc.width

    column_widths = [
        38 * sw,
        14 * sw,
        14 * sw,
        7 * sw,
        7 * sw,
        8 * sw,
        12 * sw,
    ]

    items_table = Table(data, colWidths=column_widths)  # Create table

    # Set style for table and rows

    items_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                ("LINEBELOW", (0, 0), (-1, 0), 0.5, colors.black),
                ("FONTNAME", (0, 1), (-1, 0), "Helvetica"),
                ("ALIGN", (1, 1), (-3, -1), "CENTER"),
                ("ALIGN", (-2, 1), (-1, -5), "RIGHT"),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -5),
                    [colors.aliceblue, colors.white],
                ),
                ("BOX", (0, 0), (-1, -5), 0.5, colors.black),
                ("INNERGRID", (0, 0), (-1, -5), 0.1, colors.darkgray),
                # ('BOX',(-3,-4),(-1,-1),0.5,colors.black),
                ("ALIGN", (-3, -4), (-1, -1), "RIGHT"),
                ("LINEABOVE", (-3, -1), (-1, -1), 0.1, colors.darkgray),
                # ('SPAN',(0,-4),(3,-1)),
                # ('SPAN',(-3,-4),(-2,-4))
            ],
        ),
    )

    # Add items_table to 'elements' list

    elements.append(items_table)

    doc.build(elements)

    # doc.showPage()

    # doc.save()

    buffer.seek(0)

    return FileResponse(buffer, as_attachment=True, filename=filename)


# ------------------ NOT CURRENTLY USED ----------------------------

# def get_image(filename: str, url: str):

#     """Get an image for the PDF"""

#     if not os.path.exists(filename):

#         response = HttpResponse()


def append_as_list(data: list[list:str], list: list[list:str]):
    for i in list:
        data.append(i)

    return data


def item_rows(purchase_request: PurchaseRequest):
    """Create nested list of items to be used in a table"""

    items = purchase_request.simpleproduct_set.all()

    rows = []

    for i in items:
        row = [
            truncate_string(i.name, 40),
            i.identifier,
            "",
            i.quantity,
            i.unit,
            i.unit_price,
            i.extended_price,
        ]

        rows.append(row)

    return rows


def fill_pr_pdf(request, purchase_request: PurchaseRequest):
    pass


def update_balance(request, pk: int):
    balance = get_object_or_404(Balance, pk=pk)

    balance.recalculate_balance()

    return redirect("balances_list")


def update_tracker(request, pk, *args, **kwargs):
    fragment = furl(request.get_full_path())

    # TODO(karl): not properly identifying whether any new information was obtained
    # https://github.com/wsutc/SEAS-purchase-system/issues/153
    tracker = get_object_or_404(Tracker, pk=pk)

    try:
        if tracker.carrier:
            response = update_tracking_details(
                [(tracker.tracking_number, tracker.carrier.carrier_code)],
            )

        else:
            response = update_tracking_details([(tracker.tracking_number, None)])

        data = next(iter(response or []), None)

    except TrackerInvalidApiKey:
        logger.warning("Tracking API Key not set or invalid.", exc_info=1)

        messages.error(request, "API key not set, please contact site admin.")

    except TrackerNotRegistered:
        logger.info(f"Tracker '{tracker.tracking_number}' expected to be registered.")

        messages.warning(
            request,
            f"Tracker for '{tracker.tracking_number}' not registered, please register.",
        )

    except Exception:
        messages.error(
            request,
            "Unknown error updating tracker, please contact site admin.",
        )

        logger.error("Unknown exception running `update_tracker`.", exc_info=1)

    else:
        data_b = benedict(data)

        if data_b.get("code") == 0:
            tracker_obj = data_b.get("tracker")

            if tracker_obj.events_hash != tracker.events_hash:
                _, _ = tracker.create_events(tracker_obj.events)

            tracker_str = tracker.tracking_number.upper()

            count = tracker.update_tracker_fields(tracker_obj)

            if count:
                messages.success(
                    request,
                    f"Tracker '{tracker_str}' updated with new information.",
                )

            # elif tracker_obj.status == "NotFound":

            #     messages.warning(

            #         request,

            #         "Tracker '{tracker_str}' was not found, please check the tracking\

            #             number and carrier ({tracker_obj.carrier_name}).",

            #     )

            else:
                messages.info(
                    request,
                    f"Tracker '{tracker_str}' was already up to date.",
                )

        elif data_b.get("code") == -1000:
            messages.warning(
                request,
                f"Tracker '{tracker.tracking_number}' was not found, please check the tracking number and carrier ({tracker.carrier.name}).",  # noqa: E501
            )

    finally:
        url = tracker if "next" not in fragment.args else fragment.args.get("next")

    return redirect(url)


def update_purchase_request_totals(request, slug):
    redirect_url = redirect_to_next(request, "purchaserequest_detail", slug=slug)

    return_redirect = redirect(redirect_url)

    purchase_request = PurchaseRequest.objects.get(slug=slug)

    try:
        subtotal, tax, grand_total = purchase_request.update_totals()

        messages.success(
            request,
            "Purchase request totals updated ->\n"
            + f"Subtotal: {subtotal}; Sales Tax: {tax}; Grand Total: {grand_total}",
        )

    except Exception as err:
        messages.error(
            request,
            f"Unable to update total of purchase request {purchase_request.number}\n"
            + f"{err}",
        )

    return return_redirect


def purchaserequest_list_json(request):
    class SimpleObject:
        def __init__(
            self,
            input_dict: dict,
            base_model: str,
            view_name: str,
            name_dict: dict = None,
        ) -> None:
            self.input = input_dict
            if not name_dict:
                name_dict = {
                    "name": "name",
                    "slug": "slug",
                }
            self.name = input_dict.get(f"{base_model}__{name_dict.get('name')}")
            self.pk = input_dict.get(base_model)
            self.slug = input_dict.get(f"{base_model}__{name_dict.get('slug')}")
            self.view_name = view_name

        def get_url(self):
            return reverse(self.view_name, kwargs={"pk": self.pk, "slug": self.slug})

    pre_json = []
    for pr in (
        PurchaseRequest.objects.all()
        .values(
            "number",
            "grand_total",
            "requisitioner",
            "requisitioner__user__username",
            "requisitioner__slug",
            "vendor",
            "vendor__name",
            "vendor__slug",
            "status__name",
        )
        .iterator()
    ):
        vendor = SimpleObject(pr, "vendor", "vendor_detail")
        requisitioner = SimpleObject(
            pr,
            "requisitioner",
            "requisitioner_detail",
            name_dict={"name": "user__username", "slug": "slug"},
        )

        pre_json += [
            {
                "number": pr.get("number"),
                "requisitioner_name": requisitioner.name,
                "requisitioner_url": requisitioner.get_url(),
                "vendor": vendor.name,
                "vendor_url": vendor.get_url(),
                "status": pr.get("status__name"),
                "grand_total": pr.get("grand_total"),
                "shipping_status": "n/a",
            },
        ]

    return JsonResponse(pre_json, safe=False)
