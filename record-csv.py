import csv
import ctypes
import os
import queue
import threading
import tkinter as tk
import tkinter.font as tkFont
from datetime import datetime
from tkinter import filedialog

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
        self.title("KIT学生証・職員証スキャナ")
        self.geometry("650x300")
        self.custom_font = tkFont.Font(family="Helvetica", size=10)
        self.bold_font = tkFont.Font(
            family="Helvetica", size=13, weight="bold"
        )
        self.bigger_bold_font = tkFont.Font(
            family="Helvetica", size=15, weight="bold"
        )
        self.init_ui()
        self.set_default_save_path()
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
        # 上部のウィジェットの設定
        self.scan_time_label = tk.Label(
            self, text="スキャン時間:", font=self.bold_font
        )
        self.scan_time_label.pack(pady=(10, 0))

        self.id_label = tk.Label(self, text="ID:", font=self.bigger_bold_font)
        self.id_label.pack(pady=(10, 0))

        self.ready_label = tk.Label(
            self, text="準備完了", font=self.bigger_bold_font
        )
        self.ready_label.pack(pady=(10, 0))

        # 下部のウィジェットの設定
        self.file_path_label = tk.Label(
            self, text="ファイルパス: 未選択", font=self.custom_font
        )
        self.file_path_label.pack(side=tk.BOTTOM, pady=(10, 0))

        self.save_button = tk.Button(
            self,
            text="ファイル保存場所を選択",
            command=self.select_save_directory,
            font=self.custom_font,
        )
        self.save_button.pack(side=tk.BOTTOM, pady=(10, 10))
        self.save_button.pack()

    def set_default_save_path(self):
        default_save_directory = os.getcwd()
        today = datetime.now().strftime("%Y%m%d")
        file_name = f"scan-{today}.csv"
        self.file_path = os.path.join(default_save_directory, file_name)
        self.file_path_label.config(text=f"ファイルパス: {self.file_path}")

    def update_labels(self, tag_id, scan_time):
        self.id_label.config(text=f"ID: {tag_id}")
        self.scan_time_label.config(
            text=f"スキャン時間: {scan_time.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        self.ready_label.config(text="準備完了")
        self.save_to_csv(tag_id, scan_time)

    def select_save_directory(self):
        save_directory = filedialog.askdirectory(title="保存場所を選択")
        if save_directory:
            today = datetime.now().strftime("%Y%m%d")
            file_name = f"scan-{today}.csv"
            self.file_path = os.path.join(save_directory, file_name)
            self.file_path_label.config(text=f"ファイルパス: {self.file_path}")

    def save_to_csv(self, tag_id, scan_time):
        if (
            not os.path.isfile(self.file_path)
            or os.path.getsize(self.file_path) == 0
        ):
            with open(
                self.file_path, "w", newline="", encoding="utf-8-sig"
            ) as file:
                writer = csv.writer(file)
                writer.writerow(["id", "scan_datetime"])

        with open(
            self.file_path, "r", newline="", encoding="utf-8-sig"
        ) as file:
            reader = csv.reader(file)
            if any(row[0] == tag_id for row in reader):
                self.ready_label.config(text="既にスキャンされています")
                return

        with open(
            self.file_path, "a", newline="", encoding="utf-8-sig"
        ) as file:
            writer = csv.writer(file)
            writer.writerow([tag_id, scan_time.strftime("%Y-%m-%d %H:%M:%S")])
            self.ready_label.config(text="スキャン完了")


if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
