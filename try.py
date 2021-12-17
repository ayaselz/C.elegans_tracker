import sys
import os
import re
from PySide6 import QtCore, QtWidgets, QtGui
from main import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import *


class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        qfile = QFile('ui.ui')
        qfile.open(QFile.ReadOnly)
        qfile.close()
        self.cwd = os.getcwd()  # 获取当前程序文件位置
        # 从UI定义中动态创建一个相应的窗口对象
        self.ui = QUiLoader().load(qfile)

        # self.ui = gui.Ui_Form()  # 实例化UI对象
        # self.ui.setupUi(self)  # 初始化

        self.model = Model()

        self.image_name = ''
        self.image_path = ''

        self.image_num = 0
        self.image_8bit = None
        self.image_16bit = None

        self.flip = False

        self.parameter_dict = {'alpha': 3, 'beta': 0,
                               'peak_circle': 6, 'peak_ratio': 0.4,
                               'bias_row': 0, 'bias_column': 0,
                               'label_radius': 7,
                               'right_black': 0, 'right_circle': 5, 'right_ratio': 0.6,
                               'left_black': 0, 'left_circle': 5, 'left_ratio': 0.6,
                               }
        self.right_result = []
        self.left_result = []


        # 信号处理
        self.ui.button_select_file.clicked.connect(self.button_select_file)
        self.ui.button_next.clicked.connect(self.button_next)
        self.ui.button_last.clicked.connect(self.button_last)
        self.ui.button_go.clicked.connect(self.button_go)

        self.ui.checkbox_mirror_symmetry.stateChanged.connect(self.checkbox_mirror_symmetry)

        self.ui.text_file_path.setText(self.image_path)

    def cv2QPix(self, img):
        # cv 图片转换成 qt图片
        qt_img = QtGui.QImage(img.data,  # 数据源
                              img.shape[1],  # 宽度
                              img.shape[0],  # 高度
                              img.shape[1],  # 行字节数
                              QtGui.QImage.Format_Grayscale8)
        return QtGui.QPixmap.fromImage(qt_img)

    def button_select_file(self):
        image_path_name, _ = QFileDialog.getOpenFileName(self, 'Select image', '', 'Image files(*.tif)')
        print(image_path_name)
        self.image_path, self.image_name = os.path.split(image_path_name)
        print(self.image_path, self.image_name)
        self.ui.text_file_path.setText(self.image_path)

        if self.image_path == '':
            self.image_path = QFileDialog.getExistingDirectory(self, 'Select image')
            self.ui.text_file_path.setText(self.image_path)
            print(self.image_path)
            print('\nCancel')

        regex = re.compile(r'\d+')
        if bool(re.search(r'\d', self.image_name)):
            self.image_num = int(max(regex.findall(self.image_name)))
            print(self.image_num)
        self.open_image(self.image_num)

    def open_image(self, num):
        if self.image_path != '':
            image_path_n = self.image_path + '/' + f'{num:04}' + '.tif'
            self.image_16bit, self.image_8bit = self.model.transfer_16bit_to_8bit(image_path_n)

            if self.flip:
                self.image_8bit = self.model.flip_y(self.image_8bit)
                self.image_16bit = self.model.flip_y(self.image_16bit)

            image_bright = self.model.image_bright(self.image_8bit, alpha=3, beta=0)
            self.ui.label_image.setPixmap(self.cv2QPix(image_bright))
            self.ui.text_num.setText(str(self.image_num))

    def button_next(self):
        self.image_num += 1
        self.open_image(self.image_num)

    def button_last(self):
        self.image_num -= 1
        self.open_image(self.image_num)

    def button_go(self):
        self.image_num = int(self.ui.text_num.toPlainText())
        self.open_image(self.image_num)

    def checkbox_mirror_symmetry(self):
        self.flip = not self.flip
        self.open_image(self.image_num)


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    widget = MyWidget()
    # widget.show()
    widget.ui.show()
    sys.exit(app.exec())