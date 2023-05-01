# Tests how to show GIF images running in QTreeView

## Final solution
1. Use `customWidget.setParent(treeView.viewport())` binds all custom widgets to the treeview as child widgets.
2. In `itemdelegate.paint()`, call `customWidget.show()` to make the widget visible.
3. Keep all visible widgets in a list `visibleWdigets`. They are all customWidgets in the treeView's visible area.
4. On the event of `treeView.collapsed()`, `QSortFilterProxyModel.filterAcceptsRow()`, `treeView.verticalScrollBar().valueChanged()`, make sure call `customWidget.hide()` to the no longer visible widgets in the `visibleWdigets` list.
5. Share one global QMovie instance with all customwidgets, lower the cpu usage.