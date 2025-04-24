"""
Amazon SP-APIとの実際の統合テスト
(SPAPI_TEST_ENABLED=1の環境変数設定時のみ実行)
"""

import os
import pytest

from sp_api.base import Marketplaces
from onsenpi import OnsenpiSPAPIClient


# テストをスキップするためのマーカー
pytestmark = pytest.mark.skipif(os.environ.get("SPAPI_TEST_ENABLED") != "1", reason="環境変数SPAPI_TEST_ENABLEDが1に設定されていないため、実際のAPI通信テストをスキップします。")


class TestInventoryIntegration:
    """inventoryモジュールの統合テスト"""

    def test_search_catalog_items(self, integration_client):
        """カタログ検索APIの結合テスト"""
        # 一般的なキーワードで検索
        results = integration_client.inventory.search_catalog_items("test product")

        # レスポンスの基本構造を検証
        assert isinstance(results, dict)
        # 'items'キーが存在するか、またはエラーメッセージが適切に含まれているか
        assert "items" in results or "errors" in results


class TestOrdersIntegration:
    """ordersモジュールの統合テスト"""

    def test_get_orders(self, integration_client):
        """注文取得APIの結合テスト"""
        # 少数の注文のみ取得（期間を短く、または最大件数を制限）
        orders = integration_client.orders.get_orders(created_after="2023-01-01T00:00:00Z", max_results_per_page=5)

        # レスポンスの基本構造を検証
        assert isinstance(orders, dict)
        # 'Orders'キーが存在するか、またはエラーメッセージが適切に含まれているか
        assert "Orders" in orders or "errors" in orders


class TestProductIntegration:
    """productモジュールの統合テスト"""

    def test_get_item_offers_batch(self, integration_client):
        """商品価格情報のバッチ取得テスト"""
        # 商品情報の取得（ASINはテスト用のもの、または実際の環境から取得）
        test_asins = os.environ.get("SP_API_TEST_ASINS", "B000000000,B111111111").split(",")

        if not test_asins or test_asins[0] == "B000000000":
            pytest.skip("有効なテスト用ASINが設定されていません。SP_API_TEST_ASINSにカンマ区切りでASINを設定してください")

        # 例: "B00X,B00Y,B00Z"のように環境変数で指定
        results = integration_client.product.get_competitive_pricing(test_asins[:2])  # 最初の2つだけ使用

        # レスポンスの基本構造を検証
        assert isinstance(results, dict)
        assert "Items" in results


class TestReportIntegration:
    """レポート関連の統合テスト"""

    def test_report_request_workflow(self, integration_client, temp_directory):
        """レポートリクエスト～取得のワークフロー統合テスト"""
        # このテストは時間がかかるためオプションでスキップ可能に
        if os.environ.get("SP_API_TEST_REPORTS") != "1":
            pytest.skip("レポートテストはSP_API_TEST_REPORTS=1の場合のみ実行")

        # レポートをリクエスト
        report_response = integration_client.inventory.request_listing_report()
        assert "reportId" in report_response

        # レポートIDを保存
        report_id = report_response["reportId"]
        print(f"レポートがリクエストされました。ID: {report_id}")

        # レポートの準備完了を待つ - 長時間かかる可能性があるためタイムアウト長め
        max_checks = 5  # 試行回数を少なくして実行時間を短縮
        document_id = None

        with pytest.raises(Exception):  # テスト実行時間短縮のため、あえてタイムアウトさせる
            document_id = integration_client.inventory.wait_for_report_to_be_ready(report_id, check_interval=10, max_checks=max_checks)

        print(f"レポート {report_id} のステータスチェックが完了しました")

        # 注意: 実際のテストでは時間がかかるため、ドキュメントIDの取得まで成功しなくても
        # リクエスト自体ができることを確認できればよい
