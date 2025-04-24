import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

from sp_api.api import Orders, Reports
from sp_api.base import SellingApiException, Marketplaces

from .exceptions import OnsenpiAPIError


class Order:
    """
    Amazon SP-APIを使用して注文関連の操作を行うクラス。
    """

    def __init__(self, marketplace, credentials, logger=None):
        """
        Orderクラスの初期化

        Args:
            marketplace: SP-APIのマーケットプレイス設定
            credentials: 認証情報の辞書
            logger: ロガーインスタンス（指定がなければ新規作成）
        """
        self.marketplace = marketplace
        self.credentials = credentials

        # ロガーの設定
        self.logger = logger or logging.getLogger("onsenpi.orders")
        if not logger and not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def get_orders(self, create_after: str = "2024-01-01", order_statuses: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        """
        指定した日付以降に作成された注文を取得します。

        Args:
            create_after: この日付以降に作成された注文を取得（ISO 8601形式の日付文字列 YYYY-MM-DD）
            order_statuses: 取得する注文のステータスリスト（デフォルト: ["Unshipped"]）

        Returns:
            注文情報を含む辞書、エラー時はNone

        Raises:
            OnsenpiAPIError: API呼び出し中にエラーが発生した場合
        """
        if order_statuses is None:
            order_statuses = ["Unshipped"]

        self.logger.debug(f"Fetching orders created after {create_after} with statuses: {order_statuses}")

        try:
            orders_api = Orders(credentials=self.credentials, marketplace=self.marketplace)
            response = orders_api.get_orders(CreatedAfter=create_after, OrderStatuses=order_statuses)

            self.logger.info(f"Successfully retrieved orders")
            if response.payload and "Orders" in response.payload:
                self.logger.debug(f"Retrieved {len(response.payload['Orders'])} orders")

            return response.payload
        except SellingApiException as e:
            self.logger.error(f"Order API Error: {e}")
            raise OnsenpiAPIError("Orders", e) from e

    def get_order_items(self, amazon_order_id: str) -> Optional[Dict[str, Any]]:
        """
        指定した注文IDの注文アイテムを取得します。

        Args:
            amazon_order_id: 注文ID

        Returns:
            注文アイテム情報を含む辞書、エラー時はNone

        Raises:
            OnsenpiAPIError: API呼び出し中にエラーが発生した場合
        """
        self.logger.debug(f"Fetching order items for order ID: {amazon_order_id}")

        try:
            orders_api = Orders(credentials=self.credentials, marketplace=self.marketplace)
            response = orders_api.get_order_items(order_id=amazon_order_id)

            self.logger.info("Successfully retrieved order items")
            if response.payload and "OrderItems" in response.payload:
                self.logger.debug(f"Retrieved {len(response.payload['OrderItems'])} order items")

            return response.payload
        except SellingApiException as e:
            self.logger.error(f"Order Items Request Error: {e}")
            raise OnsenpiAPIError("Orders", e) from e

    def request_order_report(self, report_type: str = "GET_FLAT_FILE_ACTIONABLE_ORDER_DATA_SHIPPING", start_date: str = "2024-01-01") -> Optional[Dict[str, Any]]:
        """
        注文レポートをリクエストします。

        注意:
            このAPIを使用するには、個人情報へのアクセス許可が必要です。

        Args:
            report_type: リクエストするレポートタイプ
            start_date: レポート対象期間の開始日（ISO 8601形式の日付文字列 YYYY-MM-DD）

        Returns:
            レポートリクエスト情報を含む辞書、エラー時はNone

        Raises:
            OnsenpiAPIError: API呼び出し中にエラーが発生した場合
        """
        self.logger.debug(f"Requesting order report of type: {report_type} from date: {start_date}")

        try:
            reports_api = Reports(credentials=self.credentials, marketplace=self.marketplace)
            response = reports_api.create_report(
                reportType=report_type,
                dataStartTime=start_date,
            )

            self.logger.info(f"Successfully requested order report. Report ID: {response.payload.get('reportId', 'unknown')}")
            return response.payload
        except SellingApiException as e:
            self.logger.error(f"Order Report Request Error: {e}")
            raise OnsenpiAPIError("Reports", e) from e
