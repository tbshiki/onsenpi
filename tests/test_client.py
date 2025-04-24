"""
OnsenpiSPAPIClientのテスト
"""

import pytest
from onsenpi import OnsenpiSPAPIClient


def test_client_initialization():
    """クライアントの初期化テスト"""
    # 注: このテストはモックが必要かもしれません
    # このサンプルコードはテスト作成の参考として提供しています
    client = OnsenpiSPAPIClient(credentials={"refresh_token": "test_token", "lwa_app_id": "test_app_id", "lwa_client_secret": "test_secret", "aws_access_key": "test_access_key", "aws_secret_key": "test_secret_key", "role_arn": "test_role_arn"})
    assert client is not None
