import logging, sys

from PySide6 import QtCore
from PySide6.QtWidgets import QApplication, QMainWindow, QTreeView, QLineEdit, QVBoxLayout, QWidget, \
    QStyledItemDelegate, QAbstractItemView, QVBoxLayout
from PySide6.QtGui import QStandardItemModel, QStandardItem, QIcon

from mywidget import TaskInfoWidget

class SearchProxyModel(QtCore.QSortFilterProxyModel):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.debug('Init a %s instance' % self.__class__.__name__)
        pass

    def __accept_index(self, idx:QtCore.QModelIndex) -> bool:
        """判断 idx 节点（包括子节点）是否匹配 self.filterRegularExpression。节点（包括子节点）只要有一个能匹配到，就返回 True。

        Args:
            idx (QtCore.QModelIndex): 节点的 QModelIndex 对象

        Returns:
            bool: 匹配返回 True，否则返回 False
        """

        if idx.isValid():
            text = idx.data(QtCore.Qt.ItemDataRole.DisplayRole)
            tw = idx.data(role=QtCore.Qt.ItemDataRole.UserRole)
            if self.filterRegularExpression().match(text).hasMatch():
                if tw is not None:
                    tw.setVisible(True)
                return True
            else:
                if tw is not None:
                    tw.setVisible(False)

            # 递归对子节点进行判断
            for row in range(idx.model().rowCount(idx)):
                if self.__accept_index(idx.model().index(row, 0, idx)):
                    return True
        return False

    def filterAcceptsRow(self, sourceRow:int, sourceParent:QtCore.QModelIndex):
        """重写父类方法，判断节点是否满足过滤条件。
        节点可以通过 sourceParent[sourceRow] 定位
        过滤条件可以从 QSortFilterProxyModel.filterRegularExpression 属性获取
        
        ！！注意！！：
        对于多级数据模型，filter 会自动递归地对所有节点调用 filterAcceptsRow。先对一级节点调用该方法，然后再二级节点，再三级节点这样。
        但是如果某个父节点返回的是 False，那么它的子节点将不会再被递归！！

        Args:
            sourceRow (int): 节点的在父节点的第几行
            sourceParent (QtCore.QModelIndex): 父节点

        Returns:
            _type_: 满足过滤条件返回 True，否则返回 False
        """
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
        # TaskInfoWidget 必须先初始化。如果像下面这样调用 TaskInfoWidget，实际上是不会初始化 widget 实例的。🤷‍♂️
        # self.setData(TaskInfoWidget(title, description, icon), role=QtCore.Qt.ItemDataRole.UserRole)
        pass

class TaskInfoDelegate(QStyledItemDelegate):
    """docstring for TaskInfoDelegate."""
    def __init__(self, parent=None):
        super(TaskInfoDelegate, self).__init__(parent)
        
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.debug('Init a %s instance' % self.__class__.__name__)
        pass

    def paint(self, painter, option, index):
        """如果重写 paint 方法，派生类就需要自己负责绘制所有内容，包括 文字、图标、背景色 等等。

        Args:
            painter (QtGui.QPainter): 画笔（建议在绘制前 painter.save 保存画笔状态，绘制后 painter.restore 恢复画笔状态）
            option (QtWidgets.QStyleOptionViewItem): 需要通过 initStyleOption() 方法初始化
            index (QtCore.QModelIndex): 待绘制 item 的 ModelIndex
        """

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
        # 由于设置了 task_widget 的父 widget 是 treeview。
        # 所以必须设置 task_widget 相对于其父 widget 的位置与矩形。由 tlw > parent widget > child widget 这样的绘制链自动绘制。
        # 因此，我们也就不需要在此主动调用 task_widget.render() 进行手工绘制了。
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

        tk11.widget.setParent(self.treeview.viewport())
        tk12.widget.setParent(self.treeview.viewport())
        tk13.widget.setParent(self.treeview.viewport())
        tk21.widget.setParent(self.treeview.viewport())
        tk22.widget.setParent(self.treeview.viewport())

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
