import logging
import time
from typing import Any, Dict, Optional

import requests
from sp_api.api import CatalogItems, Reports
from sp_api.base import SellingApiException

from .exceptions import OnsenpiAPIError, OnsenpiDownloadError, OnsenpiReportError


class Inventory:
    """
    Amazon SP-APIを使用して在庫関連の操作を行うクラス。
    """

    def __init__(self, marketplace: Any, credentials: Dict[str, str], logger: Optional[logging.Logger] = None):
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

    def search_catalog_items(self, keyword: str) -> Dict[str, Any]:
        """
        キーワードに基づいて商品カタログを検索

        Args:
            keyword: 検索キーワード

        Returns:
            検索結果の辞書

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
            raise OnsenpiAPIError("inventory_catalog", original_exception=e)

    def get_catalog_item(self, asin: str) -> Dict[str, Any]:
        """
        ASINから商品カタログ情報を取得

        Args:
            asin: 商品のASIN

        Returns:
            商品カタログ情報の辞書

        Raises:
            OnsenpiAPIError: API呼び出し中にエラーが発生した場合
        """
        self.logger.debug(f"Getting catalog item for ASIN: {asin}")

        try:
            catalog = CatalogItems(marketplace=self.marketplace, credentials=self.credentials)
            response = catalog.get_catalog_item(asin=asin, marketplaceIds=self.marketplace.marketplace_id)
            return response.payload
        except SellingApiException as e:
            self.logger.error(f"Catalog API Error: {e}")
            raise OnsenpiAPIError("inventory_catalog", original_exception=e)

    def request_listing_report(self, report_type: str = "GET_MERCHANT_LISTINGS_ALL_DATA") -> Dict[str, Any]:
        """
        レポートをリクエストし、バッチIDを取得

        Args:
            report_type: リクエストするレポートタイプ（デフォルト: GET_MERCHANT_LISTINGS_ALL_DATA）

        Returns:
            レポートリクエストの情報を含む辞書

        Raises:
            OnsenpiAPIError: API呼び出し中にエラーが発生した場合
        """
        self.logger.debug(f"Requesting listing report of type: {report_type}")

        try:
            reports_api = Reports(credentials=self.credentials, marketplace=self.marketplace)
            response = reports_api.create_report(reportType=report_type)
            self.logger.info(f"Successfully requested report of type: {report_type}")
            return response.payload
        except SellingApiException as e:
            self.logger.error(f"Report Request Error: {e}")
            raise OnsenpiAPIError("Reports", original_exception=e)

    def get_report_type_by_batch_id(self, report_id: str) -> str:
        """
        バッチID（レポートID）からそのレポートの種類を取得

        Args:
            report_id: レポートID

        Returns:
            レポートタイプ

        Raises:
            OnsenpiAPIError: API呼び出し中にエラーが発生した場合
        """
        self.logger.debug(f"Getting report type for batch ID: {report_id}")

        try:
            reports_api = Reports(credentials=self.credentials, marketplace=self.marketplace)
            response = reports_api.get_report(report_id)
            report_type = response.payload.get("reportType")
            self.logger.debug(f"Report type for {report_id}: {report_type}")
            return report_type
        except SellingApiException as e:
            self.logger.error(f"Error getting report type: {e}")
            raise OnsenpiAPIError("Reports", original_exception=e)

    def wait_for_report_to_be_ready(self, batch_id: str, timeout: int = 300, interval: int = 30, max_checks: Optional[int] = None) -> Optional[str]:
        """
        指定したbatch_id に対してステータスがDONE になるまで待機して結果を取得

        Args:
            batch_id: レポートのバッチID
            timeout: 最大待機時間（秒）
            interval: ステータス確認間隔（秒）
            max_checks: 最大チェック回数 (None = 無制限)

        Returns:
            レポートドキュメントID（準備完了時）またはNone（タイムアウト時）

        Raises:
            OnsenpiReportError: レポート処理中にエラーが発生した場合
        """
        elapsed_time = 0
        check_count = 0
        reports_api = Reports(credentials=self.credentials, marketplace=self.marketplace)

        self.logger.info(f"Waiting for report {batch_id} to be ready (timeout: {timeout}s, interval: {interval}s)")

        while elapsed_time < timeout and (max_checks is None or check_count < max_checks):
            try:
                check_count += 1
                response = reports_api.get_report(batch_id)
                status = response.payload.get("processingStatus")

                # ステータスが「DONE」ならレポートが準備完了
                if status == "DONE":
                    report_document_id = response.payload.get("reportDocumentId")
                    self.logger.info(f"Report {batch_id} is ready. Document ID: {report_document_id}")
                    return report_document_id

                # ステータスがまだ「DONE」でない場合のログ出力
                self.logger.debug(f"Report {batch_id} is not ready yet. Status: {status}. Waiting for {interval} seconds.")

                # 次のリクエストまで待機
                time.sleep(interval)
                elapsed_time += interval

            except SellingApiException as e:
                self.logger.error(f"SellingApiException occurred: {e}")
                raise OnsenpiReportError(f"Error while waiting for report {batch_id}: {e}")

            except Exception as e:
                self.logger.error(f"Unexpected error: {e}", exc_info=True)
                raise OnsenpiReportError(f"Unexpected error while waiting for report {batch_id}: {e}")

        if max_checks is not None and check_count >= max_checks:
            self.logger.warning(f"Maximum number of checks ({max_checks}) reached for report {batch_id}")
        else:
            self.logger.warning(f"Timeout reached: Report {batch_id} was not ready within {timeout} seconds.")

        return None

    def get_recent_report_requests(self, report_type: str = "GET_MERCHANT_LISTINGS_DATA_BACK_COMPAT") -> Optional[str]:
        """
        最近のレポートリクエストを取得し、直近のバッチIDを返す

        Args:
            report_type: 取得するレポートタイプ

        Returns:
            最新のレポートのバッチID、または該当するレポートがない場合はNone

        Raises:
            OnsenpiAPIError: API呼び出し中にエラーが発生した場合
        """
        self.logger.debug(f"Getting recent report requests of type: {report_type}")

        try:
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
                    self.logger.info(f"Found recent report with ID: {batch_id}")
                    return batch_id
                else:
                    self.logger.warning("Payload does not contain any reports")
                    return None
            else:
                self.logger.warning("Response does not have valid payload structure")
                return None
        except SellingApiException as e:
            self.logger.error(f"Error getting recent reports: {e}")
            raise OnsenpiAPIError("Reports", original_exception=e)

    def get_report_document_url(self, report_document_id: str) -> str:
        """
        レポートドキュメントIDからダウンロードURLを取得

        Args:
            report_document_id: レポートドキュメントID

        Returns:
            レポートダウンロードURL

        Raises:
            OnsenpiAPIError: API呼び出し中にエラーが発生した場合
        """
        self.logger.debug(f"Getting report document URL for ID: {report_document_id}")

        try:
            reports_api = Reports(credentials=self.credentials, marketplace=self.marketplace)
            response = reports_api.get_report_document(report_document_id)
            url = response.payload.get("url")
            if not url:
                raise OnsenpiReportError(f"No URL returned for report document ID: {report_document_id}")
            return url
        except SellingApiException as e:
            self.logger.error(f"Get Report Document Error: {e}")
            raise OnsenpiAPIError("Reports", original_exception=e)

    def download_report_data(self, report_document_id: str, temp_gzip_file_name: str) -> bool:
        """
        レポートデータをダウンロードしてファイルに保存

        Args:
            report_document_id: レポートドキュメントID
            temp_gzip_file_name: 保存先のGZIPファイル名

        Returns:
            ダウンロード成功時はTrue、失敗時はFalse

        Raises:
            OnsenpiDownloadError: ダウンロード中にエラーが発生した場合
        """
        self.logger.debug(f"Downloading report data for document ID: {report_document_id} to {temp_gzip_file_name}")

        try:
            url = self.get_report_document_url(report_document_id)
            response = requests.get(url, stream=True)
            response.raise_for_status()

            with open(temp_gzip_file_name, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            self.logger.info(f"Successfully downloaded report to {temp_gzip_file_name}")
            return True
        except requests.exceptions.RequestException as e:
            self.logger.error(f"HTTP request error when downloading report: {e}")
            raise OnsenpiDownloadError(f"Error downloading report: {e}")
        except IOError as e:
            self.logger.error(f"IO error when writing report file: {e}")
            raise OnsenpiDownloadError(f"Error writing report file: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error downloading report: {e}", exc_info=True)
            raise OnsenpiDownloadError(f"Unexpected error downloading report: {e}")
