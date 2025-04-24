"""
onsenpiの例外クラスのテスト
"""

import pytest

from onsenpi.exceptions import (
    OnsenpiAPIError,
    OnsenpiDownloadError,
    OnsenpiException,
    OnsenpiReportError,
    OnsenpiValidationError,
)
from tests.conftest import MockSellingApiException


class TestOnsenpiExceptions:
    """例外クラスのテストスイート"""

    def test_base_exception(self):
        """基本例外クラスのテスト"""
        # メッセージのみ
        ex1 = OnsenpiException("テストエラー")
        assert str(ex1) == "テストエラー"

        # コード指定あり
        ex2 = OnsenpiException("テストエラー", code="E001")
        assert str(ex2) == "テストエラー (Code: E001)"
        assert ex2.code == "E001"

    def test_api_error_with_message(self):
        """メッセージ指定でのAPIエラーのテスト"""
        # 基本的なAPIエラー
        api_error = OnsenpiAPIError("TestAPI", message="APIエラー", code="500")
        assert api_error.api_name == "TestAPI"
        assert api_error.message == "APIエラー"
        assert api_error.code == "500"
        assert api_error.original_exception is None

    def test_api_error_with_original_exception(self):
        """元の例外からのAPIエラー生成テスト"""
        # カスタムSellingApiExceptionを作成
        ex = MockSellingApiException(message="元のエラー", code="429", response={"status": 429, "headers": {"x-amzn-RequestId": "req-123"}})

        api_error = OnsenpiAPIError("TestAPI", ex, operation="商品検索")
        assert "TestAPI" in str(api_error)
        assert "429" in api_error.get_error_details()["original_code"]
        assert api_error.request_id == "req-123"
        assert api_error.operation == "商品検索"

    @pytest.mark.parametrize("error_code,status_code,is_throttling,is_auth", [("429", 429, True, False), ("ThrottlingException", 429, True, False), ("401", 401, False, True), ("AccessDenied", 401, False, True), ("500", 500, False, False)])
    def test_api_error_detection(self, error_code, status_code, is_throttling, is_auth):
        """API例外検出機能のパラメトリックテスト"""
        # 元の例外を用意
        ex = MockSellingApiException(message=f"Test {error_code}", code=error_code, response={"status": status_code, "headers": {}})

        error = OnsenpiAPIError("TestAPI", ex)
        assert error.is_throttling_error() == is_throttling
        assert error.is_authentication_error() == is_auth

    def test_api_error_detection_direct_code(self):
        """直接コード指定でのAPI例外検出テスト"""
        # コード直接指定
        error1 = OnsenpiAPIError("TestAPI", code="429")
        assert error1.is_throttling_error() == True
        assert error1.is_authentication_error() == False

        error2 = OnsenpiAPIError("TestAPI", code="401")
        assert error2.is_throttling_error() == False
        assert error2.is_authentication_error() == True

    def test_api_error_details(self):
        """APIエラー詳細情報のテスト"""
        ex = MockSellingApiException(message="詳細テスト", code="500", response={"status": 500, "headers": {"x-amzn-RequestId": "req-details"}})

        error = OnsenpiAPIError("DetailAPI", ex, operation="詳細取得")
        details = error.get_error_details()

        assert "api_name" in details
        assert details["api_name"] == "DetailAPI"
        assert "original_code" in details
        assert details["original_code"] == "500"
        assert "request_id" in details
        assert details["request_id"] == "req-details"
        assert "operation" in details
        assert details["operation"] == "詳細取得"

    def test_report_error(self):
        """レポート例外クラスのテスト"""
        report_error = OnsenpiReportError("レポートエラー", report_id="report-123", report_type="GET_FLAT_FILE_ORDERS_DATA", code="R001")

        # 文字列表現の確認
        assert "レポートエラー" in str(report_error)
        assert "R001" in str(report_error)

        # 詳細情報の確認
        details = report_error.get_error_details()
        assert details["report_id"] == "report-123"
        assert details["report_type"] == "GET_FLAT_FILE_ORDERS_DATA"
        assert details["code"] == "R001"

    def test_download_error(self):
        """ダウンロード例外クラスのテスト"""
        download_error = OnsenpiDownloadError("ダウンロードエラー", url="https://example.com/file.txt", file_path="/tmp/file.txt", status_code=404, code="D001")

        # 文字列表現の確認
        assert "ダウンロードエラー" in str(download_error)

        # 詳細情報の確認
        details = download_error.get_error_details()
        assert details["url"] == "https://example.com/file.txt"
        assert details["file_path"] == "/tmp/file.txt"
        assert details["status_code"] == 404
        assert details["code"] == "D001"

    def test_validation_error(self):
        """バリデーション例外クラスのテスト"""
        constraints = ["正しいメールアドレス形式である必要があります", "必須項目です"]
        validation_error = OnsenpiValidationError("バリデーションエラー", field="email", value="invalid", constraints=constraints, code="V001")

        # 文字列表現の確認
        error_str = str(validation_error)
        assert "バリデーションエラー" in error_str
        assert "Field: email" in error_str
        assert "Constraints: [" in error_str
        assert "正しいメールアドレス形式" in error_str

        # 詳細情報の確認
        details = validation_error.get_error_details()
        assert details["field"] == "email"
        assert details["value"] == "'invalid'"  # repr()形式で格納される
        assert len(details["constraints"]) == 2
        assert details["code"] == "V001"
