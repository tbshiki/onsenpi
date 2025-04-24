"""
テスト全体で共通のフィクスチャやヘルパー関数を定義します。
"""

import logging
import os
import tempfile
from unittest import mock

import pytest
from sp_api.base import Marketplaces, SellingApiException

from onsenpi import OnsenpiSPAPIClient


class MockResponse:
    """SP-APIレスポンスのモッククラス"""

    def __init__(self, payload, status_code=200):
        self.payload = payload
        self.status_code = status_code


class MockSellingApiException(SellingApiException):
    """テスト用にカスタマイズしたSellingApiExceptionクラス"""

    def __init__(self, message, code=None, response=None):
        # 親クラスの__init__を呼び出さず、必要な属性を直接設定
        self.message = message
        self.code = code
        self.response = response or {}


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


@pytest.fixture
def mock_sp_api():
    """SP-API全般のモックを提供するフィクスチャ"""
    with mock.patch("onsenpi.inventory.CatalogItems") as mock_catalog, mock.patch("onsenpi.inventory.Reports") as mock_reports, mock.patch("onsenpi.orders.Orders") as mock_orders, mock.patch("onsenpi.product.Products") as mock_products:
        yield {"catalog": mock_catalog, "reports": mock_reports, "orders": mock_orders, "products": mock_products}


@pytest.fixture
def temp_directory():
    """一時ディレクトリを提供するフィクスチャ。テストファイル操作に使用します。"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def integration_client():
    """実際のAPI通信用クライアント（環境変数でスキップ制御）"""
    if os.environ.get("SPAPI_TEST_ENABLED") != "1":
        pytest.skip("API通信テストはスキップされます（環境変数 SPAPI_TEST_ENABLED=1 を設定してください）")

    return OnsenpiSPAPIClient(marketplace=Marketplaces.JP, refresh_token=os.environ.get("SP_API_REFRESH_TOKEN"), lwa_app_id=os.environ.get("SP_API_LWA_APP_ID"), lwa_client_secret=os.environ.get("SP_API_LWA_CLIENT_SECRET"))
