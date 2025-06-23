from typing import Optional, Dict, Any
import logging
from sp_api.api import Feeds
from sp_api.base import Marketplaces, SellingApiException


class Feed:
    """
    Amazon SP-APIのFeed送信（POST_FLAT_FILE_RECONCILIATION_DATAなど）を簡単に行うためのクラス。
    """

    def __init__(self, marketplace: Any = Marketplaces.JP, credentials: Optional[Dict[str, str]] = None, logger: Optional[logging.Logger] = None):
        self.marketplace = marketplace
        self.credentials = credentials or {}
        self.logger = logger or logging.getLogger("onsenpi.feeds")
        self._client = Feeds(marketplace=self.marketplace, **self.credentials)

    def send_reconciliation_data(self, tsv_path: str, marketplace_id: Optional[str] = None) -> Dict[str, Any]:
        """
        POST_FLAT_FILE_RECONCILIATION_DATA フィードを送信する
        Args:
            tsv_path: タブ区切りテキストファイルのパス
            marketplace_id: マーケットプレイスID（省略時はJP）
        Returns:
            Feed作成APIのレスポンス
        """
        try:
            # 1. Feed Document作成
            doc = self._client.create_feed_document("text/tab-separated-values")
            upload_url = doc.payload["url"]
            feed_document_id = doc.payload["feedDocumentId"]

            # 2. データをアップロード
            with open(tsv_path, "rb") as f:
                import requests

                requests.put(upload_url, data=f, headers={"Content-Type": "text/tab-separated-values"})

            # 3. Feed送信
            result = self._client.create_feed(feedType="POST_FLAT_FILE_RECONCILIATION_DATA", feedDocumentId=feed_document_id, marketplaceIds=[marketplace_id or self.marketplace.marketplace_id])
            self.logger.info(f"Feed送信完了: {result.payload}")
            return result.payload
        except SellingApiException as e:
            self.logger.error(f"SP-APIエラー: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Feed送信失敗: {e}")
            raise
