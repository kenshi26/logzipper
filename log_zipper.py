import zipfile
from pathlib import Path
from datetime import datetime, timedelta
import shutil
import json

class LogZipper:
    def __init__(self, json_path: str):
        self.log_paths = self.load_log_list(json_path)
        self.yesterday = datetime.today().date() - timedelta(days=1)

    def load_log_list(self, json_path: str):
        with open(json_path, 'r', encoding='utf-8') as f:
            return [Path(p) for p in json.load(f)]

    def zip_folder(self, input_folder: Path, output_zip_path: Path):
        # ログファイルをZIP圧縮する
        with zipfile.ZipFile(output_zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as z:
            for file_path in input_folder.rglob('*'):
                if file_path.is_file():
                    arcname = input_folder.name / file_path.relative_to(input_folder)
                    z.write(file_path, arcname)

    def process_log_path(self, log_path: Path):
        for subfolder in log_path.iterdir():
            if not subfolder.is_dir():
                continue
            try:
                folder_date = datetime.strptime(subfolder.name, "%Y-%m-%d").date()
            except ValueError:
                continue  # フォルダ名が日付形式でない場合はスキップする。
             
            # フォルダの日付が昨日までの場合、ZIP圧縮して削除する。
            if folder_date <= self.yesterday:
                zip_path = subfolder.with_suffix(".zip")
                if zip_path.exists():
                    print(f"Skip (already zipped): {zip_path}")
                    continue
                self.zip_folder(subfolder, zip_path)
                print(f"Zipped: {subfolder} → {zip_path}")
                try:
                    shutil.rmtree(subfolder)
                    print(f"Deleted: {subfolder}")
                except Exception as e:
                    print(f"Error deleting {subfolder}: {e}")

    def run(self):
        for path in self.log_paths:
            if path.exists() and path.is_dir():
                print(f"\nProcessing: {path}")
                self.process_log_path(path)
            else:
                print(f"Invalid path: {path}")

if __name__ == "__main__":
    zipper = LogZipper("log_list.json")
    zipper.run()
