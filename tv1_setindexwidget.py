import logging, sys

from PySide6 import QtCore
from PySide6.QtWidgets import QApplication, QMainWindow, QTreeView, QLineEdit, QVBoxLayout, QWidget, \
    QAbstractItemView, QVBoxLayout
from PySide6.QtGui import QStandardItemModel, QStandardItem

from mywidget import TaskInfoWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.debug('Init a %s instance' % self.__class__.__name__)

        self.treeview = QTreeView()
        self.treeview.setHeaderHidden(True)
        self.treeview.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        
        # 定义数据
        self.treemodel = QStandardItemModel()
        # 根节点
        rootItem = self.treemodel.invisibleRootItem()
        # 一级节点
        gp1 = QStandardItem('TG_Default')
        gp2 = QStandardItem('TG_Test')
        # 二级节点
        tk11 = QStandardItem('t_任务1')
        tk12 = QStandardItem('t_<span style="color:red;"><b>任务</b></span>task2')
        tk13 = QStandardItem('t_资料收集333')
        tk21 = QStandardItem('t_发送测试')
        tk22 = QStandardItem('t_collection 1')

        rootItem.appendRow(gp1)
        rootItem.appendRow(gp2)
        self.logger.info('tk11 index（未加入 itemmodel 前）: %s', tk11.index())
        gp1.appendRow(tk11)
        self.logger.info('tk11 index（加入 itemmodel 后）: %s', tk11.index())
        gp1.appendRow(tk12)
        gp1.appendRow(tk13)
        gp2.appendRow(tk21)
        gp2.appendRow(tk22)

        # 给 QTreeView 设置数据
        self.treeview.setModel(self.treemodel)
        self.treeview.setIndexWidget(tk11.index(), TaskInfoWidget(tk11.text()))
        self.treeview.setIndexWidget(tk12.index(), TaskInfoWidget(tk12.text()))
        self.treeview.setIndexWidget(tk13.index(), TaskInfoWidget(tk13.text()))
        self.treeview.setIndexWidget(tk21.index(), TaskInfoWidget(tk21.text()))
        self.treeview.setIndexWidget(tk22.index(), TaskInfoWidget(tk22.text()))

        # 展开所有节点
        self.treeview.expandAll()
        # 连接 信号-槽函数
        self.treeview.doubleClicked.connect(self.on_doubleclicked)

        # 搜索栏
        self.ui_search = QLineEdit()
        self.ui_search.setPlaceholderText('Search...')
        self.ui_search.textChanged.connect(self.on_search_text_changed)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.ui_search)
        main_layout.addWidget(self.treeview)
        widget = QWidget()
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)

    def on_doubleclicked(self, index:QtCore.QModelIndex):
        """槽函数，响应 QTreeView 的 doubleClicked() 信号，
        该信号会向槽函数传递 QModelIndex 对象，代表被双击的节点

        Args:
            index (QtCore.QModelIndex): 被双击的节点
        """
        self.logger.debug('double clicked on [%s, %s]', index.row(), index.column())
        self.logger.debug('data(Default): %s', index.data())
        self.logger.debug('data(UserRole): %s', index.data(role=QtCore.Qt.ItemDataRole.UserRole))

    def on_search_text_changed(self, text):
        self.logger.debug('search text changed: %s', text)
        # 执行 fitler 操作 ...
        self.treeview.expandAll()
        pass

def main():
    logging.info('Start main process')
    # 生成QApplication主程序
    app = QApplication(sys.argv)

    # 生成窗口类实例
    main_window = MainWindow()
    # 设置窗口标题
    main_window.setWindowTitle('QTreeView Test')
    # 设置窗口大小
    main_window.resize(400, 500)
    # 显示窗口
    main_window.show()

    # 进入QApplication的事件循环
    sys.exit(app.exec())
    
    pass


if __name__ == '__main__':
    log_format = '%(asctime)s pid[%(process)d] %(levelname)7s %(name)s.%(funcName)s - %(message)s'
    logging.basicConfig(level=logging.DEBUG, format=log_format)
    main()