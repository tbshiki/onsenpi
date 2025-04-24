import csv
import gzip
import io
import logging
import os
import shutil
from contextlib import contextmanager
from typing import Optional, List, Dict, Iterator, TextIO, BinaryIO, Union, Tuple

from .exceptions import OnsenpiException


class DataConverter:
    """
    Amazon SP-APIから取得したデータの変換と処理を支援するユーティリティクラス。
    主にレポートファイルの変換に使用します。
    """

    DEFAULT_ENCODING = "cp932"
    DEFAULT_FIELD_SIZE_LIMIT = 200_000_000
    DEFAULT_BUFFER_SIZE = 8192  # 8KB バッファサイズ

    @staticmethod
    def convert_gzip_to_txt(temp_gzip_file_name: str, txt_file_name: str, encoding: Optional[str] = None, field_size_limit: Optional[int] = None, temp_directory: Optional[str] = None, delete_original: bool = False, logger: Optional[logging.Logger] = None, buffer_size: int = DEFAULT_BUFFER_SIZE) -> bool:
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
            buffer_size: ファイル読み書き時のバッファサイズ

        Returns:
            bool: 変換が成功したかどうか

        Raises:
            OnsenpiException: 変換中にエラーが発生した場合
        """
        # ロガーの設定
        log = logger or logging.getLogger("onsenpi.data_converter")

        encoding = encoding or DataConverter.DEFAULT_ENCODING
        field_size_limit = field_size_limit or DataConverter.DEFAULT_FIELD_SIZE_LIMIT

        # パスの結合
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

            # 出力ディレクトリの存在確認と作成
            output_dir = os.path.dirname(txt_file_name)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
                log.info(f"Created output directory: {output_dir}")

            with gzip.open(temp_gzip_file_name, "rt", encoding=encoding) as gzip_file:
                reader = csv.reader(gzip_file, delimiter="\t", quotechar='"')

                with open(txt_file_name, "w", newline="", encoding=encoding, buffering=buffer_size) as txt_file:
                    writer = csv.writer(txt_file, delimiter="\t", quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    row_count = 0
                    for row in reader:
                        writer.writerow(row)
                        row_count += 1

            log.info(f"Report converted and saved to {txt_file_name} with {row_count} rows")

            # 元のGZIPファイルを削除する場合
            if delete_original and os.path.exists(temp_gzip_file_name):
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

    @staticmethod
    def parse_csv_from_string(csv_content: str, delimiter: str = "\t", has_header: bool = True, encoding: str = DEFAULT_ENCODING) -> Tuple[List[str], List[Dict[str, str]]]:
        """
        文字列からCSVデータをパースして、ヘッダーと行データの辞書リストを返します。

        Args:
            csv_content: パースするCSV/TSV形式の文字列
            delimiter: 区切り文字（デフォルト：タブ）
            has_header: ヘッダー行があるかどうか
            encoding: 文字エンコーディング

        Returns:
            ヘッダーリストと行データの辞書リストのタプル

        Raises:
            OnsenpiException: パース中にエラーが発生した場合
        """
        try:
            # 文字列をIOに変換
            with io.StringIO(csv_content) as csvfile:
                reader = csv.reader(csvfile, delimiter=delimiter)

                # ヘッダーを読み取る
                headers = next(reader) if has_header else []

                # データ行をリストに変換
                if has_header:
                    rows = [dict(zip(headers, row)) for row in reader]
                else:
                    rows = [dict(enumerate(row)) for row in reader]

                return headers, rows

        except Exception as e:
            raise OnsenpiException(f"CSV文字列のパースエラー: {e}") from e

    @staticmethod
    @contextmanager
    def open_file_safely(file_path: str, mode: str = "r", encoding: Optional[str] = None) -> Iterator[Union[TextIO, BinaryIO]]:
        """
        ファイルを安全に開くためのコンテキストマネージャ。
        自動的にファイルをクローズし、例外処理を行います。

        Args:
            file_path: 開くファイルのパス
            mode: ファイルオープンモード
            encoding: 文字エンコーディング（テキストモード時のみ）

        Yields:
            開いたファイルオブジェクト

        Raises:
            OnsenpiException: ファイルのオープン時にエラーが発生した場合
        """
        file_obj = None
        try:
            # 'b'がモードに含まれていればバイナリモード、なければテキストモード
            if "b" in mode:
                file_obj = open(file_path, mode)
            else:
                file_obj = open(file_path, mode, encoding=encoding or DataConverter.DEFAULT_ENCODING)
            yield file_obj
        except IOError as e:
            raise OnsenpiException(f"ファイル '{file_path}' を開けませんでした: {e}") from e
        finally:
            if file_obj is not None:
                file_obj.close()

    @staticmethod
    def ensure_directory_exists(directory_path: str) -> None:
        """
        ディレクトリが存在することを保証し、存在しない場合は作成します。

        Args:
            directory_path: 確認/作成するディレクトリパス

        Raises:
            OnsenpiException: ディレクトリ作成中にエラーが発生した場合
        """
        try:
            if directory_path and not os.path.exists(directory_path):
                os.makedirs(directory_path, exist_ok=True)
        except Exception as e:
            raise OnsenpiException(f"ディレクトリ '{directory_path}' の作成に失敗しました: {e}") from e

    @staticmethod
    def safe_copy_file(src_path: str, dst_path: str) -> None:
        """
        ファイルを安全にコピーします。

        Args:
            src_path: コピー元ファイルのパス
            dst_path: コピー先ファイルのパス

        Raises:
            OnsenpiException: コピー中にエラーが発生した場合
        """
        try:
            # コピー先ディレクトリの存在確認
            dst_dir = os.path.dirname(dst_path)
            DataConverter.ensure_directory_exists(dst_dir)

            # ファイルコピー
            shutil.copy2(src_path, dst_path)
        except Exception as e:
            raise OnsenpiException(f"ファイルのコピーに失敗しました '{src_path}' から '{dst_path}': {e}") from e
