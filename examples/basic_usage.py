"""
onsenpiの基本的な使用例

このサンプルではOnsenpiSPAPIClientの基本的な使い方を示します。
各クラスの主要な機能の使用方法を例示しています。
"""

import logging
import os

from sp_api.base import Marketplaces
from onsenpi import OnsenpiAPIError, OnsenpiException, OnsenpiSPAPIClient


def main():
    # ロギングの設定
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    logger = logging.getLogger("onsenpi_example")

    # 認証情報を設定
    # 実際の利用時は、環境変数やシークレットマネージャーから取得することをお勧めします
    refresh_token = os.environ.get("SP_API_REFRESH_TOKEN", "YOUR_REFRESH_TOKEN")
    lwa_app_id = os.environ.get("SP_API_LWA_APP_ID", "YOUR_LWA_APP_ID")
    lwa_client_secret = os.environ.get("SP_API_LWA_CLIENT_SECRET", "YOUR_LWA_CLIENT_SECRET")

    try:
        # クライアントを初期化
        client = OnsenpiSPAPIClient(marketplace=Marketplaces.JP, refresh_token=refresh_token, lwa_app_id=lwa_app_id, lwa_client_secret=lwa_client_secret, log_level=logging.INFO)
        logger.info("クライアントの初期化が完了しました")

        # 1. 注文情報の取得例
        # 過去30日間の未出荷注文を取得（日付を指定しない場合は自動的に過去30日分を取得）
        try:
            orders = client.get_orders(order_statuses=["Unshipped"])
            order_count = len(orders.get("Orders", []))
            logger.info(f"取得した未出荷注文数: {order_count}")

            # 最初の注文の詳細を取得
            if order_count > 0:
                order_id = orders["Orders"][0]["AmazonOrderId"]
                logger.info(f"注文ID: {order_id} の詳細を取得します")

                order_items = client.get_order_items(order_id)
                item_count = len(order_items.get("OrderItems", []))
                logger.info(f"注文アイテム数: {item_count}")

                # 最初のアイテムの情報表示
                if item_count > 0:
                    item = order_items["OrderItems"][0]
                    logger.info(f"アイテム: {item.get('Title')} - {item.get('QuantityOrdered')}個")
        except OnsenpiAPIError as e:
            logger.error(f"注文情報の取得中にエラーが発生しました: {e}")

        # 2. 商品情報の検索と取得
        try:
            # キーワードで商品カタログを検索
            keyword = "keyboard"
            logger.info(f"キーワード '{keyword}' で商品を検索します")
            search_results = client.product.search_catalog_items(keyword)

            if search_results and "items" in search_results:
                result_count = len(search_results["items"])
                logger.info(f"検索結果: {result_count} 件")

                # 最初の商品の詳細情報を取得
                if result_count > 0:
                    asin = search_results["items"][0].get("asin")
                    logger.info(f"ASIN: {asin} の商品情報を取得します")

                    item_details = client.product.get_item(asin)
                    if item_details:
                        item_title = item_details.get("attributes", {}).get("title", "Unknown")
                        logger.info(f"商品名: {item_title}")
        except OnsenpiAPIError as e:
            logger.error(f"商品情報の検索/取得中にエラーが発生しました: {e}")

        # 3. 在庫レポートのリクエストと処理
        try:
            # 出品レポートをリクエスト
            logger.info("出品レポートをリクエストします")
            report_response = client.inventory.request_listing_report()
            report_id = report_response.get("reportId")
            logger.info(f"レポートID: {report_id} がリクエストされました")

            # 本番環境ではレポートの準備が整うまで待機が必要です
            # 以下はサンプルコードのためコメントアウトします
            """
            logger.info(f"レポートの準備が完了するまで待機します")
            document_id = client.inventory.wait_for_report_to_be_ready(report_id)
            if document_id:
                logger.info(f"ドキュメントID: {document_id} のダウンロードを開始します")

                # レポートをダウンロード
                temp_gzip_file = "temp_report.gz"
                if client.inventory.download_report_data(document_id, temp_gzip_file):
                    logger.info(f"レポートを {temp_gzip_file} にダウンロードしました")

                    # ダウンロードしたGZIPファイルをテキストに変換
                    from onsenpi import DataConverter
                    DataConverter.convert_gzip_to_txt(
                        temp_gzip_file,
                        "report.txt",
                        delete_original=True,
                        logger=logger
                    )
                    logger.info("レポートの変換が完了しました")
            """
        except OnsenpiAPIError as e:
            logger.error(f"レポート処理中にエラーが発生しました: {e}")

        # 4. 競合価格情報の取得
        try:
            # テスト用のASINリスト（実際の使用では実在するASINを指定）
            test_asins = ["B00TEST123", "B00TEST456"]  # サンプル用のダミーASIN
            logger.info(f"{len(test_asins)}件のASINに対する競合価格を取得します")

            # 実際の環境では以下のコードを使用（サンプルコードのためコメントアウト）
            """
            pricing_data = client.product.get_competitive_pricing(test_asins)
            if pricing_data:
                for item in pricing_data.get("Items", []):
                    asin = item.get("ASIN", "Unknown")
                    status = item.get("status", "Unknown")
                    logger.info(f"ASIN: {asin}, ステータス: {status}")

                    if status == "Success":
                        competitive_prices = item.get("Product", {}).get("CompetitivePricing", {}) \
                                                .get("CompetitivePrices", [])
                        for price in competitive_prices:
                            price_type = price.get("CompetitivePriceId")
                            amount = price.get("Price", {}).get("ListingPrice", {}).get("Amount")
                            currency = price.get("Price", {}).get("ListingPrice", {}).get("CurrencyCode")
                            logger.info(f"  価格タイプ: {price_type}, 金額: {amount} {currency}")
            """
        except OnsenpiAPIError as e:
            logger.error(f"価格情報の取得中にエラーが発生しました: {e}")

    except OnsenpiException as e:
        logger.error(f"エラーが発生しました: {e}")

    logger.info("プログラムを終了します")


if __name__ == "__main__":
    main()
