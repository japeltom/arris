from PySide6.QtWidgets import QDialog

from ui.ui_tag_adder import Ui_Dialog

class TagAdder(QDialog,Ui_Dialog):

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)

        self.setWindowTitle("Add tags")
        self.setModal(True) # Block input to other windows.

        # This is the list of all tags to be added.
        self.all_items = []
        self.source_list.addItems(self.all_items)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.filter_lineEdit.textChanged.connect(self.filter_items)
        self.to_source_button.clicked.connect(self.move_to_source)
        self.to_target_button.clicked.connect(self.move_to_target)

    def move_to_target(self):
        for item in self.source_list.selectedItems():
            self.target_list.addItem(item.text())
            self.source_list.takeItem(self.source_list.row(item))
            self.all_items.remove(item.text())

    def move_to_source(self):
        for item in self.target_list.selectedItems():
            self.source_list.addItem(item.text())
            self.target_list.takeItem(self.target_list.row(item))
            self.all_items.append(item.text())

    def filter_items(self, text):
        self.source_list.clear()
        for item in self.all_items:
            if text.lower() in item.lower():
                self.source_list.addItem(item)

    def set_selected_tags(self, tags):
        for tag in tags:
            self.target_list.addItem(tag.lower())

    def get_selected_tags(self):
        result = []
        for i in range(self.target_list.count()):
            item = self.target_list.item(i)
            result.append(item.text().lower())

        return result


