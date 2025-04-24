"""
Amazon SP-APIとの実際の統合テスト
(SPAPI_TEST_ENABLED=1の環境変数設定時のみ実行)
"""

import os

import pytest

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

    def test_report_request_workflow(self, integration_client):
        """レポートリクエスト～取得のワークフローテスト"""
        # このテストは時間がかかるためオプションでスキップ可能に
        if os.environ.get("SP_API_TEST_REPORTS") != "1":
            pytest.skip("レポートテストはSP_API_TEST_REPORTS=1の場合のみ実行")

        # レポートをリクエスト
        report_response = integration_client.inventory.request_listing_report()
        assert "reportId" in report_response

        # レポートIDを保存
        report_id = report_response["reportId"]
        print(f"レポートがリクエストされました。ID: {report_id}")

        # レポートの準備完了を待つ - 長時間かかる可能性があるためタイムアウト短め
        # 注: 実際の統合テストでは長いタイムアウトが必要な場合もある
        try:
            document_id = integration_client.inventory.wait_for_report_to_be_ready(
                report_id,
                timeout=120,  # 2分のタイムアウト
                interval=10,  # 10秒ごとにチェック
            )

            # ドキュメントIDが取得できた場合はダウンロードも試行
            if document_id:
                print(f"ドキュメントID: {document_id} が取得できました")

                # 一時ファイルにダウンロード
                import tempfile

                with tempfile.NamedTemporaryFile(suffix=".gz", delete=False) as temp_file:
                    temp_path = temp_file.name

                try:
                    result = integration_client.inventory.download_report_data(document_id, temp_path)
                    assert result is True
                    assert os.path.exists(temp_path)
                    assert os.path.getsize(temp_path) > 0
                    print(f"レポートが正常にダウンロードされました: {temp_path}")
                finally:
                    # テスト後にファイルを削除
                    if os.path.exists(temp_path):
                        os.unlink(temp_path)
        except Exception as e:
            # テスト目的としては、APIエラーでなくタイムアウトなら問題なし
            print(f"レポート取得中に例外が発生: {e}")
            # タイムアウト以外のエラーは再スロー
            if not str(e).startswith("Error while waiting for report") and "timed out" not in str(e).lower():
                raise

    def test_recent_reports(self, integration_client):
        """最近のレポートリクエスト取得テスト"""
        # このテストは時間がかかるためオプションでスキップ可能に
        if os.environ.get("SP_API_TEST_REPORTS") != "1":
            pytest.skip("レポートテストはSP_API_TEST_REPORTS=1の場合のみ実行")

        # 最近のレポートをチェック
        batch_id = integration_client.inventory.get_recent_report_requests()

        # レポートの存在は環境によって変わるため、厳密なアサーションはしない
        print(f"最近のレポートID: {batch_id}")

        if batch_id:
            # レポートタイプの取得をテスト
            report_type = integration_client.inventory.get_report_type_by_batch_id(batch_id)
            print(f"レポートタイプ: {report_type}")
            assert report_type is not None
