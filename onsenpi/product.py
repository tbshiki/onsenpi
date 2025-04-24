import logging
from typing import Any, Dict, List, Optional

from sp_api.api import CatalogItems, ListingsItems, Products
from sp_api.base import SellingApiException

from .exceptions import OnsenpiAPIError


class Product:
    """
    Amazon SP-APIを使用して商品関連の操作を行うクラス。
    商品情報の取得や価格情報の取得などの機能を提供します。
    """

    def __init__(self, marketplace: Any, credentials: Dict[str, str], logger: Optional[logging.Logger] = None):
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

    def get_item_offers_batch(self, asins: List[str], item_conditions: Optional[List[str]] = None, marketplace_id: Optional[str] = None) -> Dict[str, Any]:
        """
        複数のASINに対応する商品の価格オファーを一括で取得します。

        Args:
            asins: 取得対象の商品ASINのリスト
            item_conditions: 取得する商品コンディションのリスト（デフォルト: ["NEW"]）
            marketplace_id: マーケットプレイスID（指定しない場合は現在のマーケットプレイスを使用）

        Returns:
            オファー情報を含む辞書

        Raises:
            OnsenpiAPIError: API呼び出し中にエラーが発生した場合
        """
        if item_conditions is None:
            item_conditions = ["NEW"]

        if marketplace_id is None:
            marketplace_id = self.marketplace.marketplace_id

        self.logger.debug(f"Getting item offers batch for {len(asins)} ASINs")

        try:
            products_api = Products(self.marketplace, credentials=self.credentials)
            request = []

            for asin in asins:
                for item_condition in item_conditions:
                    request.append({"uri": f"/products/pricing/v0/items/{asin}/offers", "method": "GET", "ItemCondition": item_condition, "MarketplaceId": marketplace_id})

            self.logger.debug(f"Created {len(request)} requests for pricing information")
            response = products_api.get_item_offers_batch(request)

            self.logger.info(f"Successfully retrieved batch item offers for {len(asins)} ASINs")
            return response.payload

        except SellingApiException as e:
            self.logger.error(f"Products API Error: {e}")
            raise OnsenpiAPIError("Products", original_exception=e)

    def get_competitive_pricing(self, asins: List[str]) -> Dict[str, Any]:
        """
        指定したASINの競合価格情報を取得します。

        Args:
            asins: 取得対象の商品ASINのリスト(最大20件)

        Returns:
            競合価格情報を含む辞書

        Raises:
            OnsenpiAPIError: API呼び出し中にエラーが発生した場合
        """
        if len(asins) > 20:
            self.logger.warning("ASINリストは20件以内に制限されています。先頭20件のみ処理します。")
            asins = asins[:20]

        self.logger.debug(f"Getting competitive pricing for {len(asins)} ASINs")

        try:
            products_api = Products(self.marketplace, credentials=self.credentials)
            response = products_api.get_competitive_pricing_for_asins(asins=asins, marketplaceId=self.marketplace.marketplace_id)

            self.logger.info(f"Successfully retrieved competitive pricing for {len(asins)} ASINs")
            return response.payload

        except SellingApiException as e:
            self.logger.error(f"Products API Error (competitive pricing): {e}")
            raise OnsenpiAPIError("Products", original_exception=e)

    def get_item(self, asin: str) -> Dict[str, Any]:
        """
        ASINを指定して商品情報を取得します（カタログ情報）

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

            self.logger.info(f"Successfully retrieved catalog item for ASIN: {asin}")
            return response.payload

        except SellingApiException as e:
            self.logger.error(f"Catalog API Error: {e}")
            self.logger.error(f"Error Code: {getattr(e, 'code', 'unknown')}")
            self.logger.error(f"Error Response: {getattr(e, 'response', 'N/A')}")
            raise OnsenpiAPIError("CatalogItems", original_exception=e)

    def search_catalog_items(self, keywords: str, marketplace_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        キーワードを指定して商品カタログを検索します。

        Args:
            keywords: 検索キーワード
            marketplace_ids: 検索対象のマーケットプレイスID（指定しない場合は現在のマーケットプレイスを使用）

        Returns:
            検索結果を含む辞書

        Raises:
            OnsenpiAPIError: API呼び出し中にエラーが発生した場合
        """
        if marketplace_ids is None:
            marketplace_ids = [self.marketplace.marketplace_id]

        self.logger.debug(f"Searching catalog items with keywords: {keywords}")

        try:
            catalog_api = CatalogItems(marketplace=self.marketplace, credentials=self.credentials)
            response = catalog_api.search_catalog_items(keywords=keywords, marketplaceIds=marketplace_ids)

            result_count = len(response.payload.get("items", [])) if response.payload and "items" in response.payload else 0
            self.logger.info(f"Successfully searched catalog items. Found {result_count} results")
            return response.payload

        except SellingApiException as e:
            self.logger.error(f"Catalog Search API Error: {e}")
            raise OnsenpiAPIError("CatalogItems", original_exception=e)

    def get_listings_item(self, seller_sku: str) -> Dict[str, Any]:
        """
        出品者SKUを指定して、出品商品情報を取得します。

        Args:
            seller_sku: 出品者SKU

        Returns:
            出品商品情報を含む辞書

        Raises:
            OnsenpiAPIError: API呼び出し中にエラーが発生した場合
        """
        self.logger.debug(f"Getting listings item for SKU: {seller_sku}")

        try:
            listings_api = ListingsItems(marketplace=self.marketplace, credentials=self.credentials)
            response = listings_api.get_listings_item(sellerId=self.credentials.get("seller_id", ""), sku=seller_sku)

            self.logger.info(f"Successfully retrieved listings item for SKU: {seller_sku}")
            return response.payload

        except SellingApiException as e:
            self.logger.error(f"Listings API Error: {e}")
            raise OnsenpiAPIError("ListingsItems", original_exception=e)

    def update_listings_item(self, seller_sku: str, listings_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        出品者SKUを指定して、出品商品情報を更新します。

        Args:
            seller_sku: 出品者SKU
            listings_data: 更新する出品商品情報の辞書

        Returns:
            更新結果を含む辞書

        Raises:
            OnsenpiAPIError: API呼び出し中にエラーが発生した場合
        """
        self.logger.debug(f"Updating listings item for SKU: {seller_sku}")

        try:
            listings_api = ListingsItems(marketplace=self.marketplace, credentials=self.credentials)
            response = listings_api.put_listings_item(sellerId=self.credentials.get("seller_id", ""), sku=seller_sku, body=listings_data)

            self.logger.info(f"Successfully updated listings item for SKU: {seller_sku}")
            return response.payload

        except SellingApiException as e:
            self.logger.error(f"Listings Update API Error: {e}")
            raise OnsenpiAPIError("ListingsItems", original_exception=e)
