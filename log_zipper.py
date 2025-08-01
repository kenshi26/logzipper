import zipfile
from pathlib import Path
from datetime import datetime, timedelta
import shutil
import json

class LogZipper:
    def __init__(self, json_path: str):
        self.log_paths = self.load_log_list(json_path)
        self.threshold_time = datetime.now() - timedelta(days=1)
        self.old_zip_threshold = datetime.now() - timedelta(days=90)

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
                folder_time = datetime.fromtimestamp(subfolder.stat().st_mtime)
            except ValueError:
                continue  # フォルダ名が日付形式でない場合はスキップする。
             
            # フォルダのタイムスタンプが24時間前のものをZIP圧縮して削除する。
            if folder_time <= self.threshold_time:
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

            # フォルダのタイムスタンプが90日以上前のZIPファイルを削除する。 
            for zip_file in log_path.glob("*.zip"):
                try:
                    zipped_time = datetime.fromtimestamp(zip_file.stat().st_mtime)
                    if zipped_time < self.old_zip_threshold:
                        zip_file.unlink()
                        print(f"Deleted old zip : {zip_file}")
                except Exception as e:
                    print(f"Error checking zipped_time for {zip_file}: {e}")

    def run(self):
        for path in self.log_paths:
            if path.exists() and path.is_dir():
                print(f"\nProcessing: {path}")
                self.process_log_path(path)
            else:
                print(f"Invalid path: {path}")

if __name__ == "__main__":
    zipper = LogZipper("params/log_list.json")
    zipper.run()
