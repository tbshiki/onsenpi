"""
onsenpiの例外クラスを定義するモジュールです。
"""

from sp_api.base import SellingApiException


class OnsenpiException(Exception):
    """onsenpiの基本例外クラス"""

    pass


class OnsenpiAPIError(OnsenpiException):
    """SP-APIとの通信中に発生したエラーをラップする例外クラス"""

    def __init__(self, api_name, original_exception=None, message=None):
        """
        Args:
            api_name (str): エラーが発生したAPIの名前
            original_exception (Exception, optional): 元の例外オブジェクト
            message (str, optional): エラーメッセージ
        """
        self.api_name = api_name
        self.original_exception = original_exception

        if message is None and isinstance(original_exception, Exception):
            if isinstance(original_exception, SellingApiException):
                message = f"{api_name} API Error: {original_exception}, Code: {original_exception.code}, Response: {original_exception.response}"
            else:
                message = f"{api_name} Error: {original_exception}"

        super().__init__(message)


class OnsenpiReportError(OnsenpiException):
    """レポート処理中のエラー"""

    pass


class OnsenpiDownloadError(OnsenpiException):
    """ダウンロード処理中のエラー"""

    pass
