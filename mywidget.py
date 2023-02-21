import logging, sys, os, random

from PySide6 import QtCore
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, \
    QLabel, QVBoxLayout, QHBoxLayout
from PySide6.QtGui import QIcon, QMovie, QFont

class MyLabel(QLabel):
    """docstring for MyLabel."""
    def __init__(self, arg):
        super(MyLabel, self).__init__(arg)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.debug('Init a %s instance' % self.__class__.__name__)

    def paintEvent(self, event):
        self.logger.debug('my label [%s] paintevent: %s', self.text(), event.rect())
        self.logger.debug("label's top window: %s", self.window())
        
        # 调用父类方法进行绘制
        super().paintEvent(event)
        pass
    

class TaskInfoWidget(QWidget):
    """自定义 Widget。包含 icon，title， description 三个部分"""
    def __init__(self, title: str, description: str = '任务描述...', icon: QIcon = None, parent: QWidget = None):
        super(TaskInfoWidget, self).__init__(parent)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.debug('Init a %s instance' % self.__class__.__name__)

        self.first_paint = True

        # 1. 图标
        self.label_icon = QLabel(self)
        self.label_icon.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_icon.setFixedWidth(40)
        
        # 1.1 QLabel 加载图片
        ## 使用 QIcon 来获得缩放后的 QPixmap
        # self.label_icon.setPixmap(QIcon(os.path.dirname(__file__) + "/dog.png").pixmap(32, 32))
        
        ### 注意！不要像下面这样直接使用 QPixmap.scaled() 来缩放图标，scaled 方法的效果并不理想！（好像）
        ## p = QtGui.QPixmap(os.path.dirname(__file__) + "/dog.png")
        ## self.label_icon.setPixmap(p.scaled(32, 32, transformMode=QtCore.Qt.TransformationMode.SmoothTransformation))
        
        # 1.2 QLabel 加载 gif
        self.movie = QMovie(os.path.dirname(__file__) + "/loading.gif")
        self.movie.setScaledSize(QtCore.QSize(32, 32))
        self.movie.setCacheMode(QMovie.CacheMode.CacheAll)
        self.label_icon.setMovie(self.movie)
        self.movie.start()

        # 2. title
        self.label_title = MyLabel(self)
        font = QFont()
        font.setPointSize(24)
        self.label_title.setFont(font)
        self.label_title.setText(title)

        # 3. description
        self.label_description = QLabel(self)
        self.label_description.setText(description)  # QLabel.setText() 是支持富文本的
        
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.addWidget(self.label_title)
        self.verticalLayout.addWidget(self.label_description)

        self.horizontalLayout = QHBoxLayout(self)
        self.horizontalLayout.addWidget(self.label_icon)
        self.horizontalLayout.addLayout(self.verticalLayout)

        self.label_icon.setStyleSheet('background-color: #{:06x}'.format(random.randint(0, 0xFFFFFF)))
        self.label_title.setStyleSheet('background-color: #{:06x}'.format(random.randint(0, 0xFFFFFF)))
        self.label_description.setStyleSheet('background-color: #{:06x}'.format(random.randint(0, 0xFFFFFF)))
        
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        
        pass
    
    def paintEvent(self, event):
        """所有 QWidget 绘制的时候，都是调用 paintEvent() 方法进行绘制。

        如果继承自某个内建 widget（比如 QLabel, QPushButton 这些），那么重写该方法将会覆盖父类的绘制行为。
        
        此外！！！如果该 widget 还有 child widgets 的话，在执行完自己的 paintEvent() 之后，
        还会接着自动调用所有 child widgets 的 paintEvent()！
        （其实并不是所有，只需要调用与该 event.rect() 有交集的 child widgets 的 paintEvent() 方法。）

        对于 TaskInfoWidget，我们不需要在此手工绘制什么，只需由其 child widgets 自行绘制即可。
        Args:
            event (_type_): _description_
        """
        self.logger.debug('paint event: %s', event.rect())
        pass

def test_show_TaskInfoWidget():
    app = QApplication(sys.argv)

    main_window = QMainWindow()
    main_window.setWindowTitle('TaskInfoWidget Test')
    main_window.setCentralWidget(TaskInfoWidget('任务标题', '任务详情描述...'))
    main_window.show()
    sys.exit(app.exec())
    pass


if __name__ == '__main__':
    log_format = '%(asctime)s pid[%(process)d] %(levelname)7s %(name)s.%(funcName)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_format)
    test_show_TaskInfoWidget()