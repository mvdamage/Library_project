import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem, QLabel, QLineEdit,
    QComboBox, QTextEdit, QDateEdit, QMessageBox, QTabWidget,
    QHeaderView, QSplitter, QFrame, QDialog, QDialogButtonBox,
    QFormLayout, QGroupBox, QGridLayout, QProgressBar
)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QColor

from database import Database

class BookDialog(QDialog):
    """Диалог для добавления/редактирования книги"""
    
    def __init__(self, parent=None, book_data=None):
        super().__init__(parent)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.book_data = book_data
        self.setWindowTitle("Новая книга" if book_data is None else "Редактирование книги")
        self.setModal(True)
        self.setMinimumWidth(700)
        self.init_ui()
        
        if book_data:
            self.load_book_data()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Форма для ввода данных
        form_layout = QFormLayout()
        
        # Название книги
        self.title_edit = QLineEdit()
        self.title_edit.setMaximumHeight(100)
        self.title_edit.setPlaceholderText("Введите название книги")
        form_layout.addRow("Название:", self.title_edit)

        # Том книги
        self.volume_edit = QLineEdit()
        self.volume_edit.setMaximumHeight(100)
        self.volume_edit.setPlaceholderText("Введите том книги")
        form_layout.addRow("Том: (при наличии)", self.volume_edit)

        # Автор
        self.author_edit = QTextEdit()
        self.author_edit.setMaximumHeight(100)
        self.author_edit.setPlaceholderText("Введите автора книги")
        form_layout.addRow("Автор:", self.author_edit)

        # Год
        self.year_edit = QTextEdit()
        self.year_edit.setMaximumHeight(50)
        self.year_edit.setPlaceholderText("Введите год издания книги")
        form_layout.addRow("Год издания:", self.year_edit)

        # Жанр
        self.genre_edit = QTextEdit()
        self.genre_edit.setMaximumHeight(100)
        self.genre_edit.setPlaceholderText("Введите жанр книги")
        form_layout.addRow("Жанр:", self.genre_edit)
                        
        layout.addLayout(form_layout)
        
        # Кнопки
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self
        )
        buttons.button(QDialogButtonBox.Cancel).setText("Отменить")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        ok_text = "Сохранить" if self.book_data else "Добавить"
        buttons.button(QDialogButtonBox.Ok).setText(ok_text)
    
    def load_book_data(self):
        """Загрузка данных книги для редактирования"""
    #    self.book_data: (id, title, author, year, genre)
    #    self.title_edit.setText(self.book_data[1])
        # self.desc_edit.setText(self.book_data[2] if self.task_data[2] else "")
        self.title_edit.setText(self.book_data[1] or "")
        self.volume_edit.setText(self.book_data[2] or "")
        self.author_edit.setPlainText(self.book_data[3] or "")
        self.year_edit.setPlainText("" if self.book_data[4] is None else str(self.book_data[4]))
        self.genre_edit.setPlainText(self.book_data[5] or "")
        
    def get_book_data(self):
        """Получение данных из формы"""
        return {
            'title': self.title_edit.text().strip(),
            'volume': self.volume_edit.text().strip(),
            'author': self.author_edit.toPlainText().strip(),
            'year': self.year_edit.toPlainText().strip(),
            'genre': self.genre_edit.toPlainText().strip(),
        }

class Library(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = Database()
     #   self.current_filter = "Все"
        self.init_ui()
        self.load_books()
    
    def init_ui(self):
        self.setWindowTitle("Домашняя библиотека")
        self.setGeometry(100, 100, 1600, 1100)
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Основной layout
        main_layout = QVBoxLayout(central_widget)
        
        # Верхняя панель с кнопками
        self.create_toolbar(main_layout)
               
        # Таблица задач
        self.create_book_table(main_layout)
        
        # Нижняя панель
        self.create_status_bar()
        
        # Применение стилей
        self.apply_styles()
    
    def create_toolbar(self, parent_layout):
        """Создание верхней панели инструментов"""
        toolbar = QHBoxLayout()
        
        # Кнопка добавления
        self.add_btn = QPushButton("➕ Новая книга")
        self.add_btn.setMinimumHeight(40)
        self.add_btn.clicked.connect(self.add_book)
        toolbar.addWidget(self.add_btn)
        
        # Кнопка редактирования
        self.edit_btn = QPushButton("✏️ Редактировать")
        self.edit_btn.setMinimumHeight(40)
        self.edit_btn.clicked.connect(self.edit_book)
        toolbar.addWidget(self.edit_btn)
        
        # Кнопка удаления
        self.delete_btn = QPushButton("🗑️ Удалить книгу")
        self.delete_btn.setMinimumHeight(40)
        self.delete_btn.clicked.connect(self.delete_book)
        toolbar.addWidget(self.delete_btn)
        
        toolbar.addStretch()
                
        # Поиск
        toolbar.addWidget(QLabel("Поиск:"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Введите текст для поиска...")
        self.search_edit.setMinimumWidth(600)
        self.search_edit.setMaximumWidth(600)
        self.search_edit.textChanged.connect(self.on_search_changed)
        toolbar.addWidget(self.search_edit)
        
        parent_layout.addLayout(toolbar)
    
    def create_book_table(self, parent_layout):
        """Создание таблицы книг"""
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "N", "Название", "Том", "Автор", "Год издания", "Жанр"
        ])
        
        # Настройка таблицы
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setAlternatingRowColors(True)
        
        # Двойной клик для редактирования
        self.table.doubleClicked.connect(self.edit_book)
        
        parent_layout.addWidget(self.table)
    
    def create_status_bar(self):
        """Создание строки состояния"""
        self.status_label = QLabel("Готов к работе")
        self.statusBar().addWidget(self.status_label)
    
    def apply_styles(self):
        """Применение стилей к приложению"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
            QTableWidget {
                background-color: white;
                alternate-background-color: #f9f9f9;
                selection-background-color: #BBDEFB;
                gridline-color: #E0E0E0;
            }
            QHeaderView::section {
                background-color: #2196F3;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
            QComboBox, QLineEdit, QDateEdit {
                padding: 5px;
                border: 1px solid #BDBDBD;
                border-radius: 4px;
                min-height: 20px;
            }
            QComboBox:focus, QLineEdit:focus, QDateEdit:focus {
                border: 2px solid #2196F3;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #BDBDBD;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
    
    def load_books(self):
        """Загрузка книг в таблицу"""
        if hasattr(self, 'search_edit') and self.search_edit.text():
            books = self.db.search_book(self.search_edit.text())
        else:
            books = self.db.get_all_books()
        
        self.table.setRowCount(len(books))
        
        for row, book in enumerate(books):
            for col, value in enumerate(book):
                item = QTableWidgetItem(str(value) if value else "")
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(row, col, item)
        
    def add_book(self):
        """Добавление новой книги"""
        dialog = BookDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_book_data()
            if data['title']:
                self.db.add_book(
                    data['title'],
                    data['volume'],
                    data['author'],
                    data['year'],
                    data['genre']
                )
                self.load_books()
               # self.update_statistics()
                self.status_label.setText(f"Книга '{data['title']}' добавлена")
            else:
                QMessageBox.warning(self, "Ошибка", "Название книги не может быть пустым")
    
    def edit_book(self):
        """Редактирование выбранной книги"""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.information(self, "Информация", "Выберите книгу для редактирования")
            return
        
        book_id = int(self.table.item(current_row, 0).text())
        
        # Получаем полные данные задачи из БД
        library = self.db.get_all_books()
        book_data = next((t for t in library if t[0] == book_id), None)
        
        if book_data:
            dialog = BookDialog(self, book_data)
            if dialog.exec_() == QDialog.Accepted:
                data = dialog.get_book_data()
                if data['title']:
                    self.db.update_book(
                        book_id,
                        data['title'],
                        data['volume'],
                        data['author'],
                        data['year'],
                        data['genre']
                    )
                    self.load_books()
                    self.status_label.setText(f"Книга обновлена")
                else:
                    QMessageBox.warning(self, "Ошибка", "Название книги не может быть пустым")
    
    def delete_book(self):
        """Удаление книги"""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.information(self, "Информация", "Выберите книгу для удаления")
            return
        
        book_id = int(self.table.item(current_row, 0).text())
        book_title = self.table.item(current_row, 1).text()

        box = QMessageBox(self)
        box.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        box.setWindowTitle("Подтверждение")
        box.setText(f"Удалить книгу '{book_title}'?")
        box.setIcon(QMessageBox.Question)
        box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        box.button(QMessageBox.Yes).setText("Да")
        box.button(QMessageBox.No).setText("Нет")
        box.setDefaultButton(QMessageBox.No)

        if box.exec_() == QMessageBox.Yes:
            if self.db.delete_book(book_id):
                self.load_books()
                self.status_label.setText(f"Книга '{book_title}' удалена")
    
    def on_search_changed(self, search_text):
        """Обработка поиска"""
        self.load_books()
    
    def closeEvent(self, event):
        """Обработка закрытия приложения"""
        self.db.close()
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Современный стиль
    
    # Установка шрифта по умолчанию
    font = QFont("Inter", 12)
    app.setFont(font)
    
    window = Library()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()