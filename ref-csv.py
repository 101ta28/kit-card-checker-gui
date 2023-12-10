import csv
import ctypes
import os
import queue
import threading
import tkinter as tk
import tkinter.font as tkFont
from datetime import datetime
from tkinter import filedialog, messagebox

import nfc

# 高画質化
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(True)
except:
    pass


# NFCの読み取りを行うスレッド
class NFCReaderThread(threading.Thread):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback
        self.daemon = True

    def run(self):
        clf = nfc.ContactlessFrontend("usb")
        while clf.connect(rdwr={"on-connect": self.on_connect}):
            pass

    def on_connect(self, tag):
        try:
            # Type3Tag以外の場合は処理をスキップ
            if not isinstance(tag, nfc.tag.tt3.Type3Tag):
                print("Unsupported NFC tag type:", type(tag))
                return False

            try:
                sc = nfc.tag.tt3.ServiceCode(0x200B >> 6, 0x200B & 0x3F)
                bc = nfc.tag.tt3.BlockCode(0, service=0)
                data = tag.read_without_encryption([sc], [bc])
                tag_id = data[0:8].decode("utf-8")
                self.callback(tag_id)
            except Exception as e:
                print("Error reading NFC tag:", e)

        except AttributeError as e:
            print("AttributeError:", e)
            return False

        return True


# メインウィンドウのクラス
class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("KIT学生証・職員証スキャナ(リスト参照版)")
        self.geometry("650x400")
        self.file_path = None  # CSVファイルパスを初期化
        self.custom_font = tkFont.Font(family="Helvetica", size=10)
        self.bold_font = tkFont.Font(
            family="Helvetica", size=13, weight="bold"
        )
        self.bigger_bold_font = tkFont.Font(
            family="Helvetica", size=15, weight="bold"
        )
        self.init_ui()
        self.nfc_queue = queue.Queue()
        self.after(100, self.process_queue)
        self.nfc_thread = NFCReaderThread(self.nfc_queue.put)
        self.nfc_thread.start()

    def process_queue(self):
        try:
            while True:
                tag_id = self.nfc_queue.get_nowait()
                scan_time = datetime.now()
                self.update_labels(tag_id, scan_time)
        except queue.Empty:
            pass
        self.after(100, self.process_queue)

    def init_ui(self):
        self.scan_time_label = tk.Label(
            self, text="スキャン時間:", font=self.bold_font
        )
        self.scan_time_label.pack(pady=(10, 0))

        self.id_label = tk.Label(self, text="ID:", font=self.bigger_bold_font)
        self.id_label.pack(pady=(10, 0))

        self.name_label = tk.Label(
            self, text="名前:", font=self.bigger_bold_font
        )
        self.name_label.pack(pady=(10, 0))

        self.ready_label = tk.Label(
            self, text="準備完了", font=self.bigger_bold_font
        )
        self.ready_label.pack(pady=(10, 0))

        self.file_path_label = tk.Label(
            self, text="参照CSVファイル: 未選択", font=self.custom_font
        )
        self.file_path_label.pack(side=tk.BOTTOM, pady=(10, 0))

        self.save_button = tk.Button(
            self,
            text="CSVファイルを選択",
            command=self.select_csv_file,
            font=self.custom_font,
        )
        self.save_button.pack(side=tk.BOTTOM, pady=(10, 10))

    def select_csv_file(self):
        file_path = filedialog.askopenfilename(
            title="CSVファイルを選択", filetypes=[("CSVファイル", "*.csv")]
        )
        if file_path:
            if self.check_csv_format(file_path):
                self.file_path = file_path
                self.file_path_label.config(
                    text=f"参照CSVファイル: {self.file_path}"
                )
            else:
                messagebox.showerror("エラー", "CSVの形式が不正です。")

    def check_csv_format(self, file_path):
        try:
            with open(
                file_path, "r", newline="", encoding="utf-8-sig"
            ) as file:
                reader = csv.reader(file)
                headers = next(reader)
                return (
                    len(headers) >= 2
                    and headers[0] == "id"
                    and headers[1] == "name"
                )
        except Exception as e:
            print("CSVファイルの読み込み中にエラーが発生しました:", e)
            return False

    def update_labels(self, tag_id, scan_time):
        if self.file_path is None:
            messagebox.showwarning("警告", "CSVファイルが読み込まれていません。")
            return

        name, status = self.update_csv(tag_id, scan_time)
        self.id_label.config(text=f"ID: {tag_id}")
        self.name_label.config(text=f"名前: {name}")
        self.scan_time_label.config(
            text=f"スキャン時間: {scan_time.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        if status == "scanned":
            self.ready_label.config(text="既にスキャンされています")
        elif status == "new":
            self.ready_label.config(text="スキャン済み")
        else:
            self.ready_label.config(text="準備完了")

    def update_csv(self, tag_id, scan_time):
        data = []
        name = "不明"
        status = "not_found"

        if os.path.isfile(self.file_path):
            with open(
                self.file_path, "r", newline="", encoding="utf-8-sig"
            ) as file:
                reader = csv.DictReader(file)
                fieldnames = [
                    field for field in reader.fieldnames if field
                ]  # 空のフィールドを無視

                # 不足しているフィールドの追加
                if "scanned" not in fieldnames:
                    fieldnames.append("scanned")
                if "scanned_datetime" not in fieldnames:
                    fieldnames.append("scanned_datetime")

                for row in reader:
                    # 空のフィールドを除去
                    row = {key: row[key] for key in fieldnames if key in row}

                    if row["id"] == tag_id:
                        name = row["name"]
                        if row.get("scanned") == "true":
                            status = "scanned"
                        else:
                            row["scanned"] = "true"
                            row["scanned_datetime"] = scan_time.strftime(
                                "%Y-%m-%d %H:%M:%S"
                            )
                            status = "new"
                    data.append(row)

                # 新規IDのデータを追加
                if status == "not_found":
                    new_row = {key: "" for key in fieldnames}
                    new_row.update(
                        {
                            "id": tag_id,
                            "name": "不明",
                            "scanned": "true",
                            "scanned_datetime": scan_time.strftime(
                                "%Y-%m-%d %H:%M:%S"
                            ),
                        }
                    )
                    data.append(new_row)
                    status = "new"

            # ファイルにデータを書き戻す
            with open(
                self.file_path, "w", newline="", encoding="utf-8-sig"
            ) as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)

        return name, status


if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
