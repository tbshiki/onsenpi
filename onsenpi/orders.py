from sp_api.api import Orders, Reports
from sp_api.base import SellingApiException


class Order:
    def __init__(self, marketplace, credentials):
        self.marketplace = marketplace
        self.credentials = credentials

    def get_orders(self):
        try:
            orders = Orders(credentials=self.credentials, marketplace=self.marketplace)
            response = orders.get_orders(CreatedAfter="2024-01-01", OrderStatuses=["Unshipped"])
            return response.payload
        except SellingApiException as e:
            print(f"Order Request Error: {e}")
            return None

    def request_order_report(self, report_type="GET_FLAT_FILE_ACTIONABLE_ORDER_DATA_SHIPPING", **kwargs):
        try:
            orders = Reports(credentials=self.credentials, marketplace=self.marketplace)
            response = orders.create_report(
                report_type=report_type,
                dataStartTime="2024-01-01",
            )
            # print(kwargs.get("dataStartTime"))
            return response.payload
        except SellingApiException as e:
            print(f"Order Report Request Error: {e}")
            return None
