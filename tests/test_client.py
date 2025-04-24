"""
OnsenpiSPAPIClientのテスト
"""

import logging
import os
import tempfile
from unittest import mock

import pytest
from sp_api.base import Marketplaces, SellingApiException

from onsenpi import DataConverter, OnsenpiAPIError, OnsenpiException, OnsenpiSPAPIClient


@pytest.fixture
def mock_credentials():
    """テスト用の認証情報を提供するフィクスチャ"""
    return {"refresh_token": "test_token", "lwa_app_id": "test_app_id", "lwa_client_secret": "test_secret"}


@pytest.fixture
def client(mock_credentials):
    """テスト用のクライアントインスタンスを提供するフィクスチャ"""
    return OnsenpiSPAPIClient(marketplace=Marketplaces.JP, refresh_token=mock_credentials["refresh_token"], lwa_app_id=mock_credentials["lwa_app_id"], lwa_client_secret=mock_credentials["lwa_client_secret"], log_level=logging.DEBUG)


def test_client_initialization(client):
    """クライアントの初期化テスト"""
    assert client is not None
    assert client.marketplace == Marketplaces.JP
    assert client.inventory is not None
    assert client.orders is not None
    assert client.product is not None


def test_client_getattr_routing(client):
    """__getattr__メソッドのルーティング機能テスト"""
    # インスタンスのモックを作成
    client.inventory.search_catalog_items = mock.MagicMock(return_value={"test": "data"})

    # OnsenpiSPAPIClientを通じて子モジュールのメソッドにアクセス
    result = client.search_catalog_items("test_keyword")

    # 正しくルーティングされたかを確認
    client.inventory.search_catalog_items.assert_called_once_with("test_keyword")
    assert result == {"test": "data"}


def test_client_getattr_error(client):
    """存在しない属性へのアクセスでAttributeErrorが発生することをテスト"""
    with pytest.raises(AttributeError):
        client.non_existent_method()


@mock.patch("onsenpi.inventory.CatalogItems")
def test_inventory_search_catalog_items(mock_catalog_items, client):
    """inventoryモジュールのsearch_catalog_itemsメソッドのテスト"""
    # モックの設定
    mock_instance = mock_catalog_items.return_value
    mock_response = mock.MagicMock()
    mock_response.payload = {"items": [{"asin": "B00TEST123", "title": "Test Product"}]}
    mock_instance.search_catalog_items.return_value = mock_response

    # メソッド呼び出し
    result = client.inventory.search_catalog_items("test keyword")

    # 検証
    assert result == mock_response.payload
    mock_instance.search_catalog_items.assert_called_once()


@mock.patch("onsenpi.inventory.CatalogItems")
def test_inventory_search_catalog_items_error(mock_catalog_items, client):
    """inventoryモジュールのsearch_catalog_itemsメソッドのエラー処理テスト"""
    # モックの設定
    mock_instance = mock_catalog_items.return_value
    mock_instance.search_catalog_items.side_effect = SellingApiException("Test error")

    # エラーが発生することを確認
    with pytest.raises(OnsenpiAPIError):
        client.inventory.search_catalog_items("test keyword")


def test_data_converter():
    """DataConverterのテスト"""
    # テスト用の一時ディレクトリを作成
    with tempfile.TemporaryDirectory() as temp_dir:
        # コンテキストマネージャのテスト
        try:
            with pytest.raises(OnsenpiException):
                with DataConverter.open_file_safely("non_existent_file.txt", "r"):
                    pass
        except Exception as e:
            pytest.fail(f"Unexpected exception: {e}")

        # ディレクトリ作成機能のテスト
        test_dir = os.path.join(temp_dir, "test_dir")
        DataConverter.ensure_directory_exists(test_dir)
        assert os.path.exists(test_dir)

        # 2回呼んでもエラーにならないことを確認
        DataConverter.ensure_directory_exists(test_dir)

        # ファイルのセーフコピーのテスト
        test_src = os.path.join(temp_dir, "src.txt")
        test_dst = os.path.join(test_dir, "dst.txt")
        test_content = "テスト内容"

        # テストファイル作成
        with open(test_src, "w", encoding="utf-8") as f:
            f.write(test_content)

        # ファイルコピーテスト
        DataConverter.safe_copy_file(test_src, test_dst)
        assert os.path.exists(test_dst)

        # 内容確認
        with open(test_dst, "r", encoding="utf-8") as f:
            content = f.read()
            assert content == test_content


@mock.patch("onsenpi.product.Products")
def test_product_get_competitive_pricing(mock_products, client):
    """productモジュールのget_competitive_pricingメソッドのテスト"""
    # モックの設定
    mock_instance = mock_products.return_value
    mock_response = mock.MagicMock()
    mock_response.payload = {"Items": [{"ASIN": "B00TEST123", "status": "Success", "Product": {"CompetitivePricing": {"CompetitivePrices": [{"CompetitivePriceId": "1", "Price": {"ListingPrice": {"Amount": 1000, "CurrencyCode": "JPY"}}}]}}}]}
    mock_instance.get_competitive_pricing_for_asins.return_value = mock_response

    # メソッド呼び出し
    result = client.product.get_competitive_pricing(["B00TEST123"])

    # 検証
    assert result == mock_response.payload
    mock_instance.get_competitive_pricing_for_asins.assert_called_once()


@mock.patch("onsenpi.orders.Orders")
def test_orders_get_orders(mock_orders, client):
    """ordersモジュールのget_ordersメソッドのテスト"""
    # モックの設定
    mock_instance = mock_orders.return_value
    mock_response = mock.MagicMock()
    mock_response.payload = {"Orders": [{"AmazonOrderId": "123-1234567-1234567", "PurchaseDate": "2023-01-01T00:00:00Z", "OrderStatus": "Unshipped", "OrderTotal": {"CurrencyCode": "JPY", "Amount": 3000}}]}
    mock_instance.get_orders.return_value = mock_response

    # メソッド呼び出し
    result = client.orders.get_orders(order_statuses=["Unshipped"])

    # 検証
    assert result == mock_response.payload
    mock_instance.get_orders.assert_called_once()


@mock.patch("onsenpi.orders.Orders")
def test_orders_get_orders_error(mock_orders, client):
    """ordersモジュールのget_ordersメソッドのエラー処理テスト"""
    # モックの設定
    mock_instance = mock_orders.return_value
    mock_instance.get_orders.side_effect = SellingApiException("Test error")

    # エラーが発生することを確認
    with pytest.raises(OnsenpiAPIError):
        client.orders.get_orders()


@mock.patch("onsenpi.inventory.Reports")
def test_inventory_request_listing_report(mock_reports, client):
    """inventoryモジュールのrequest_listing_reportメソッドのテスト"""
    # モックの設定
    mock_instance = mock_reports.return_value
    mock_response = mock.MagicMock()
    mock_response.payload = {"reportId": "test_report_id"}
    mock_instance.create_report.return_value = mock_response

    # メソッド呼び出し
    result = client.inventory.request_listing_report()

    # 検証
    assert result == mock_response.payload
    mock_instance.create_report.assert_called_once()
