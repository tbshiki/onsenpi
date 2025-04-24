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
