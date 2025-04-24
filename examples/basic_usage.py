"""
onsenpiの基本的な使用例

このサンプルではOnsenpiSPAPIClientの基本的な使い方を示します。
"""

from onsenpi import OnsenpiSPAPIClient


def main():
    # 認証情報を設定
    # 実際の利用時は、環境変数やシークレットマネージャーから取得することをお勧めします
    credentials = {"refresh_token": "YOUR_REFRESH_TOKEN", "lwa_app_id": "YOUR_LWA_APP_ID", "lwa_client_secret": "YOUR_LWA_CLIENT_SECRET", "aws_access_key": "YOUR_AWS_ACCESS_KEY", "aws_secret_key": "YOUR_AWS_SECRET_KEY", "role_arn": "YOUR_ROLE_ARN"}

    # クライアントを初期化
    client = OnsenpiSPAPIClient(credentials, marketplace="JP")

    # 注文情報の取得例
    # 2023年1月1日以降に作成された注文を取得
    orders = client.get_orders(created_after="2023-01-01")
    print(f"取得した注文数: {len(orders)}")

    # 在庫情報の取得例
    inventory = client.get_inventory()
    print(f"在庫アイテム数: {len(inventory)}")

    # 商品情報の取得例
    asin = "EXAMPLE_ASIN"
    product = client.get_product_by_asin(asin)
    print(f"商品情報: {product}")


if __name__ == "__main__":
    main()
