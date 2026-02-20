from typing import Any, Dict, List, Optional

from sp_api.base import SellingApiException

"""
onsenpiの例外クラスを定義するモジュールです。
より具体的なエラー情報を提供するための例外階層を実装します。
"""


class OnsenpiException(Exception):
    """onsenpiの基本例外クラス"""

    def __init__(self, message: str = "Onsenpi operation failed", code: Optional[str] = None):
        self.message = message
        self.code = code
        super().__init__(message)

    def __str__(self) -> str:
        base_str = self.message
        if self.code:
            base_str += f" (Code: {self.code})"
        return base_str


class OnsenpiAPIError(OnsenpiException):
    """SP-APIとの通信中に発生したエラーをラップする例外クラス"""

    def __init__(self, api_name: str, original_exception: Optional[Exception] = None, message: Optional[str] = None, code: Optional[str] = None, request_id: Optional[str] = None, operation: Optional[str] = None):
        """
        Args:
            api_name (str): エラーが発生したAPIの名前
            original_exception (Exception, optional): 元の例外オブジェクト
            message (str, optional): エラーメッセージ
            code (str, optional): エラーコード
            request_id (str, optional): リクエストID
            operation (str, optional): 実行しようとしていた操作
        """
        self.api_name = api_name
        self.original_exception = original_exception
        self.request_id = request_id
        self.operation = operation

        # SP-APIの元の例外からエラーコードを取得
        if code is None and isinstance(original_exception, SellingApiException):
            code = getattr(original_exception, "code", None)

        # レスポンスからリクエストIDを取得（存在する場合）
        if request_id is None and isinstance(original_exception, SellingApiException):
            try:
                response = getattr(original_exception, "response", {})
                if isinstance(response, dict) and "headers" in response:
                    self.request_id = response["headers"].get("x-amzn-RequestId")
            except (AttributeError, TypeError, KeyError):
                pass

        # メッセージがない場合は元の例外からメッセージを生成
        if message is None:
            if isinstance(original_exception, SellingApiException) or isinstance(original_exception, Exception):
                # 元の例外のメッセージを取得
                orig_msg = getattr(original_exception, "message", str(original_exception))
                message = f"{api_name} API Error: {orig_msg}, Code: {getattr(original_exception, 'code', 'unknown')}"
                if self.operation:
                    message = f"{self.operation} - {message}"
            else:
                message = f"{api_name} Error"
                if self.operation:
                    message = f"{self.operation} - {message}"

        super().__init__(message, code)

    def get_error_details(self) -> Dict[str, Any]:
        """APIエラーの詳細情報を辞書形式で返します。"""
        details = {"api_name": self.api_name, "message": self.message, "code": self.code, "operation": self.operation, "request_id": self.request_id}

        if isinstance(self.original_exception, SellingApiException):
            details.update({"original_code": getattr(self.original_exception, "code", None), "original_response": getattr(self.original_exception, "response", None)})

        return details

    def is_throttling_error(self) -> bool:
        """スロットリングエラー（レート制限）かどうかを判定します"""
        if self.code in ["429", "ThrottlingException", "Throttling"]:
            return True

        if isinstance(self.original_exception, SellingApiException):
            code = getattr(self.original_exception, "code", "")
            if code in ["429", "ThrottlingException", "Throttling"]:
                return True

            try:
                status = getattr(self.original_exception, "response", {}).get("status", 0)
                if status == 429:
                    return True
            except (AttributeError, TypeError):
                pass

        return False

    def is_authentication_error(self) -> bool:
        """認証エラーかどうかを判定します"""
        auth_codes = ["401", "403", "Unauthorized", "Forbidden", "AccessDenied", "InvalidAccessKeyId"]
        if self.code in auth_codes:
            return True

        if isinstance(self.original_exception, SellingApiException):
            code = getattr(self.original_exception, "code", "")
            if code in auth_codes:
                return True

            try:
                status = getattr(self.original_exception, "response", {}).get("status", 0)
                if status in [401, 403]:
                    return True
            except (AttributeError, TypeError):
                pass

        return False

    def is_not_found_error(self) -> bool:
        """リソースが見つからないエラーかどうかを判定します"""
        not_found_codes = ["404", "ResourceNotFound", "NotFound"]
        if self.code in not_found_codes:
            return True

        if isinstance(self.original_exception, SellingApiException):
            code = getattr(self.original_exception, "code", "")
            if code in not_found_codes:
                return True

            try:
                status = getattr(self.original_exception, "response", {}).get("status", 0)
                if status == 404:
                    return True
            except (AttributeError, TypeError):
                pass

        return False

    def get_retry_after(self) -> Optional[int]:
        """
        スロットリングエラーの場合、Retry-Afterヘッダーの値を秒単位で返します。
        ヘッダーがない場合はNoneを返します。
        """
        if not self.is_throttling_error() or not isinstance(self.original_exception, SellingApiException):
            return None

        try:
            response = getattr(self.original_exception, "response", {})
            headers = response.get("headers", {})
            retry_after = headers.get("Retry-After") or headers.get("retry-after")

            if retry_after:
                return int(retry_after)
        except (AttributeError, TypeError, ValueError, KeyError):
            pass

        return None


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

    def __init__(self, message: str, url: Optional[str] = None, file_path: Optional[str] = None, code: Optional[str] = None, status_code: Optional[int] = None):
        self.url = url
        self.file_path = file_path
        self.status_code = status_code
        super().__init__(message, code)

    def get_error_details(self) -> Dict[str, Any]:
        """ダウンロードエラーの詳細情報を辞書形式で返します。"""
        return {"message": self.message, "code": self.code, "url": self.url, "file_path": self.file_path, "status_code": self.status_code}


class OnsenpiValidationError(OnsenpiException):
    """入力データのバリデーション中のエラー"""

    def __init__(self, message: str, field: Optional[str] = None, value: Optional[Any] = None, code: Optional[str] = None, constraints: Optional[List[str]] = None):
        self.field = field
        self.value = value
        self.constraints = constraints or []
        super().__init__(message, code)

    def get_error_details(self) -> Dict[str, Any]:
        """バリデーションエラーの詳細情報を辞書形式で返します。"""
        return {"message": self.message, "code": self.code, "field": self.field, "value": repr(self.value), "constraints": self.constraints}

    def __str__(self) -> str:
        base_str = super().__str__()
        if self.field:
            base_str += f", Field: {self.field}"
        if self.constraints:
            constraints_str = ", ".join(self.constraints)
            base_str += f", Constraints: [{constraints_str}]"
        return base_str
