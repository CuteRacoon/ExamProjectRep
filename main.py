import sys


from PyQt5.QtWidgets import QApplication


import UIinteraction

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = UIinteraction.MainWindow()
    window.show()  # Отображаем окно приложения
    sys.exit(app.exec_())  # Запуск основного цикла приложения