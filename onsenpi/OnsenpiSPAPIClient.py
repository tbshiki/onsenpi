import logging
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
        marketplace=Marketplaces.JP,
        refresh_token=None,
        lwa_app_id=None,
        lwa_client_secret=None,
        log_level=logging.INFO,
    ):
        """
        OnsenpiSPAPIClientの初期化

        Args:
            marketplace: SP-APIのマーケットプレイス設定（デフォルト：日本）
            refresh_token: SP-APIの認証用リフレッシュトークン
            lwa_app_id: LWAアプリケーションID
            lwa_client_secret: LWAクライアントシークレット
            log_level: ロギングレベル（デフォルト：INFO）
        """
        # ロガーの設定
        self.logger = logging.getLogger("onsenpi")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        self.logger.setLevel(log_level)

        self.marketplace = marketplace
        self.credentials = {
            "refresh_token": refresh_token,
            "lwa_app_id": lwa_app_id,
            "lwa_client_secret": lwa_client_secret,
        }

        self.logger.debug(f"Initializing OnsenpiSPAPIClient with marketplace: {marketplace.name}")

        # 子モジュールの初期化
        self.inventory = Inventory(marketplace, self.credentials, logger=self.logger)
        self.orders = Order(marketplace, self.credentials, logger=self.logger)
        self.product = Product(marketplace, self.credentials, logger=self.logger)

    def __getattr__(self, name):
        """
        存在しない属性が呼ばれたときに自動的に適切なモジュールのメソッドにルーティングする。
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
