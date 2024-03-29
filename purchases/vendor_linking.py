# import requests
from furl import furl

from .models import Vendor


def link_from_identifier(identifier: str, vendor: Vendor) -> str:
    """Uses vendor parameter to determine correct tool for building string.

    Returns the appropriate link or None if nothing works."""
    # vendor_name = vendor.name
    # match vendor_name:
    #     case "Amazon":
    #         link = Amazon.link_from_identifier(identifier)
    #     case "Tormach":
    #         link = Tormach.link_from_identifier(identifier)
    #     case "CDW-G":
    #         link = CDWG.link_from_identifier(identifier)
    #     case "McMaster-Carr":
    #         link = McMaster.link_from_identifier(identifier)
    #     case "MSC":
    #         link = MSC.link_from_identifier(identifier)
    #     case "LittleMachineShop.com":
    #         link = LittleMachineShop.link_from_identifier(identifier)
    #     case _:
    #         link = None

    format_string = vendor.product_link

    if format_string:
        link = format_string.replace("{number}", identifier)
        return link
    else:
        return ""


class VendorBaseClass:
    base_url = furl("https://tricities.wsu.edu/")

    def link_from_identifier(self, identifer: str) -> str:
        return identifer


class Amazon(VendorBaseClass):
    """Define any methods related to connections to Amazon's website."""

    base_url = furl("https://www.amazon.com/dp/")

    def link_from_identifier(self, identifier: str) -> str:
        """Return the complete URL to an item given it's ASIN."""

        url = Amazon.base_url

        if identifier:
            url /= identifier

        return url


class Tormach(VendorBaseClass):
    """Define any methods related to connections to Tormach's website.
    Unfortunately, it doesn't appear that Tormach has an easy way to determine this.
    Use their search URL instead.
    """

    base_url = furl("https://tormach.com/")

    def link_from_identifier(self, identifier: str) -> str:
        """Returns a query based on the number."""

        url = Tormach.base_url

        if identifier:
            url /= "search"
            url.args["q"] = identifier

        return url


class CDWG(VendorBaseClass):
    """Define any methods related to connections to CDW-G's website."""

    base_url = furl("https://www.cdwg.com/")

    def link_from_identifier(self, identifier: str) -> str:
        """Returns a query based on the number. Often redirects to product page."""

        url = CDWG.base_url

        if identifier:
            url /= "search/"
            url.args["key"] = identifier

        return url


class McMaster(VendorBaseClass):
    """Define any methods related to connections to McMaster's website."""

    base_url = furl("https://www.mcmaster.com/")

    def link_from_identifier(self, identifier: str) -> str:
        """Returns a query based on the number. Often redirects to product page."""

        url = McMaster.base_url
        if identifier:
            url /= identifier

        return url


class MSC(VendorBaseClass):
    """Define any methods related to connections to MSC's website."""

    base_url = furl("https://www.mscdirect.com/product/details/")

    def link_from_identifier(self, identifier: str) -> str:
        """Should return a valid product detail page given the MSC#"""

        url = MSC.base_url
        if identifier:
            url /= identifier

        return url


class LittleMachineShop(VendorBaseClass):
    """Define any methods related to connections to LittleMachineShop.com's website."""

    base_url = furl(
        "https://littlemachineshop.com/products/product_view.php?ProductID=",
    )

    def link_from_identifier(self, identifier: str) -> str:
        """Returns a query based on the number. Often redirects to product page."""

        url = McMaster.base_url
        if identifier:
            url /= identifier

        return url
