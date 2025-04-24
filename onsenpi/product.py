import logging
from typing import Dict, List, Optional, Any, Union

from sp_api.api import Products, CatalogItems
from sp_api.base import SellingApiException

from .exceptions import OnsenpiAPIError


class Product:
    """
    Amazon SP-APIを使用して商品関連の操作を行うクラス。
    商品情報の取得や価格情報の取得などの機能を提供します。
    """

    def __init__(self, marketplace, credentials, logger=None):
        """
        Productクラスの初期化

        Args:
            marketplace: SP-APIのマーケットプレイス設定
            credentials: 認証情報の辞書
            logger: ロガーインスタンス（指定がなければ新規作成）
        """
        self.marketplace = marketplace
        self.credentials = credentials

        # ロガーの設定
        self.logger = logger or logging.getLogger("onsenpi.product")
        if not logger and not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def get_item_offers_batch(self, asins: List[str], item_conditions: Optional[List[str]] = None, marketplace_id: str = "A1VC38T7YXB528") -> Optional[Dict[str, Any]]:
        """
        複数のASINに対応する商品の価格オファーを一括で取得します。

        Args:
            asins: 取得対象の商品ASINのリスト
            item_conditions: 取得する商品コンディションのリスト（デフォルト: ["NEW"]）
            marketplace_id: マーケットプレイスID（デフォルト: 日本マーケットプレイス "A1VC38T7YXB528"）

        Returns:
            オファー情報を含む辞書

        Raises:
            OnsenpiAPIError: API呼び出し中にエラーが発生した場合
        """
        if item_conditions is None:
            item_conditions = ["NEW"]

        self.logger.debug(f"Getting item offers batch for {len(asins)} ASINs")

        try:
            products_api = Products(self.marketplace, credentials=self.credentials)
            request = []

            for asin in asins:
                for item_condition in item_conditions:
                    request.append({"uri": f"/products/pricing/v0/items/{asin}/offers", "method": "GET", "ItemCondition": item_condition, "MarketplaceId": marketplace_id})

            self.logger.debug(f"Created {len(request)} requests for pricing information")
            response = products_api.get_item_offers_batch(request)

            self.logger.info(f"Successfully retrieved batch item offers")
            return response.payload

        except SellingApiException as e:
            self.logger.error(f"Products API Error: {e}")
            raise OnsenpiAPIError("Products", e) from e

    def get_item(self, asin: str) -> Optional[Dict[str, Any]]:
        """
        ASINを指定して商品情報を取得します（新CatalogItems API対応版）

        Args:
            asin: 取得する商品のASIN

        Returns:
            商品情報を含む辞書

        Raises:
            OnsenpiAPIError: API呼び出し中にエラーが発生した場合
        """
        self.logger.debug(f"Getting catalog item for ASIN: {asin}")

        try:
            catalog_api = CatalogItems(marketplace=self.marketplace, credentials=self.credentials)
            response = catalog_api.get_catalog_item(asin=asin, marketplaceIds=[self.marketplace.marketplace_id])

            self.logger.info("Successfully retrieved catalog item")
            return response.payload

        except SellingApiException as e:
            self.logger.error(f"Catalog API Error: {e}")
            self.logger.error(f"Error Code: {e.code}")
            self.logger.error(f"Error Response: {e.response}")
            raise OnsenpiAPIError("CatalogItems", e) from e

    def list_items_query(self, query: str) -> List[Dict[str, Any]]:
        """
        キーワードクエリを使用して商品情報を検索します（新API対応版）

        Args:
            query: 検索キーワード

        Returns:
            商品情報のリスト

        Raises:
            OnsenpiAPIError: API呼び出し中にエラーが発生した場合
        """
        self.logger.debug(f"Searching catalog items with query: {query}")

        try:
            catalog_api = CatalogItems(marketplace=self.marketplace, credentials=self.credentials)
            response = catalog_api.search_catalog_items(keywords=query, marketplaceIds=[self.marketplace.marketplace_id])

            items = response.payload.get("items", [])
            self.logger.info(f"Successfully retrieved {len(items)} catalog items")
            return items

        except SellingApiException as e:
            self.logger.error(f"Catalog API Error: {e}")
            self.logger.error(f"Error Code: {e.code}")
            self.logger.error(f"Error Response: {e.response}")
            raise OnsenpiAPIError("CatalogItems", e) from e

    def list_items_jan(self, jan_code: str) -> Optional[Dict[str, Any]]:
        """
        JANコードを指定して商品情報を取得します（新CatalogItems API対応）

        Args:
            jan_code: 検索対象のJANコード

        Returns:
            レスポンスのpayload全体を含む辞書

        Raises:
            OnsenpiAPIError: API呼び出し中にエラーが発生した場合
        """
        self.logger.debug(f"Searching catalog items by JAN code: {jan_code}")

        try:
            catalog_api = CatalogItems(marketplace=self.marketplace, credentials=self.credentials)
            response = catalog_api.search_catalog_items(keywords=jan_code, marketplaceIds=[self.marketplace.marketplace_id])

            self.logger.info("Successfully retrieved catalog items by JAN code")
            return response.payload

        except SellingApiException as e:
            self.logger.error(f"Catalog API Error: {e}")
            self.logger.error(f"Error Code: {e.code}")
            self.logger.error(f"Error Response: {e.response}")
            raise OnsenpiAPIError("CatalogItems", e) from e

    def search_asin_by_jan(self, jan_code: str) -> Optional[str]:
        """
        JANコードからASINを検索します。

        Args:
            jan_code: 検索対象のJANコード

        Returns:
            検索されたASIN（見つからなかった場合はNone）

        Raises:
            OnsenpiAPIError: API呼び出し中にエラーが発生した場合
        """
        self.logger.debug(f"Searching ASIN by JAN code: {jan_code}")

        try:
            catalog_api = CatalogItems(marketplace=self.marketplace, credentials=self.credentials)
            response = catalog_api.search_catalog_items(keywords=jan_code, marketplaceIds=[self.marketplace.marketplace_id])

            # ASINを抽出（複数候補がある場合は最初のものを返す）
            items = response.payload.get("items", [])
            if not items:
                self.logger.warning(f"No items found for JAN: {jan_code}")
                return None

            asin = items[0]["asin"]
            self.logger.info(f"Found ASIN: {asin} for JAN: {jan_code}")
            return asin

        except SellingApiException as e:
            self.logger.error(f"Catalog API Error: {e}")
            self.logger.error(f"Error Code: {e.code}")
            self.logger.error(f"Error Response: {e.response}")
            raise OnsenpiAPIError("CatalogItems", e) from e

    def get_product_pricing_for_asins(self, asin_list: List[str]) -> Optional[Dict[str, Any]]:
        """
        指定されたASINの競合価格情報を取得します。

        Args:
            asin_list: 価格情報を取得するASINのリスト

        Returns:
            競合価格情報を含む辞書

        Raises:
            OnsenpiAPIError: API呼び出し中にエラーが発生した場合
        """
        self.logger.debug(f"Getting competitive pricing for {len(asin_list)} ASINs")

        try:
            products_api = Products(self.marketplace, credentials=self.credentials)
            response = products_api.get_competitive_pricing_for_asins(asin_list=asin_list)

            self.logger.info("Successfully retrieved competitive pricing information")
            return response.payload

        except SellingApiException as e:
            self.logger.error(f"Products API Error: {e}")
            raise OnsenpiAPIError("Products", e) from e

    def get_item_offers(self, asin: str, item_condition: str = "NEW") -> Optional[Dict[str, Any]]:
        """
        指定したASINの商品に対するオファー情報を取得します。

        Args:
            asin: 取得対象の商品ASIN
            item_condition: 商品のコンディション（デフォルト: "NEW"）

        Returns:
            オファー情報を含む辞書

        Raises:
            OnsenpiAPIError: API呼び出し中にエラーが発生した場合
        """
        self.logger.debug(f"Getting item offers for ASIN: {asin}, condition: {item_condition}")

        try:
            products_api = Products(self.marketplace, credentials=self.credentials)
            response = products_api.get_item_offers(
                item_condition=item_condition,
                asin=asin,
            )

            self.logger.info(f"Successfully retrieved offers for ASIN: {asin}")
            return response.payload

        except SellingApiException as e:
            self.logger.error(f"Products API Error: {e}")
            raise OnsenpiAPIError("Products", e) from e

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
