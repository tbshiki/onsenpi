"""
OnsenpiSPAPIClientのテスト
"""

import logging
import os
import tempfile
from unittest import mock

import pytest
from sp_api.base import Marketplaces, SellingApiException

from onsenpi import DataConverter, OnsenpiAPIError, OnsenpiException, OnsenpiSPAPIClient, OnsenpiValidationError


@pytest.fixture
def mock_credentials():
    """テスト用の認証情報を提供するフィクスチャ"""
    return {"refresh_token": "test_token", "lwa_app_id": "test_app_id", "lwa_client_secret": "test_secret"}


@pytest.fixture
def client(mock_credentials):
    """テスト用のクライアントインスタンスを提供するフィクスチャ"""
    return OnsenpiSPAPIClient(marketplace=Marketplaces.JP, refresh_token=mock_credentials["refresh_token"], lwa_app_id=mock_credentials["lwa_app_id"], lwa_client_secret=mock_credentials["lwa_client_secret"], log_level=logging.DEBUG)


@pytest.fixture
def create_mock_response():
    """テスト用モックレスポンスを生成するヘルパーフィクスチャ"""

    def _create_response(payload):
        response = mock.MagicMock()
        response.payload = payload
        return response

    return _create_response


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


class MockSellingApiException(SellingApiException):
    """テスト用にカスタマイズしたSellingApiExceptionクラス"""

    def __init__(self, message, code=None, response=None):
        # 親クラスの__init__を呼び出さず、必要な属性を直接設定
        self.message = message
        self.code = code
        self.response = response or {}


@mock.patch("onsenpi.inventory.CatalogItems")
def test_inventory_search_catalog_items_error(mock_catalog_items, client):
    """inventoryモジュールのsearch_catalog_itemsメソッドのエラー処理テスト"""
    # モックの設定
    mock_instance = mock_catalog_items.return_value

    # カスタムSellingApiExceptionを作成
    ex = MockSellingApiException(message="Test error", code="500", response={"status": 500, "headers": {"x-amzn-RequestId": "test-request-id"}})

    mock_instance.search_catalog_items.side_effect = ex

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

    # カスタムSellingApiExceptionを作成
    ex = MockSellingApiException(message="Rate exceeded", code="429", response={"status": 429, "headers": {"x-amzn-RequestId": "test-request-id", "x-amzn-RateLimit-Limit": "1"}})

    mock_instance.get_orders.side_effect = ex

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


def test_client_set_log_level(client):
    """ロギングレベル変更機能のテスト"""
    # 初期状態を確認
    initial_level = client.logger.level

    # 新しいレベルに変更
    new_level = logging.WARNING if initial_level != logging.WARNING else logging.DEBUG
    client.set_log_level(new_level)

    # 全てのロガーが変更されていることを確認
    assert client.logger.level == new_level
    assert client.inventory.logger.level == new_level
    assert client.orders.logger.level == new_level
    assert client.product.logger.level == new_level


def test_onsenpi_api_error_detection():
    """OnsenpiAPIErrorの機能テスト"""
    # スロットリングエラーの検出テスト
    throttling_ex = MockSellingApiException(message="Rate exceeded", code="429", response={"status": 429, "headers": {"x-amzn-RequestId": "req-123"}})
    error = OnsenpiAPIError("TestAPI", throttling_ex)
    assert error.is_throttling_error() == True
    assert error.is_authentication_error() == False

    # 認証エラーの検出テスト
    auth_ex = MockSellingApiException(message="Authentication failed", code="401", response={"status": 401, "headers": {"x-amzn-RequestId": "req-456"}})
    error = OnsenpiAPIError("TestAPI", auth_ex)
    assert error.is_authentication_error() == True
    assert error.is_throttling_error() == False

    # エラー詳細情報の取得テスト
    details = error.get_error_details()
    assert "api_name" in details
    assert details["api_name"] == "TestAPI"
    assert "request_id" in details


@mock.patch("onsenpi.inventory.CatalogItems")
def test_inventory_search_catalog_items_with_args(mock_catalog_items, client):
    """inventoryモジュールのsearch_catalog_itemsメソッドの引数検証テスト"""
    # モックの設定
    mock_instance = mock_catalog_items.return_value
    mock_response = mock.MagicMock()
    mock_response.payload = {"items": [{"asin": "B00TEST123", "title": "Test Product"}]}
    mock_instance.search_catalog_items.return_value = mock_response

    # テストキーワードで呼び出し
    test_keyword = "test keyboard"
    client.inventory.search_catalog_items(test_keyword)

    # 引数の検証
    mock_instance.search_catalog_items.assert_called_with(keywords=test_keyword, marketplaceIds=client.marketplace.marketplace_id)


@mock.patch("onsenpi.inventory.Reports")
def test_inventory_report_workflow(mock_reports, client):
    """inventoryモジュールのレポートワークフローテスト"""
    # request_listing_reportのモック
    mock_reports_instance = mock_reports.return_value
    request_response = mock.MagicMock()
    request_response.payload = {"reportId": "test_report_id"}
    mock_reports_instance.create_report.return_value = request_response

    # wait_for_report_to_be_readyのモック
    get_response = mock.MagicMock()
    get_response.payload = {"processingStatus": "DONE", "reportDocumentId": "test_document_id"}
    mock_reports_instance.get_report.return_value = get_response

    # get_report_document_urlのモック
    url_response = mock.MagicMock()
    url_response.payload = {"url": "https://example.com/report.gz"}
    mock_reports_instance.get_report_document.return_value = url_response

    # ワークフローのテスト
    report_response = client.inventory.request_listing_report()
    assert "reportId" in report_response

    with mock.patch("time.sleep", return_value=None):  # sleep関数をモック化
        document_id = client.inventory.wait_for_report_to_be_ready(report_response["reportId"])
        assert document_id == "test_document_id"

        # ダウンロードURLの取得テスト
        with mock.patch("requests.get") as mock_requests:
            mock_requests.return_value = mock.MagicMock()
            mock_requests.return_value.raise_for_status = mock.MagicMock()

            with mock.patch("builtins.open", mock.mock_open()) as mock_file:
                # 仮ファイル名でダウンロードテスト
                result = client.inventory.download_report_data(document_id, "test.gz")
                assert result == True

                # 各ステップが呼ばれたことを検証
                mock_reports_instance.get_report_document.assert_called_once_with(document_id)
                mock_requests.assert_called_once_with("https://example.com/report.gz", stream=True)
                mock_file.assert_called_once_with("test.gz", "wb")
