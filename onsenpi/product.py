from sp_api.api import Products  # , Catalog
from sp_api.base import SellingApiException
from sp_api.api import CatalogItems


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

    # def get_item(self, asin):
    #     """
    #     ASINを指定して商品情報を取得
    #     250331 でCatalog が廃止された
    #     """
    #     try:
    #         catalog = Catalog(self.marketplace, credentials=self.credentials)
    #         response = catalog.get_item(asin=asin, MarketplaceId=self.marketplace.marketplace_id)
    #         return response.payload
    #     except SellingApiException as e:
    #         print(f"Catalog API Error: {e}")
    #         return None

    def get_item(self, asin):
        """
        ASINを指定して商品情報を取得（新CatalogItems API対応版）
        """
        try:
            catalog = CatalogItems(marketplace=self.marketplace, credentials=self.credentials)
            response = catalog.get_catalog_item(asin=asin, marketplaceIds=[self.marketplace.marketplace_id])
            return response.payload
        except SellingApiException as e:
            print(f"Catalog API Error: {e}")
            print(f"Error Code: {e.code}")
            print(f"Error Response: {e.response}")
            return None

    # def list_items_query(self, query):
    #     """
    #     商品情報を取得するためのクエリを指定して商品情報を取得
    #     250331 でCatalog が廃止された
    #     """

    #     print(f"Query: {query}")
    #     try:
    #         catalog = Catalog(self.marketplace, credentials=self.credentials)
    #         response = catalog.list_items(Query=query, MarketplaceId=self.marketplace.marketplace_id)
    #         return response.payload
    #     except SellingApiException as e:
    #         print(f"Catalog API Error: {e}")
    #         return None

    def list_items_query(self, query):
        """
        商品情報を取得するためのクエリを指定して商品情報を取得（新API対応版）
        """
        print(f"Query: {query}")
        try:
            catalog = CatalogItems(marketplace=self.marketplace, credentials=self.credentials)
            response = catalog.search_catalog_items(keywords=query, marketplaceIds=[self.marketplace.marketplace_id])
            return response.payload.get("items", [])
        except SellingApiException as e:
            print(f"Catalog API Error: {e}")
            print(f"Error Code: {e.code}")
            print(f"Error Response: {e.response}")
            return None

    # def list_items_jan(self, jan_code):
    #     """
    #     JANコードを指定して商品情報を取得
    #     250331 でCatalog が廃止された
    #     """
    #     print(f"JAN: {jan_code}")
    #     try:
    #         catalog = Catalog(self.marketplace, credentials=self.credentials)
    #         response = catalog.list_items(JAN=jan_code, MarketplaceId=self.marketplace.marketplace_id)
    #         return response.payload
    #     except SellingApiException as e:
    #         print(f"Catalog API Error: {e}")
    #         return None

    def list_items_jan(self, jan_code):
        """
        JANコードを指定して商品情報を取得（新CatalogItems API対応）
        レスポンスのpayloadをそのまま返す
        """
        print(f"JAN: {jan_code}")
        try:
            catalog = CatalogItems(marketplace=self.marketplace, credentials=self.credentials)
            response = catalog.search_catalog_items(keywords=jan_code, marketplaceIds=[self.marketplace.marketplace_id])
            return response.payload  # ← payload全体を返す
        except SellingApiException as e:
            print(f"Catalog API Error: {e}")
            print(f"Error Code: {e.code}")
            print(f"Error Response: {e.response}")
            return None

    def search_asin_by_jan(self, jan_code):
        print(f"JAN: {jan_code}")
        try:
            catalog = CatalogItems(marketplace=self.marketplace, credentials=self.credentials)
            response = catalog.search_catalog_items(keywords=jan_code, marketplaceIds=[self.marketplace.marketplace_id])
            # ASINを抽出（複数候補がある場合は最初のものを返す）
            items = response.payload.get("items", [])
            if not items:
                print("No items found for JAN:", jan_code)
                return None
            asin = items[0]["asin"]
            print("Found ASIN:", asin)
            return asin
        except SellingApiException as e:
            print(f"Catalog API Error: {e}")
            print(f"Error Code: {e.code}")
            print(f"Error Response: {e.response}")
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
