"""
onsenpiの例外クラスを定義するモジュールです。
より具体的なエラー情報を提供するための例外階層を実装します。
"""

from typing import Optional, Any, Dict
from sp_api.base import SellingApiException


class OnsenpiException(Exception):
    """onsenpiの基本例外クラス"""

    def __init__(self, message: str = "Onsenpi operation failed", code: Optional[str] = None):
        self.message = message
        self.code = code
        super().__init__(message)


class OnsenpiAPIError(OnsenpiException):
    """SP-APIとの通信中に発生したエラーをラップする例外クラス"""

    def __init__(self, api_name: str, original_exception: Optional[Exception] = None, message: Optional[str] = None, code: Optional[str] = None):
        """
        Args:
            api_name (str): エラーが発生したAPIの名前
            original_exception (Exception, optional): 元の例外オブジェクト
            message (str, optional): エラーメッセージ
            code (str, optional): エラーコード
        """
        self.api_name = api_name
        self.original_exception = original_exception

        # SP-APIの元の例外からエラーコードを取得
        if code is None and isinstance(original_exception, SellingApiException):
            code = getattr(original_exception, "code", None)

        # メッセージがない場合は元の例外からメッセージを生成
        if message is None and isinstance(original_exception, Exception):
            if isinstance(original_exception, SellingApiException):
                message = f"{api_name} API Error: {original_exception}, Code: {getattr(original_exception, 'code', 'unknown')}, Response: {getattr(original_exception, 'response', 'N/A')}"
            else:
                message = f"{api_name} Error: {original_exception}"

        super().__init__(message, code)

    def get_error_details(self) -> Dict[str, Any]:
        """APIエラーの詳細情報を辞書形式で返します。"""
        details = {"api_name": self.api_name, "message": self.message, "code": self.code}

        if isinstance(self.original_exception, SellingApiException):
            details.update({"original_code": getattr(self.original_exception, "code", None), "original_response": getattr(self.original_exception, "response", None)})

        return details


class OnsenpiReportError(OnsenpiException):
    """レポート処理中のエラー"""

    def __init__(self, message: str, report_id: Optional[str] = None, report_type: Optional[str] = None, code: Optional[str] = None):
        self.report_id = report_id
        self.report_type = report_type
        super().__init__(message, code)

    def get_error_details(self) -> Dict[str, Any]:
        """レポートエラーの詳細情報を辞書形式で返します。"""
        return {"message": self.message, "code": self.code, "report_id": self.report_id, "report_type": self.report_type}


class OnsenpiDownloadError(OnsenpiException):
    """ダウンロード処理中のエラー"""

    def __init__(self, message: str, url: Optional[str] = None, file_path: Optional[str] = None, code: Optional[str] = None):
        self.url = url
        self.file_path = file_path
        super().__init__(message, code)

    def get_error_details(self) -> Dict[str, Any]:
        """ダウンロードエラーの詳細情報を辞書形式で返します。"""
        return {"message": self.message, "code": self.code, "url": self.url, "file_path": self.file_path}


class OnsenpiValidationError(OnsenpiException):
    """入力データのバリデーション中のエラー"""

    def __init__(self, message: str, field: Optional[str] = None, value: Optional[Any] = None, code: Optional[str] = None):
        self.field = field
        self.value = value
        super().__init__(message, code)

    def get_error_details(self) -> Dict[str, Any]:
        """バリデーションエラーの詳細情報を辞書形式で返します。"""
        return {"message": self.message, "code": self.code, "field": self.field, "value": repr(self.value)}
