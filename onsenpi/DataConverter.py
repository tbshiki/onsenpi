import csv
import gzip
import io
import logging
import os
import shutil
from contextlib import contextmanager
from typing import Optional, List, Dict, Iterator, TextIO, BinaryIO, Union, Tuple, Any

from .exceptions import OnsenpiException


class DataConverter:
    """
    Amazon SP-APIから取得したデータの変換と処理を支援するユーティリティクラス。
    主にレポートファイルの変換に使用します。
    """

    DEFAULT_ENCODING = "cp932"
    DEFAULT_FIELD_SIZE_LIMIT = 200_000_000
    DEFAULT_BUFFER_SIZE = 8192  # 8KB バッファサイズ
    CHUNK_SIZE = 1024 * 1024  # 1MB チャンクサイズ（大きなファイルの効率的な処理用）

    @staticmethod
    def convert_gzip_to_txt(temp_gzip_file_name: str, txt_file_name: str, encoding: Optional[str] = None, field_size_limit: Optional[int] = None, temp_directory: Optional[str] = None, delete_original: bool = False, logger: Optional[logging.Logger] = None, buffer_size: int = DEFAULT_BUFFER_SIZE) -> bool:
        """
        GZIP形式のファイルをテキスト/TSV形式に変換します。メモリ効率を考慮した実装です。

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

            with gzip.open(temp_gzip_file_name, "rt", encoding=encoding, buffering=buffer_size) as gzip_file:
                reader = csv.reader(gzip_file, delimiter="\t", quotechar='"')

                with open(txt_file_name, "w", newline="", encoding=encoding, buffering=buffer_size) as txt_file:
                    writer = csv.writer(txt_file, delimiter="\t", quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    row_count = 0
                    for row in reader:
                        writer.writerow(row)
                        row_count += 1
                        # 大量のデータを処理する場合はメモリ使用量を抑えるため、定期的にログ出力
                        if row_count % 10000 == 0:
                            log.debug(f"Processed {row_count} rows")

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
    def convert_gzip_to_txt_streaming(temp_gzip_file_name: str, txt_file_name: str, encoding: Optional[str] = None, temp_directory: Optional[str] = None, delete_original: bool = False, logger: Optional[logging.Logger] = None) -> bool:
        """
        GZIP形式のファイルをテキスト形式に変換します。ストリーミング方式で大きなファイルも効率的に処理します。
        CSVパースを行わず、単純にテキスト変換するため、より高速です。

        Args:
            temp_gzip_file_name: 変換元のGZIPファイル名
            txt_file_name: 変換後のテキストファイル名
            encoding: 文字エンコーディング（デフォルト: cp932）
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
        encoding = encoding or DataConverter.DEFAULT_ENCODING

        # パスの結合
        if temp_directory is not None:
            temp_gzip_file_name = os.path.join(temp_directory, temp_gzip_file_name)
            txt_file_name = os.path.join(temp_directory, txt_file_name)

        log.debug(f"Converting {temp_gzip_file_name} to {txt_file_name} using streaming method")
        log.debug(f"Encoding: {encoding}")

        try:
            # ファイルの存在確認
            if not os.path.exists(temp_gzip_file_name):
                log.error(f"Source file not found: {temp_gzip_file_name}")
                return False

            # 出力ディレクトリの存在確認と作成
            output_dir = os.path.dirname(txt_file_name)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
                log.info(f"Created output directory: {output_dir}")

            total_size = 0
            with gzip.open(temp_gzip_file_name, "rb") as gz_file, open(txt_file_name, "wb") as txt_file:
                while True:
                    chunk = gz_file.read(DataConverter.CHUNK_SIZE)
                    if not chunk:
                        break
                    txt_file.write(chunk)
                    total_size += len(chunk)
                    log.debug(f"Processed {total_size / (1024 * 1024):.2f} MB")

            log.info(f"Report converted and saved to {txt_file_name}, total size: {total_size / (1024 * 1024):.2f} MB")

            # 元のGZIPファイルを削除する場合
            if delete_original and os.path.exists(temp_gzip_file_name):
                os.remove(temp_gzip_file_name)
                log.info(f"Original file {temp_gzip_file_name} deleted")

            return True

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
    def parse_csv_from_file(file_path: str, delimiter: str = "\t", has_header: bool = True, encoding: Optional[str] = None, chunk_size: int = 1000) -> Iterator[Dict[str, str]]:
        """
        CSVファイルを効率的にパースし、行データの辞書をイテレータとして返します。
        メモリ効率を考慮して、指定されたチャンクサイズずつ処理します。

        Args:
            file_path: パースするCSVファイルのパス
            delimiter: 区切り文字（デフォルト：タブ）
            has_header: ヘッダー行があるかどうか
            encoding: 文字エンコーディング（指定がなければデフォルトエンコーディングを使用）
            chunk_size: 一度に処理する行数

        Yields:
            各行のデータを表す辞書

        Raises:
            OnsenpiException: パース中にエラーが発生した場合
        """
        encoding = encoding or DataConverter.DEFAULT_ENCODING

        try:
            with open(file_path, "r", encoding=encoding) as csvfile:
                reader = csv.reader(csvfile, delimiter=delimiter)

                # ヘッダーの処理
                if has_header:
                    headers = next(reader)
                else:
                    # ヘッダーがない場合は列インデックスを使用
                    first_row = next(reader)
                    headers = list(range(len(first_row)))
                    # 最初の行も処理するために位置を戻す
                    csvfile.seek(0)
                    if has_header:
                        next(reader)  # ヘッダー行をスキップ

                # チャンク単位で読み込み
                for row in reader:
                    if not row:  # 空行をスキップ
                        continue
                    yield dict(zip(headers, row))

        except Exception as e:
            raise OnsenpiException(f"CSVファイル '{file_path}' のパースエラー: {e}") from e

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

    @staticmethod
    def merge_tsv_files(file_paths: List[str], output_file: str, encoding: Optional[str] = None, include_header: bool = True) -> int:
        """
        複数のTSVファイルを1つのファイルにマージします。
        最初のファイルのヘッダーが保持され、その他のファイルのヘッダーは無視されます。

        Args:
            file_paths: マージするTSVファイルのパスのリスト
            output_file: 出力先のファイルパス
            encoding: 文字エンコーディング（指定がなければデフォルトを使用）
            include_header: 出力ファイルにヘッダーを含めるかどうか

        Returns:
            マージされた行数（ヘッダー行を除く）

        Raises:
            OnsenpiException: マージ処理中にエラーが発生した場合
        """
        encoding = encoding or DataConverter.DEFAULT_ENCODING
        total_rows = 0

        try:
            # 出力ディレクトリが存在することを確認
            output_dir = os.path.dirname(output_file)
            if output_dir:
                DataConverter.ensure_directory_exists(output_dir)

            # 出力ファイルを開く
            with open(output_file, "w", encoding=encoding, newline="") as outfile:
                writer = csv.writer(outfile, delimiter="\t", quotechar='"', quoting=csv.QUOTE_MINIMAL)

                # 各入力ファイルを処理
                for i, file_path in enumerate(file_paths):
                    if not os.path.exists(file_path):
                        raise OnsenpiException(f"ファイル '{file_path}' が存在しません")

                    with open(file_path, "r", encoding=encoding, newline="") as infile:
                        reader = csv.reader(infile, delimiter="\t", quotechar='"')

                        # ヘッダー行の処理
                        header = next(reader, None)
                        if i == 0 and include_header and header:
                            writer.writerow(header)

                        # データ行の処理
                        for row in reader:
                            writer.writerow(row)
                            total_rows += 1

            return total_rows

        except Exception as e:
            raise OnsenpiException(f"TSVファイルのマージに失敗しました: {e}") from e

    @staticmethod
    def extract_columns_from_tsv(input_file: str, output_file: str, columns: List[int], encoding: Optional[str] = None, include_header: bool = True) -> int:
        """
        TSVファイルから指定した列のみを抽出して新しいTSVファイルを作成します。

        Args:
            input_file: 入力TSVファイルのパス
            output_file: 出力TSVファイルのパス
            columns: 抽出する列のインデックスのリスト（0から始まる）
            encoding: 文字エンコーディング（指定がなければデフォルトを使用）
            include_header: 出力ファイルにヘッダーを含めるかどうか

        Returns:
            処理した行数（ヘッダーを除く）

        Raises:
            OnsenpiException: 処理中にエラーが発生した場合
        """
        encoding = encoding or DataConverter.DEFAULT_ENCODING
        processed_rows = 0

        try:
            # 出力ディレクトリが存在することを確認
            output_dir = os.path.dirname(output_file)
            if output_dir:
                DataConverter.ensure_directory_exists(output_dir)

            with open(input_file, "r", encoding=encoding, newline="") as infile, open(output_file, "w", encoding=encoding, newline="") as outfile:
                reader = csv.reader(infile, delimiter="\t", quotechar='"')
                writer = csv.writer(outfile, delimiter="\t", quotechar='"', quoting=csv.QUOTE_MINIMAL)

                # ヘッダー行の処理
                header = next(reader, None)
                if header and include_header:
                    # 指定された列のみを抽出
                    filtered_header = [header[col] for col in columns if col < len(header)]
                    writer.writerow(filtered_header)

                # データ行の処理
                for row in reader:
                    if row:
                        # 指定された列のみを抽出（インデックスの範囲チェック付き）
                        filtered_row = [row[col] if col < len(row) else "" for col in columns]
                        writer.writerow(filtered_row)
                        processed_rows += 1

            return processed_rows

        except Exception as e:
            raise OnsenpiException(f"TSVファイルからの列抽出に失敗しました: {e}") from e
