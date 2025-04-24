import csv
import gzip
import logging
import os
from typing import Optional

from .exceptions import OnsenpiException


class DataConverter:
    """
    Amazon SPから取得したデータの変換と処理を支援するユーティリティクラス。
    主にレポートファイルの変換に使用します。
    """

    DEFAULT_ENCODING = "cp932"
    DEFAULT_FIELD_SIZE_LIMIT = 200_000_000

    @staticmethod
    def convert_gzip_to_txt(temp_gzip_file_name: str, txt_file_name: str, encoding: Optional[str] = None, field_size_limit: Optional[int] = None, temp_directory: Optional[str] = None, delete_original: bool = False, logger: Optional[logging.Logger] = None) -> bool:
        """
        GZIP形式のファイルをテキスト/TSV形式に変換します。

        Args:
            temp_gzip_file_name: 変換元のGZIPファイル名
            txt_file_name: 変換後のテキストファイル名
            encoding: 文字エンコーディング（デフォルト: cp932）
            field_size_limit: CSVフィールドサイズの上限
            temp_directory: ファイルを配置するディレクトリ
            delete_original: 変換後に元のファイルを削除するかどうか
            logger: ロギング用のロガーインスタンス

        Returns:
            bool: 変換が成功したかどうか

        Raises:
            OnsenpiException: 変換中にエラーが発生した場合
        """
        # ロガーの設定
        log = logger or logging.getLogger("onsenpi.data_converter")

        if encoding is None:
            encoding = DataConverter.DEFAULT_ENCODING
        if field_size_limit is None:
            field_size_limit = DataConverter.DEFAULT_FIELD_SIZE_LIMIT

        if temp_directory is not None:
            temp_gzip_file_name = os.path.join(temp_directory, temp_gzip_file_name)
            txt_file_name = os.path.join(temp_directory, txt_file_name)

        log.debug(f"Converting {temp_gzip_file_name} to {txt_file_name}")
        log.debug(f"Encoding: {encoding}, Field size limit: {field_size_limit}")

        try:
            # CSVのフィールドサイズのリミットを設定
            csv.field_size_limit(field_size_limit)

            # ファイルの存在確認
            if not os.path.exists(temp_gzip_file_name):
                log.error(f"Source file not found: {temp_gzip_file_name}")
                return False

            with gzip.open(temp_gzip_file_name, "rt", encoding=encoding) as gzip_file:
                reader = csv.reader(gzip_file, delimiter="\t", quotechar='"')

                # 出力ディレクトリの存在確認と作成
                output_dir = os.path.dirname(txt_file_name)
                if output_dir and not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                    log.info(f"Created output directory: {output_dir}")

                with open(txt_file_name, "w", newline="", encoding=encoding) as txt_file:
                    writer = csv.writer(txt_file, delimiter="\t", quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    row_count = 0
                    for row in reader:
                        writer.writerow(row)
                        row_count += 1

            log.info(f"Report converted and saved to {txt_file_name} with {row_count} rows")

            # 元のGZIPファイルを削除する場合
            if delete_original:
                os.remove(temp_gzip_file_name)
                log.info(f"Original file {temp_gzip_file_name} deleted")

            return True

        except UnicodeDecodeError as e:
            log.error(f"Encoding error when converting file: {e}")
            raise OnsenpiException(f"エンコーディングエラー: {encoding}は適切ではありません。別のエンコーディングを試してください。") from e
        except PermissionError as e:
            log.error(f"Permission error when accessing file: {e}")
            raise OnsenpiException(f"ファイルアクセス権限エラー: {e}") from e
        except Exception as e:
            log.error(f"Error converting report: {e}", exc_info=True)
            raise OnsenpiException(f"ファイル変換エラー: {e}") from e
