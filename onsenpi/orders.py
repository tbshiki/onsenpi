from sp_api.api import Orders, Reports
from sp_api.base import SellingApiException


class Order:
    def __init__(self, marketplace, credentials):
        self.marketplace = marketplace
        self.credentials = credentials

    def get_orders(self, create_after="2024-01-01", order_statuses=["Unshipped"]):
        try:
            orders = Orders(credentials=self.credentials, marketplace=self.marketplace)
            response = orders.get_orders(CreatedAfter=create_after, OrderStatuses=order_statuses)
            return response.payload
        except SellingApiException as e:
            print(f"Order Request Error: {e}")
            return None

    def get_order_items(self, amazon_order_id):
        try:
            order_items = Orders(credentials=self.credentials, marketplace=self.marketplace)
            response = order_items.get_order_items(order_id=amazon_order_id)
            return response.payload
        except SellingApiException as e:
            print(f"Order Items Request Error: {e}")
            return None

    def request_order_report(self, report_type="GET_FLAT_FILE_ACTIONABLE_ORDER_DATA_SHIPPING"):
        ##
        # 個人情報へのアクセス許可を取得していないと使用できない
        ##
        try:
            orders = Reports(credentials=self.credentials, marketplace=self.marketplace)
            response = orders.create_report(
                reportType=report_type,
                dataStartTime="2024-01-01",
            )
            # print(kwargs.get("dataStartTime"))
            return response.payload
        except SellingApiException as e:
            print(f"Order Report Request Error: {e}")
            return None
