from sp_api.api import Catalog, Products
from sp_api.base import SellingApiException


class Product:
    def __init__(self, marketplace, credentials):
        self.marketplace = marketplace
        self.credentials = credentials

    def get_item_offers_batch(self, asins, item_conditions=["NEW"], marketplace_id="A1VC38T7YXB528"):
        try:
            products = Products(self.marketplace, credentials=self.credentials)
            request = []
            for asin in asins:
                for item_condition in item_conditions:
                    request.append({"uri": "/products/pricing/v0/items/" + asin + "/offers", "method": "GET", "ItemCondition": item_condition, "MarketplaceId": marketplace_id})

            # print(request)
            response = products.get_item_offers_batch(request)

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

    def list_items_query(self, query):
        print(f"Query: {query}")
        try:
            catalog = Catalog(self.marketplace, credentials=self.credentials)
            response = catalog.list_items(Query=query, MarketplaceId=self.marketplace.marketplace_id)
            return response.payload
        except SellingApiException as e:
            print(f"Catalog API Error: {e}")
            return None

    def list_items_jan(self, jan_code):
        print(f"JAN: {jan_code}")
        try:
            catalog = Catalog(self.marketplace, credentials=self.credentials)
            response = catalog.list_items(JAN=jan_code, MarketplaceId=self.marketplace.marketplace_id)
            return response.payload
        except SellingApiException as e:
            print(f"Catalog API Error: {e}")
            return None

    def get_product_pricing_for_asins(self, asin_list):
        """
        指定されたASINの価格情報を取得
        """
        try:
            products = Products(self.marketplace, credentials=self.credentials)
            response = products.get_competitive_pricing_for_asins(asin_list=asin_list)
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

    def get_competitive_pricing_for_asins(self, asins):
        """
        複数のASINの競合価格情報を取得
        """
        try:
            products = Products(self.marketplace, credentials=self.credentials)
            response = products.get_competitive_pricing_for_asins(asin_list=asins)
            return response.payload
        except SellingApiException as e:
            print(f"API Error: {e}")
            return None
