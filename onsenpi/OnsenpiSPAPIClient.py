from sp_api.base import Marketplaces


from .inventory import Inventory
from .orders import Order
from .product import Product


class OnsenpiSPAPIClient:
    def __init__(
        self,
        marketplace=Marketplaces.JP,
        refresh_token=None,
        lwa_app_id=None,
        lwa_client_secret=None,
    ):
        self.marketplace = marketplace
        self.credentials = {
            "refresh_token": refresh_token,
            "lwa_app_id": lwa_app_id,
            "lwa_client_secret": lwa_client_secret,
        }

        self.inventory = Inventory(marketplace, self.credentials)
        self.orders = Order(marketplace, self.credentials)
        self.product = Product(marketplace, self.credentials)

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
