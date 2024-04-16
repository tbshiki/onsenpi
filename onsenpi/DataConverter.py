import gzip
import csv
import os


class DataConverter:
    DEFAULT_ENCODING = "cp932"
    DEFAULT_FIELD_SIZE_LIMIT = 200_000_000

    @staticmethod
    def convert_gzip_to_txt(
        temp_gzip_file_name, txt_file_name, encoding=None, field_size_limit=None, temp_directory=None, delete_original=False
    ):
        if encoding is None:
            encoding = DataConverter.DEFAULT_ENCODING
        if field_size_limit is None:
            field_size_limit = DataConverter.DEFAULT_FIELD_SIZE_LIMIT

        if temp_directory is not None:
            temp_gzip_file_name = os.path.join(temp_directory, temp_gzip_file_name)
            txt_file_name = os.path.join(temp_directory, txt_file_name)

        try:
            # CSVのフィールドサイズのリミットを設定
            csv.field_size_limit(field_size_limit)

            with gzip.open(temp_gzip_file_name, "rt", encoding=encoding) as gzip_file:
                reader = csv.reader(gzip_file, delimiter="\t", quotechar='"')

                with open(txt_file_name, "w", newline="", encoding=encoding) as txt_file:
                    writer = csv.writer(txt_file, delimiter="\t", quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    for row in reader:
                        writer.writerow(row)

            print(f"Report converted and saved to {txt_file_name}")

            # 元のGZIPファイルを削除する場合
            if delete_original:
                os.remove(temp_gzip_file_name)
                print(f"Original file {temp_gzip_file_name} deleted.")

        except Exception as e:
            print(f"Error converting report: {e}")
