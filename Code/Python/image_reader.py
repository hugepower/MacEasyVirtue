import argparse
import re
import sys
from pathlib import Path

from PIL import Image
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QListWidget,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QStatusBar,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from qt_material import apply_stylesheet


class ParserA1111:
    """
    这是一个专门读取 A1111 WebUI 图片的类，会返回一个处理好的词典。
    """

    def __init__(self, image_path):
        self.image_path = image_path

    def parse_steps(self, text):
        """
        对steps信息进行处理，返回一个键值对字典。
        处理的逻辑是：
        - 先用正则表达式匹配出每个键值对，保存到一个列表中
        - 然后把列表转换成字典，并把每个键用capitalize函数转换成大写
        - 如果匹配出错，打印提示信息，并返回一个空字典
        """
        try:
            pairs = re.findall(r"(\w+):\s*([^,]+)", text)
            data = {k.capitalize(): v for k, v in dict(pairs).items()}
            return data
        except ValueError:
            print("请确保文本中包含:和,作为分隔符")
            return {}

    def split_string(self, text):
        """
        对 negative 信息和 description 信息进行处理，返回一个字符串列表。
        处理的逻辑是：
        - 先用正则表达式匹配出括号内的内容，保存到一个列表中
        - 然后把匹配到的内容从原字符串中删除，再用逗号分割字符串，得到另一个列表
        - 最后把两个列表合并，并去掉空白和空元素，返回结果
        """
        patterns = [r"(?<=,)\s*\([^)]+\)\s*(?=,)", r"\w+\s*\([^)]+\)\s*\w+"]
        matches = []
        for pattern in patterns:
            matches += re.findall(pattern, text)
        if matches:
            for match in matches:
                text = text.replace(match, "").strip()
        result = text.split(",")
        result = [item.strip() for item in result if item]
        result = matches + result
        return result

    def read_image_info(self) -> dict:
        """
        读取图片的信息，返回一个字典，包含以下四个键：
        - description: 描述信息，是一个字符串列表
        - negative: 负面信息，是一个字符串列表
        - steps: 步骤信息，是一个键值对字典
        - image_path: 图片的路径，是一个字符串
        如果图片没有信息，返回一个空字典。
        """
        data = {
            "description": "",
            "negative": "",
            "steps": "",
            "image_path": self.image_path,
            "image_type": "A1111 WebUI",
            "raw": "",
        }
        with Image.open(self.image_path, mode="r") as f:
            image_info = f.info.get("parameters", None)
            if image_info is None:
                return {}

            items = re.sub(r"[，]", ",", str(image_info)).split("\n")
            for item in items:
                if "Negative" in item:
                    data["negative"] = self.split_string(item.split(": ")[-1])
                elif "Steps" in item:
                    data["steps"] = self.parse_steps(item)
                else:
                    data["description"] = self.split_string(item)
            data["raw"] = "\n\n".join(items)
        return data


# 创建一个继承自QWidget的子类，作为主窗口
class MyWindow(QWidget):
    # 定义构造函数
    def __init__(self, image_list):
        super().__init__()

        # 创建一个QHBoxLayout对象，作为左右布局
        hbox = QHBoxLayout()

        # 在左边的布局中，创建一个QLabel对象，用来显示图片
        self.image_label = QLabel()

        # 创建一个QListWidget对象，用来存储图片列表
        self.image_list = QListWidget()

        # 使用for循环来遍历传入的图片列表，并添加到QListWidget对象中
        for image_path in image_list:
            self.image_list.addItem(str(image_path))

        # 设置QLabel对象的固定尺寸，根据你的需要调整
        # self.image_label.setFixedSize(900, 800)

        # 将图片标签添加到左边的布局中
        hbox.addWidget(self.image_label)

        # 在右边的布局中，创建一个QVBoxLayout对象，作为垂直布局
        vbox = QVBoxLayout()

        # 在垂直布局中，创建一个QGridLayout对象，作为网格布局
        grid = QGridLayout()

        # 在网格布局中，创建三个QTextEdit对象，作为文本框
        self.edit1 = QTextEdit()
        self.edit2 = QTextEdit()
        self.edit3 = QTextEdit()

        # 创建一个表格对象
        self.table = QTableWidget()
        # 设置表格的行数和列数
        self.table.setRowCount(10)
        self.table.setColumnCount(2)

        # 设置表格的表头
        self.table.setHorizontalHeaderLabels(["参数", "值"])

        # 设置表格的大小策略为QSizePolicy.Expanding
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # 将文本框添加到网格布局中的不同单元格中
        grid.addWidget(self.edit1, 0, 0)
        grid.addWidget(self.edit2, 1, 0)
        grid.addWidget(self.table, 2, 0)

        # 将网格布局添加到垂直布局中
        vbox.addLayout(grid)

        # 在垂直布局中，创建一个QStatusBar对象，作为状态栏
        self.status_bar = QStatusBar()

        # 在状态栏中，创建五个QPushButton对象，作为编辑、保存、删除、分享、更新按钮
        self.edit_button = QPushButton("Edit")
        self.save_button = QPushButton("Save")
        self.delete_button = QPushButton("Delete")
        self.share_button = QPushButton("Share")
        self.update_button = QPushButton("Update")
        self.prev_button = QPushButton("prev")
        self.next_button = QPushButton("next")

        # 将按钮添加到状态栏中
        self.status_bar.addWidget(self.edit_button)
        self.status_bar.addWidget(self.save_button)
        self.status_bar.addWidget(self.delete_button)
        self.status_bar.addWidget(self.share_button)
        self.status_bar.addWidget(self.update_button)
        self.status_bar.addWidget(self.prev_button)
        self.status_bar.addWidget(self.next_button)

        # 为两个按钮绑定槽函数，用来处理点击事件
        self.prev_button.clicked.connect(self.prev_image)
        self.next_button.clicked.connect(self.next_image)

        # 将状态栏添加到垂直布局中的底部
        vbox.addWidget(self.status_bar)

        # 将垂直布局添加到右边的布局中
        hbox.addLayout(vbox)

        # 设置左右两边的比例为1:1，即大小一样
        hbox.setStretch(0, 1)
        hbox.setStretch(1, 1)

        # 将左右布局设置为主窗口的布局
        self.setLayout(hbox)

        # 让窗体最大化显示
        self.showMaximized()

        # 在右侧的垂直布局中，创建一个QTextEdit对象，作为文本框
        self.edit4 = QTextEdit()
        # 设置文本框的大小策略为QSizePolicy.Expanding
        self.edit4.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # 默认隐藏显示 raw 信息的文本框
        self.edit4.hide()

        # 将文本框添加到垂直布局中的合适位置，比如在表格的下方，并设置比例因子为1
        vbox.addWidget(self.edit4, 1)
        # 在右侧的状态栏中，创建一个QPushButton对象，作为切换按钮
        self.switch_button = QPushButton("切换显示模式")
        # 将按钮添加到状态栏中的合适位置，比如在更新按钮的右边
        self.status_bar.addWidget(self.switch_button)
        # 为按钮绑定一个槽函数，用来处理点击事件
        self.switch_button.clicked.connect(self.switch_mode)

        # 设置图片列表的当前索引为0，即显示第一张图片
        self.current_index = 0
        # 调用self.show_image函数，传入当前索引
        self.show_image(self.current_index)

    # 定义槽函数，用来切换显示模式
    def switch_mode(self):
        # 判断当前的显示模式
        if self.table.isVisible():
            self.edit1.hide()
            self.edit2.hide()
            self.table.hide()
            self.edit4.show()
            # 不要问为什么要用中文，我学比亚迪的
            self.switch_button.setText("简单模式")
        else:
            self.edit1.show()
            self.edit2.show()
            self.table.show()
            self.edit4.hide()
            self.switch_button.setText("复杂模式")

    # 缩放图片到合适的大小，保持宽高比
    def scale_pixmap(self, pixmap):
        pixmap = pixmap.scaled(
            self.image_label.width(),
            self.image_label.height(),
            Qt.KeepAspectRatio,
        )
        # 设置图片标签的图片
        self.image_label.setPixmap(pixmap)
        return pixmap

    def get_image_path(self, index):
        # 根据索引获取对应的图片路径
        image_path = self.image_list.item(index).text()
        return image_path

    def add_dict_to_table(self, dict):
        # 遍历字典，把数据添加到表格中
        row = 0  # 行号
        for key, value in dict.items():
            # 创建两个单元格，分别存储键和值
            key_item = QTableWidgetItem(key)
            value_item = QTableWidgetItem(value)
            # 设置单元格的对齐方式，键右对齐，值左对齐
            key_item.setTextAlignment(Qt.AlignRight)
            value_item.setTextAlignment(Qt.AlignLeft)
            # 把单元格添加到表格中
            self.table.setItem(row, 0, key_item)
            self.table.setItem(row, 1, value_item)
            # 行号加一
            row += 1

    def bind_image_info(self, image_path):
        image_info = ParserA1111(image_path).read_image_info()
        self.edit1.setText("\n".join(image_info["description"]))
        self.edit2.setText("\n".join(image_info["negative"]))
        self.add_dict_to_table(image_info["steps"])
        # 启用排序功能
        self.table.setSortingEnabled(True)

    # 定义一个函数，用来显示图片
    def show_image(self, index):
        # 根据索引获取对应的图片路径，并加载显示
        image_path = self.get_image_path(index)
        pixmap = QPixmap(image_path)
        self.scale_pixmap(pixmap)
        self.bind_image_info(image_path)
        # 在文本框中，显示图片的文本信息，可以用ParserA1111类的read_image_info方法获取
        image_info = ParserA1111(image_path).read_image_info()["raw"]
        self.edit4.setText(image_info)

    # 定义槽函数，用来显示上一张图片
    def prev_image(self):
        # 如果当前索引大于0，就减1
        if self.current_index > 0:
            self.current_index -= 1

        self.show_image(self.current_index)

    # 定义槽函数，用来显示下一张图片
    def next_image(self):
        # 如果当前索引小于图片列表的长度减1，就加1
        if self.current_index < self.image_list.count() - 1:
            self.current_index += 1

        self.show_image(self.current_index)


def get_image_paths(input_path: Path):
    if input_path is None:
        # msg = QMessageBox()
        # msg.setIcon(QMessageBox.Warning)
        # msg.setText("No path provided.")
        # msg.setWindowTitle("Error")
        # msg.setWindowFlags(Qt.WindowStaysOnTopHint)
        # msg.exec()
        sys.exit(0)
    if input_path.is_file():
        return [input_path]
    elif input_path.is_dir():
        files = [
            f for f in input_path.glob("*.*") if f.suffix in (".jpg", ".png", ".bmp")
        ]
        return files
    else:
        print("Invalid input path")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "path",
        help="the path to an image or a folder of images",
        nargs="?",
        type=Path,
    )
    args = parser.parse_args()
    app = QApplication([])
    apply_stylesheet(app, theme="dark_teal.xml")
    images = get_image_paths(args.path)
    window = MyWindow(images)
    window.show()
    app.exec()
