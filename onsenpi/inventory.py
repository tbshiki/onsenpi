import logging
import time
from typing import Any, Dict, Optional
import requests

from sp_api.api import Reports, CatalogItems
from sp_api.base import SellingApiException

from .exceptions import OnsenpiAPIError


class Inventory:
    """
    Amazon SP-APIを使用して在庫関連の操作を行うクラス。
    """

    def __init__(self, marketplace, credentials, logger=None):
        """
        Inventoryクラスの初期化

        Args:
            marketplace: SP-APIのマーケットプレイス設定
            credentials: 認証情報の辞書
            logger: ロガーインスタンス（指定がなければ新規作成）
        """
        self.marketplace = marketplace
        self.credentials = credentials

        # ロガーの設定
        self.logger = logger or logging.getLogger("onsenpi.inventory")
        if not logger and not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def search_catalog_items(self, keyword: str) -> Optional[Dict[str, Any]]:
        """
        キーワードに基づいて商品カタログを検索

        Args:
            keyword: 検索キーワード

        Returns:
            検索結果の辞書、エラー時はNone

        Raises:
            OnsenpiAPIError: API呼び出し中にエラーが発生した場合
        """
        self.logger.debug(f"Searching catalog items with keyword: {keyword}")

        try:
            catalog = CatalogItems(marketplace=self.marketplace, credentials=self.credentials)
            response = catalog.search_catalog_items(keywords=keyword, marketplaceIds=self.marketplace.marketplace_id)

            self.logger.debug("Catalog search successful")
            return response.payload

        except SellingApiException as e:
            self.logger.error(f"Catalog API Error: {e}")
            raise OnsenpiAPIError("Catalog", original_exception=e)

    def get_catalog_item(self, asin):
        try:
            catalog = CatalogItems(marketplace=self.marketplace, credentials=self.credentials)
            response = catalog.get_catalog_item(asin=asin, marketplaceIds=self.marketplace.marketplace_id)
            return response.payload
        except SellingApiException as e:
            print(f"Catalog API Error: {e}")
            return None

    def request_listing_report(self, report_type="GET_MERCHANT_LISTINGS_ALL_DATA"):
        """
        report_type に指定されたレポートをリクエストし、バッチID を取得
        デフォルトでは すべての出品商品のレポート のバッチIDを取得
        """
        try:
            reports_api = Reports(credentials=self.credentials, marketplace=self.marketplace)
            response = reports_api.create_report(reportType=report_type)
            return response.payload
        except SellingApiException as e:
            print(f"Report Request Error: {e}")
            return None

    def get_report_type_by_batch_id(self, report_id):
        """
        バッチID（レポートID）からそのレポートの種類を取得
        """
        reports_api = Reports(credentials=self.credentials, marketplace=self.marketplace)

        # バッチID（レポートID）を使ってレポートの詳細を取得
        response = reports_api.get_report(report_id)

        # レスポンスからレポートタイプを取得
        report_type = response.payload.get("reportType")
        return report_type

    def wait_for_report_to_be_ready(self, batch_id, timeout=300, interval=30):
        """
        指定したbatch_id に対してステータスがDONE になるまで待機して結果を取得
        """
        elapsed_time = 0
        reports_api = Reports(credentials=self.credentials, marketplace=self.marketplace)  # 1度だけ生成

        while elapsed_time < timeout:
            try:
                response = reports_api.get_report(batch_id)
                status = response.payload.get("processingStatus")

                # ステータスが「DONE」ならレポートが準備完了
                if status == "DONE":
                    return response.payload.get("reportDocumentId")

                # ステータスがまだ「DONE」でない場合のログ出力
                print(f"Report {batch_id} is not ready yet. Status: {status}. Waiting for {interval} seconds.")

                # 次のリクエストまで待機
                time.sleep(interval)
                elapsed_time += interval

            except SellingApiException as e:
                print(f"SellingApiException occurred: {e}")
                return None  # エラーが発生した場合は終了

            except Exception as e:
                print(f"Unexpected error: {e}")
                return None  # 他の例外が発生した場合も終了

        print(f"Timeout reached: Report {batch_id} was not ready within {timeout} seconds.")
        return None  # タイムアウトが発生した場合は None を返す

    def get_recent_report_requests(self, report_type="GET_MERCHANT_LISTINGS_DATA_BACK_COMPAT"):
        """
        最近のレポートリクエストを取得し、直近のバッチIDを返す
        デフォルトでは 出品中の商品レポート のバッチIDを取得
        """
        reports_api = Reports(credentials=self.credentials, marketplace=self.marketplace)

        # レポートリクエストのリストを取得
        response = reports_api.get_reports(reportTypes=[report_type])

        # レスポンスペイロードを確認
        if response.payload and "reports" in response.payload:
            reports_list = response.payload["reports"]

            # ペイロードがリストかどうかを確認し、要素が存在するか確認
            if isinstance(reports_list, list) and len(reports_list) > 0:
                # 最新のバッチIDを取得
                recent_report = reports_list[0]
                batch_id = recent_report.get("reportId")
                return batch_id
            else:
                print("payload にレポートが含まれていません。")
                return None
        else:
            print("レスポンスにpayload がありません。")
            return None

    def get_report_document_url(self, report_document_id):
        try:
            reports_api = Reports(credentials=self.credentials, marketplace=self.marketplace)
            response = reports_api.get_report_document(report_document_id)
            return response.payload.get("url")
        except SellingApiException as e:
            print(f"Get Report Document Error: {e}")
            return None

    def download_report_data(self, report_document_id, temp_gzip_file_name):
        try:
            url = self.get_report_document_url(report_document_id)
            if url:
                response = requests.get(url, stream=True)
                response.raise_for_status()

                with open(temp_gzip_file_name, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                return True
            else:
                print("Report URL is not available.")
                return False
        except Exception as e:
            print(f"Error downloading report: {e}")
            return False
