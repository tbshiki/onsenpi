"""
Product クラスのテスト
"""

import pytest
from unittest import mock

import logging
from sp_api.base import SellingApiException, Marketplaces

from onsenpi import Product
from onsenpi.exceptions import OnsenpiAPIError
from tests.conftest import MockResponse, MockSellingApiException


class TestProduct:
    """Product クラスのテストスイート"""

    @pytest.fixture
    def product_instance(self, mock_credentials):
        """テスト用の Product インスタンスを作成"""
        return Product(Marketplaces.JP, mock_credentials, logger=logging.getLogger("test"))

    def test_init(self, mock_credentials):
        """初期化のテスト"""
        # デフォルトのロガーを使用
        product = Product(Marketplaces.JP, mock_credentials)
        assert product.marketplace == Marketplaces.JP
        assert product.credentials == mock_credentials
        assert product.logger.name == "onsenpi.product"

        # カスタムロガーを使用
        custom_logger = logging.getLogger("custom")
        product = Product(Marketplaces.JP, mock_credentials, logger=custom_logger)
        assert product.logger == custom_logger

    def test_get_item_offers_batch(self, product_instance, mock_sp_api):
        """商品の価格オファー一括取得のテスト"""
        # モックの設定
        mock_response = MockResponse({"responses": [{"status": 200, "body": {"payload": {"offers": []}}}]})
        mock_sp_api["products"].return_value.get_item_offers_batch.return_value = mock_response

        # 関数の実行
        asins = ["B000000001", "B000000002"]
        result = product_instance.get_item_offers_batch(asins)

        # APIが正しく呼び出されたか検証
        mock_sp_api["products"].assert_called_once()
        mock_sp_api["products"].return_value.get_item_offers_batch.assert_called_once()

        # リクエストに含まれるASINの数が正しいか
        call_args = mock_sp_api["products"].return_value.get_item_offers_batch.call_args[0][0]
        assert len(call_args) == 2  # ASINが2つあるので、デフォルトのコンディション（NEW）が1つの場合は2リクエスト

        # 結果の検証
        assert result == {"responses": [{"status": 200, "body": {"payload": {"offers": []}}}]}

    def test_get_item_offers_batch_with_conditions(self, product_instance, mock_sp_api):
        """複数のコンディションを指定した価格オファー取得のテスト"""
        # モックの設定
        mock_response = MockResponse({"responses": []})
        mock_sp_api["products"].return_value.get_item_offers_batch.return_value = mock_response

        # 関数の実行
        asins = ["B000000001"]
        item_conditions = ["NEW", "USED"]
        result = product_instance.get_item_offers_batch(asins, item_conditions)

        # リクエスト数の検証（ASIN 1つ × コンディション 2つ = 2リクエスト）
        call_args = mock_sp_api["products"].return_value.get_item_offers_batch.call_args[0][0]
        assert len(call_args) == 2

    def test_get_item_offers_batch_with_marketplace_id(self, product_instance, mock_sp_api):
        """マーケットプレイスIDを指定した価格オファー取得のテスト"""
        # モックの設定
        mock_response = MockResponse({"responses": []})
        mock_sp_api["products"].return_value.get_item_offers_batch.return_value = mock_response

        # 関数の実行
        asins = ["B000000001"]
        marketplace_id = "A1VC38T7YXB528"  # Japan marketplace ID
        result = product_instance.get_item_offers_batch(asins, marketplace_id=marketplace_id)

        # マーケットプレイスIDが正しく設定されているか検証
        call_args = mock_sp_api["products"].return_value.get_item_offers_batch.call_args[0][0][0]
        assert call_args["MarketplaceId"] == marketplace_id

    def test_get_item_offers_batch_error(self, product_instance, mock_sp_api):
        """価格オファー取得時のエラー処理のテスト"""
        # エラーのモック
        mock_sp_api["products"].return_value.get_item_offers_batch.side_effect = MockSellingApiException("API Error", code="500", response={"status": 500})

        # 例外の発生確認
        with pytest.raises(OnsenpiAPIError) as excinfo:
            product_instance.get_item_offers_batch(["B000000001"])

        # 例外の内容確認
        assert "Products" in str(excinfo.value)
        assert excinfo.value.api_name == "Products"

    def test_get_competitive_pricing(self, product_instance, mock_sp_api):
        """競合価格情報取得のテスト"""
        # モックの設定
        mock_response = MockResponse({"pricing": []})
        mock_sp_api["products"].return_value.get_competitive_pricing_for_asins.return_value = mock_response

        # 関数の実行
        asins = ["B000000001", "B000000002"]
        result = product_instance.get_competitive_pricing(asins)

        # APIが正しく呼び出されたか検証
        mock_sp_api["products"].assert_called_once()
        mock_sp_api["products"].return_value.get_competitive_pricing_for_asins.assert_called_once_with(asins=asins, marketplaceId=product_instance.marketplace.marketplace_id)

        # 結果の検証
        assert result == {"pricing": []}

    def test_get_competitive_pricing_limit(self, product_instance, mock_sp_api):
        """ASINが20を超える場合の競合価格情報取得のテスト"""
        # モックの設定
        mock_response = MockResponse({"pricing": []})
        mock_sp_api["products"].return_value.get_competitive_pricing_for_asins.return_value = mock_response

        # 関数の実行（21個のASIN）
        asins = [f"B{i:09d}" for i in range(21)]  # B000000000からB000000020までの形式に修正
        result = product_instance.get_competitive_pricing(asins)

        # 最初の20件のみ処理されることを検証
        call_args = mock_sp_api["products"].return_value.get_competitive_pricing_for_asins.call_args[1]["asins"]
        assert len(call_args) == 20
        assert call_args[0] == "B000000000"
        assert call_args[19] == "B000000019"

    def test_get_competitive_pricing_error(self, product_instance, mock_sp_api):
        """競合価格情報取得時のエラー処理のテスト"""
        # エラーのモック
        mock_sp_api["products"].return_value.get_competitive_pricing_for_asins.side_effect = MockSellingApiException("API Error", code="500", response={"status": 500})

        # 例外の発生確認
        with pytest.raises(OnsenpiAPIError) as excinfo:
            product_instance.get_competitive_pricing(["B000000001"])

        # 例外の内容確認
        assert "Products" in str(excinfo.value)

    def test_get_item(self, product_instance, mock_sp_api):
        """カタログ商品情報取得のテスト"""
        # モックの設定
        mock_catalog_response = MockResponse({"item": {"asin": "B000000001", "attributes": {}}})
        mock_sp_api["catalog"].return_value.get_catalog_item.return_value = mock_catalog_response

        # 関数の実行
        result = product_instance.get_item("B000000001")

        # APIが正しく呼び出されたか検証
        mock_sp_api["catalog"].assert_called_once()
        mock_sp_api["catalog"].return_value.get_catalog_item.assert_called_once_with(asin="B000000001", marketplaceIds=[product_instance.marketplace.marketplace_id])

        # 結果の検証
        assert result == {"item": {"asin": "B000000001", "attributes": {}}}

    def test_get_item_error(self, product_instance, mock_sp_api):
        """カタログ商品情報取得時のエラー処理のテスト"""
        # エラーのモック
        mock_exception = MockSellingApiException("API Error", code="404", response={"status": 404})
        mock_sp_api["catalog"].return_value.get_catalog_item.side_effect = mock_exception

        # 例外の発生確認
        with pytest.raises(OnsenpiAPIError) as excinfo:
            product_instance.get_item("B000000001")

        # 例外の内容確認
        assert "CatalogItems" in str(excinfo.value)
        assert excinfo.value.api_name == "CatalogItems"

    def test_search_catalog_items(self, product_instance, mock_sp_api):
        """カタログ検索のテスト"""
        # モックの設定
        mock_catalog_response = MockResponse({"items": [{"asin": "B000000001"}, {"asin": "B000000002"}]})
        mock_sp_api["catalog"].return_value.search_catalog_items.return_value = mock_catalog_response

        # 関数の実行
        result = product_instance.search_catalog_items("test keyword")

        # APIが正しく呼び出されたか検証
        mock_sp_api["catalog"].assert_called_once()
        mock_sp_api["catalog"].return_value.search_catalog_items.assert_called_once_with(keywords="test keyword", marketplaceIds=[product_instance.marketplace.marketplace_id])

        # 結果の検証
        assert result == {"items": [{"asin": "B000000001"}, {"asin": "B000000002"}]}

    def test_search_catalog_items_with_marketplace(self, product_instance, mock_sp_api):
        """複数マーケットプレイス指定でのカタログ検索のテスト"""
        # モックの設定
        mock_catalog_response = MockResponse({"items": []})
        mock_sp_api["catalog"].return_value.search_catalog_items.return_value = mock_catalog_response

        # 関数の実行
        marketplace_ids = ["A1VC38T7YXB528", "ATVPDKIKX0DER"]  # JP and US
        result = product_instance.search_catalog_items("test keyword", marketplace_ids=marketplace_ids)

        # マーケットプレイスIDが正しく設定されているか検証
        mock_sp_api["catalog"].return_value.search_catalog_items.assert_called_once_with(keywords="test keyword", marketplaceIds=marketplace_ids)

    def test_search_catalog_items_error(self, product_instance, mock_sp_api):
        """カタログ検索時のエラー処理のテスト"""
        # エラーのモック
        mock_sp_api["catalog"].return_value.search_catalog_items.side_effect = MockSellingApiException("API Error", code="500", response={"status": 500})

        # 例外の発生確認
        with pytest.raises(OnsenpiAPIError) as excinfo:
            product_instance.search_catalog_items("test keyword")

        # 例外の内容確認
        assert "CatalogItems" in str(excinfo.value)
        assert excinfo.value.api_name == "CatalogItems"

    def test_get_listings_item(self, product_instance, mock_sp_api):
        """出品商品情報取得のテスト"""
        # モックの設定
        with mock.patch("onsenpi.product.ListingsItems") as mock_listings:
            mock_listings.return_value.get_listings_item.return_value = MockResponse({"sku": "TEST-SKU"})

            # 関数の実行
            result = product_instance.get_listings_item("TEST-SKU")

            # APIが正しく呼び出されたか検証
            mock_listings.assert_called_once()
            mock_listings.return_value.get_listings_item.assert_called_once_with(sellerId=product_instance.credentials.get("seller_id", ""), sku="TEST-SKU")

            # 結果の検証
            assert result == {"sku": "TEST-SKU"}

    def test_get_listings_item_error(self, product_instance, mock_sp_api):
        """出品商品情報取得時のエラー処理のテスト"""
        # モックの設定
        with mock.patch("onsenpi.product.ListingsItems") as mock_listings:
            # エラーのモック
            mock_listings.return_value.get_listings_item.side_effect = MockSellingApiException("API Error", code="404", response={"status": 404})

            # 例外の発生確認
            with pytest.raises(OnsenpiAPIError) as excinfo:
                product_instance.get_listings_item("TEST-SKU")

            # 例外の内容確認
            assert "ListingsItems" in str(excinfo.value)
            assert excinfo.value.api_name == "ListingsItems"

    def test_update_listings_item(self, product_instance, mock_sp_api):
        """出品商品情報更新のテスト"""
        # モックの設定
        with mock.patch("onsenpi.product.ListingsItems") as mock_listings:
            mock_listings.return_value.put_listings_item.return_value = MockResponse({"status": "SUCCESS"})

            # 関数の実行
            listings_data = {"price": 1000}
            result = product_instance.update_listings_item("TEST-SKU", listings_data)

            # APIが正しく呼び出されたか検証
            mock_listings.assert_called_once()
            mock_listings.return_value.put_listings_item.assert_called_once_with(sellerId=product_instance.credentials.get("seller_id", ""), sku="TEST-SKU", body=listings_data)

            # 結果の検証
            assert result == {"status": "SUCCESS"}

    def test_update_listings_item_error(self, product_instance, mock_sp_api):
        """出品商品情報更新時のエラー処理のテスト"""
        # モックの設定
        with mock.patch("onsenpi.product.ListingsItems") as mock_listings:
            # エラーのモック
            mock_listings.return_value.put_listings_item.side_effect = MockSellingApiException("API Error", code="400", response={"status": 400})

            # 例外の発生確認
            listings_data = {"price": 1000}
            with pytest.raises(OnsenpiAPIError) as excinfo:
                product_instance.update_listings_item("TEST-SKU", listings_data)

            # 例外の内容確認
            assert "ListingsItems" in str(excinfo.value)
            assert excinfo.value.api_name == "ListingsItems"
