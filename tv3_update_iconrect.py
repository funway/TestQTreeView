import logging, sys

from PySide6 import QtCore
from PySide6.QtWidgets import QApplication, QMainWindow, QTreeView, QLineEdit, QVBoxLayout, QWidget, \
    QStyledItemDelegate, QAbstractItemView, QVBoxLayout, QStyle
from PySide6.QtGui import QStandardItemModel, QStandardItem, QIcon

from mywidget import TaskInfoWidget

#############################
# Don't take this method!
#############################

class SearchProxyModel(QtCore.QSortFilterProxyModel):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.debug('Init a %s instance' % self.__class__.__name__)
        pass

    def __accept_index(self, idx:QtCore.QModelIndex) -> bool:
        if idx.isValid():
            text = idx.data(QtCore.Qt.ItemDataRole.DisplayRole)
            if self.filterRegularExpression().match(text).hasMatch():
                return True
            # 递归对子节点进行判断
            for row in range(idx.model().rowCount(idx)):
                if self.__accept_index(idx.model().index(row, 0, idx)):
                    return True
        return False

    def filterAcceptsRow(self, sourceRow:int, sourceParent:QtCore.QModelIndex):
        idx = self.sourceModel().index(sourceRow, 0, sourceParent)
        if self.__accept_index(idx):
            self.logger.debug('匹配: %s', self.sourceModel().data(idx, role=QtCore.Qt.ItemDataRole.DisplayRole))
            return True
        else:
            self.logger.debug('不匹配: %s', self.sourceModel().data(idx, role=QtCore.Qt.ItemDataRole.DisplayRole))
            return False
        
class TaskInfoItem(QStandardItem):
    """表示在 Model 中的每一个 item 项"""
    def __init__(self, title: str, description: str = '任务描述...', icon: QIcon = None):
        super(TaskInfoItem, self).__init__(title)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.debug('Init a %s instance. title[%s]', self.__class__.__name__, title)

        self.setEditable(False)
        
        self.widget = TaskInfoWidget(title, description, icon)
        self.setData(self.widget, role=QtCore.Qt.ItemDataRole.UserRole)
        pass

class TaskInfoDelegate(QStyledItemDelegate):
    """docstring for TaskInfoDelegate."""
    def __init__(self, parent=None):
        super(TaskInfoDelegate, self).__init__(parent)
        
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.debug('Init a %s instance' % self.__class__.__name__)
        pass

    def paint(self, painter, option, index):
        self.logger.debug('============ 开始绘制 ==============')

        # 1. 初始化 option （QStyleOptionViewItem 类型）
        self.initStyleOption(option, index)
        self.logger.debug('初始化后 option[text]: %s', option.text)
        self.logger.debug('初始化后 option[rect]: %s', option.rect)
        
        # 2. 判断是否是一级节点。如果是，则直接调用父类 paint 并返回
        if index.parent().isValid() == False:
            self.logger.debug('这是一级节点（任务组）')
            return super().paint(painter, option, index)
    
        # 3. 绘制二级节点
        self.logger.debug('这是二级节点（任务）')
        task_widget = index.data(role=QtCore.Qt.ItemDataRole.UserRole)
        task_widget.setGeometry(option.rect)
        icon_rect = QStyle.alignedRect(QtCore.Qt.LayoutDirection.LayoutDirectionAuto, 
                    option.displayAlignment, QtCore.QSize(32, 32), option.rect)
        
        # 不应该在 paint 里面 connect 信号-槽，这太耗 CPU 了！
        # 而且因为这里的槽函数是一个 lambda 函数，那么每次 connect 都会新建一个啊！！！又耗时，又费内存！
        # 不断的调用这个 connect 必然会导致内存暴涨！！！
        task_widget.movie.frameChanged.connect(lambda: option.widget.viewport().update(icon_rect), QtCore.Qt.ConnectionType.UniqueConnection)
        # task_widget.movie.frameChanged.connect(lambda: option.widget.viewport().update(icon_rect), QtCore.Qt.ConnectionType.SingleShotConnection)
        # if task_widget.first_paint:
        #     task_widget.movie.frameChanged.connect(lambda: option.widget.viewport().update(icon_rect), QtCore.Qt.ConnectionType.UniqueConnection)
        #     task_widget.first_paint = False

        painter.save()
        painter.translate(option.rect.topLeft())
        task_widget.render(painter, QtCore.QPoint(0, 0))
        painter.restore()
        pass

    def sizeHint(self, option, index):
        """绘制自定义 widget 时，需要重写 sizeHint 来返回自定义 widget 的大小，来占位。 """
        # 如果是一级节点，返回父类的 sizeHint
        if index.parent().isValid() == False:
            self.logger.debug('一级节点: %s', index.data())
            return super().sizeHint(option, index)
        
        # 如果是二级节点，返回自定义 widget 的 sizeHint
        self.logger.debug('二级节点: %s', index.data())
        task_widget = index.data(role=QtCore.Qt.ItemDataRole.UserRole)
        return task_widget.sizeHint()

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
        tk11 = TaskInfoItem('t_任务1')
        tk12 = TaskInfoItem('t_<span style="color:red;"><b>任务</b></span>task2')
        tk13 = TaskInfoItem('t_资料收集333')
        tk21 = TaskInfoItem('t_发送测试')
        tk22 = TaskInfoItem('t_collection 1')

        rootItem.appendRow(gp1)
        rootItem.appendRow(gp2)
        gp1.appendRow(tk11)
        gp1.appendRow(tk12)
        gp1.appendRow(tk13)
        gp2.appendRow(tk21)
        gp2.appendRow(tk22)

        # 定义 ProxyModel
        self.proxymodel = SearchProxyModel()
        self.proxymodel.setSourceModel(self.treemodel)
        self.proxymodel.setFilterCaseSensitivity(QtCore.Qt.CaseSensitivity.CaseInsensitive)

        # 给 QTreeView 设置数据
        self.treeview.setModel(self.proxymodel)

        # 给 QTreeView 设置自定义的 ItemDelegate
        delegate = TaskInfoDelegate()
        self.treeview.setItemDelegate(delegate)
        # 展开所有节点
        self.treeview.expandAll()

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

    def on_search_text_changed(self, text):
        self.logger.debug('search text changed: %s', text)
        self.proxymodel.setFilterRegularExpression(self.ui_search.text())
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
    logging.basicConfig(level=logging.INFO, format=log_format)
    main()
