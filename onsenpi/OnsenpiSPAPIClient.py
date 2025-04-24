import logging
from typing import Any, Dict, Optional
from sp_api.base import Marketplaces

from .inventory import Inventory
from .orders import Order
from .product import Product


class OnsenpiSPAPIClient:
    """
    Amazon Selling Partner APIへのアクセスを簡略化するメインクライアントクラス。
    このクラスは各機能モジュール（在庫、注文、商品）へのアクセスを提供します。
    """

    def __init__(
        self,
        marketplace: Any = Marketplaces.JP,
        refresh_token: Optional[str] = None,
        lwa_app_id: Optional[str] = None,
        lwa_client_secret: Optional[str] = None,
        log_level: int = logging.INFO,
        seller_id: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        """
        OnsenpiSPAPIClientの初期化

        Args:
            marketplace: SP-APIのマーケットプレイス設定（デフォルト：日本）
            refresh_token: SP-APIの認証用リフレッシュトークン
            lwa_app_id: LWAアプリケーションID
            lwa_client_secret: LWAクライアントシークレット
            log_level: ロギングレベル（デフォルト：INFO）
            seller_id: 出品者ID（一部のAPIリクエストで必要）
            logger: 外部から提供されるロガーインスタンス（指定がない場合は内部で作成）
        """
        # ロガーの設定
        self.logger = logger or self._setup_logger(log_level)

        self.marketplace = marketplace
        self.credentials = {
            "refresh_token": refresh_token,
            "lwa_app_id": lwa_app_id,
            "lwa_client_secret": lwa_client_secret,
        }

        # 出品者IDが指定されていれば追加
        if seller_id:
            self.credentials["seller_id"] = seller_id

        if not all([refresh_token, lwa_app_id, lwa_client_secret]):
            self.logger.warning("認証情報が完全ではありません。一部の操作ができない可能性があります。")

        self.logger.debug(f"Initializing OnsenpiSPAPIClient with marketplace: {marketplace.name}")

        # 子モジュールの初期化
        self.inventory = Inventory(marketplace, self.credentials, logger=self.logger)
        self.orders = Order(marketplace, self.credentials, logger=self.logger)
        self.product = Product(marketplace, self.credentials, logger=self.logger)

    def _setup_logger(self, log_level: int) -> logging.Logger:
        """
        ロガーの初期化と設定を行います。

        Args:
            log_level: ロガーに設定するログレベル

        Returns:
            設定済みのロガーインスタンス
        """
        logger = logging.getLogger("onsenpi")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        logger.setLevel(log_level)
        return logger

    def __getattr__(self, name: str) -> Any:
        """
        存在しない属性が呼ばれたときに自動的に適切なモジュールのメソッドにルーティングする。

        Args:
            name: 呼び出されたメソッド/属性名

        Returns:
            適切なモジュールのメソッド

        Raises:
            AttributeError: 属性が見つからない場合
        """
        # inventory のメソッドを確認
        if hasattr(self.inventory, name):
            return getattr(self.inventory, name)
        # product のメソッドを確認
        elif hasattr(self.product, name):
            return getattr(self.product, name)
        # orders のメソッドを確認
        elif hasattr(self.orders, name):
            return getattr(self.orders, name)
        else:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def set_log_level(self, log_level: int) -> None:
        """
        ロギングレベルをランタイムで変更します。

        Args:
            log_level: 新しいロギングレベル（logging.DEBUG, logging.INFO など）
        """
        self.logger.setLevel(log_level)
        self.inventory.logger.setLevel(log_level)
        self.orders.logger.setLevel(log_level)
        self.product.logger.setLevel(log_level)
        self.logger.info(f"Logging level changed to {log_level}")
