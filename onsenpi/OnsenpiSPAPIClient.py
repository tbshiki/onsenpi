from sp_api.api import Catalog, CatalogItems, Orders, Reports, Products
from sp_api.base import Marketplaces, SellingApiException

import time
import requests


class OnsenpiSPAPIClient:
    def __init__(
        self,
        marketplace=Marketplaces.JP,
        refresh_token=None,
        lwa_app_id=None,
        lwa_client_secret=None,
    ):
        self.marketplace = marketplace
        self.credentials = {
            "refresh_token": refresh_token,
            "lwa_app_id": lwa_app_id,
            "lwa_client_secret": lwa_client_secret,
        }

    def get_product_pricing_for_asins(self, asin_list):
        try:
            products = Products(self.marketplace, credentials=self.credentials)
            response = products.get_competitive_pricing_for_asins(asin_list=asin_list)
            return response.payload
        except SellingApiException as e:
            print(f"API Error: {e}")
            return None

    def get_competitive_pricing_for_asins(self, asins):
        try:
            products = Products(self.marketplace, credentials=self.credentials)
            response = products.get_competitive_pricing_for_asins(asin_list=asins)
            return response.payload
        except SellingApiException as e:
            print(f"API Error: {e}")
            return None

    def get_item_offers(self, asin, item_condition="NEW"):
        try:
            products = Products(self.marketplace, credentials=self.credentials)
            response = products.get_item_offers(
                item_condition=item_condition,
                asin=asin,
            )
            return response.payload
        except SellingApiException as e:
            print(f"API Error: {e}")
            return None

    def get_item_offers_batch(self, asins, item_conditions=["NEW"], marketplace_id="A1VC38T7YXB528"):
        try:
            products = Products(self.marketplace, credentials=self.credentials)
            requestsa = []
            for asin in asins:
                for item_condition in item_conditions:
                    requestsa.append({"uri": "/products/pricing/v0/items/" + asin + "/offers", "method": "GET", "ItemCondition": item_condition, "MarketplaceId": marketplace_id})

            print(requestsa)
            response = products.get_item_offers_batch(requestsa)

            return response.payload
        except SellingApiException as e:
            print(f"API Error: {e}")
            return None

    def get_item(self, asin):
        try:
            catalog = Catalog(self.marketplace, credentials=self.credentials)
            response = catalog.get_item(asin=asin, MarketplaceId=self.marketplace.marketplace_id)
            return response.payload
        except SellingApiException as e:
            print(f"Catalog API Error: {e}")
            return None

    def list_items(self, query):
        try:
            catalog = Catalog(self.marketplace, credentials=self.credentials)
            response = catalog.list_items(Query=query, MarketplaceId=self.marketplace.marketplace_id)
            return response.payload
        except SellingApiException as e:
            print(f"Catalog API Error: {e}")
            return None

    def search_catalog_items(self, keyword):
        try:
            catalog = CatalogItems(marketplace=self.marketplace, credentials=self.credentials)
            response = catalog.search_catalog_items(keywords=keyword, marketplaceIds=self.marketplace.marketplace_id)
            return response.payload
        except SellingApiException as e:
            print(f"Catalog API Error: {e}")
            return None

    def get_catalog_item(self, asin):
        try:
            catalog = CatalogItems(marketplace=self.marketplace, credentials=self.credentials)
            response = catalog.get_catalog_item(asin=asin, marketplaceIds=self.marketplace.marketplace_id)
            return response.payload
        except SellingApiException as e:
            print(f"Catalog API Error: {e}")
            return None

    def request_listing_report(self, report_type="GET_MERCHANT_LISTINGS_ALL_DATA"):
        try:
            reports_api = Reports(credentials=self.credentials, marketplace=self.marketplace)
            response = reports_api.create_report(reportType=report_type)
            return response.payload
        except SellingApiException as e:
            print(f"Report Request Error: {e}")
            return None

    def get_orders(self):
        try:
            orders = Orders(credentials=self.credentials, marketplace=self.marketplace)
            response = orders.get_orders(CreatedAfter="2024-01-01", OrderStatuses=["Unshipped"])

            return response.payload
        except SellingApiException as e:
            print(f"Order Report Request Error: {e}")
            return None

    def request_order_report(self, report_type="GET_FLAT_FILE_ACTIONABLE_ORDER_DATA_SHIPPING", **kwargs):
        try:
            orders = Reports(credentials=self.credentials, marketplace=self.marketplace)

            response = orders.create_report(
                report_type=report_type,
                dataStartTime="2024-01-01",
            )
            print(kwargs.get("dataStartTime"))

            return response.payload
        except SellingApiException as e:
            print(f"Order Report Request Error: {e}")
            return None

    def get_report_document_url(self, report_document_id):
        try:
            reports_api = Reports(credentials=self.credentials, marketplace=self.marketplace)
            response = reports_api.get_report_document(report_document_id)
            return response.payload.get("url")
        except SellingApiException as e:
            print(f"Get Report Document Error: {e}")
            return None

    def download_report_data(self, report_document_id, temp_gzip_file_name):
        try:
            url = self.get_report_document_url(report_document_id)
            if url:
                response = requests.get(url, stream=True)
                response.raise_for_status()

                with open(temp_gzip_file_name, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                return True
            else:
                print("Report URL is not available.")
                return False
        except Exception as e:
            print(f"Error downloading report: {e}")
            return False

    def wait_for_report_to_be_ready(self, report_id, timeout=300, interval=30):
        elapsed_time = 0
        while elapsed_time < timeout:
            try:
                reports_api = Reports(credentials=self.credentials, marketplace=self.marketplace)
                response = reports_api.get_report(report_id)
                if response.payload.get("processingStatus") == "DONE":
                    return response.payload.get("reportDocumentId")
                time.sleep(interval)
                elapsed_time += interval
            except SellingApiException as e:
                print(f"Error while waiting for report: {e}")
                return None
        return None

    def download_report_data(self, report_document_id, temp_gzip_file_name):
        try:
            url = self.get_report_document_url(report_document_id)
            if url:
                response = requests.get(url, stream=True)
                response.raise_for_status()

                with open(temp_gzip_file_name, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                return True
            else:
                print("Report URL is not available.")
                return False
        except Exception as e:
            print(f"Error downloading report: {e}")
            return False
