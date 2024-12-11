from PyQt5.QtWidgets import QMainWindow, QDialog, QMessageBox, QTableWidgetItem, QPushButton
from PyQt5.QtCore import Qt, QDate, QTime
from PyQt5.QtGui import QColor, QFont


from MainFrameUI import Ui_MainWindow
from AddEventUI import UI_AddEvent
from CalendarUI import UI_Calendar
import EventsDBControl

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):  # Corrected __init__
        super().__init__()
        self.setupUi(self)
        self.calendarBtn.clicked.connect(self.open_calendar)
        self.addEventBtn.clicked.connect(self.open_add_event_dialog)
        self.calendarWindow = None
        self.db = EventsDBControl.EventDatabase()
        self.populate_event_tables()
        self.set_column_widths(self.activeEventsTable)
        self.set_column_widths(self.inactiveEventsTable)
    def populate_event_tables(self):
        self.populate_table(self.activeEventsTable, 1)
        self.populate_table(self.inactiveEventsTable, 0)

    def set_column_widths(self, table):
        table.setColumnWidth(0, 200)
        table.setColumnWidth(1, 150)
        table.setColumnWidth(2, 100)
        table.setColumnWidth(3, 100)
        table.setColumnWidth(4, 200) # Ширина колонки с кнопкой


    def populate_table(self, table, is_active):
        table.clearContents()
        table.setRowCount(0)
        table.setColumnCount(5)  # Добавлено для кнопки "Изменить"
        events = self.db.get_events_by_status(is_active)

        if events:
            for event in events:
                row_position = table.rowCount()
                table.insertRow(row_position)

                name_item = QTableWidgetItem(event[1])
                name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
                table.setItem(row_position, 0, name_item)

                table.setItem(row_position, 1, QTableWidgetItem(event[2]))
                table.setItem(row_position, 2, QTableWidgetItem(event[3]))
                table.setItem(row_position, 3, QTableWidgetItem(event[4]))

                table.item(row_position, 1).setFlags(table.item(row_position, 1).flags() & ~Qt.ItemIsEditable)
                table.item(row_position, 2).setFlags(table.item(row_position, 2).flags() & ~Qt.ItemIsEditable)
                table.item(row_position, 3).setFlags(table.item(row_position, 3).flags() & ~Qt.ItemIsEditable)

                # Add a button to each row - using functools.partial
                import functools
                edit_button = QPushButton("Изменить")
                edit_button.setStyleSheet("""
                        QPushButton {
                            background-color: white;
                            border-radius: 20%;
                        }
                        QPushButton:hover' {
                            background-color: #f0f0f0;
                        }
                        QPushButton:pressed {
                            background-color: #e0e0e0;
                        }""")
                edit_button.clicked.connect(functools.partial(self.open_edit_dialog, event[0], table, row_position))
                table.setCellWidget(row_position, 4, edit_button)

        else:
            row_position = table.rowCount()
            table.insertRow(row_position)
            table.setItem(row_position, 0, QTableWidgetItem("Мероприятий этого типа нет"))
            # Disable other columns for better visual clarity
            for i in range(1, 5):
                table.setItem(row_position, i, QTableWidgetItem(""))
            table.setSpan(row_position, 0, 1, 5)  # Span message across all columns


    def open_edit_dialog(self, event_id, table, row):
        event = self.db.get_event_by_id(event_id)
        if event:
            dialog = AddEventDialog(self, event)  # Pass event data to the dialog
            if dialog.exec_() == QDialog.Accepted:
                self.populate_event_tables()

    def open_add_event_dialog(self):
        dialog = AddEventDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.populate_event_tables()

    def open_calendar(self):
        if self.calendarWindow is None:
            self.calendarWindow = Calendar(self)
        self.calendarWindow.show()
        self.hide()

    def closeEvent(self, event):
        self.db.close()
        super().closeEvent(event)

class Calendar(QMainWindow, UI_Calendar):
    def __init__(self, main_window):
        super().__init__()
        self.setupUi(self)  # Load the UI file
        self.main_window = main_window
        self.eventsBtn.clicked.connect(self.return_to_main)
        self.showEventButton.hide()
        self.NoEventsLabel.hide()
        self.db = EventsDBControl.EventDatabase()
        self.highlight_today()

        # VERY IMPORTANT: Connect the signal!
        self.calendarWidget.clicked.connect(self.update_chosen_date)

    def closeEvent(self, event):
        self.db.close()  # Close the database connection when the window is closed
        event.accept()
    def highlight_today(self):
        today = QDate.currentDate()
        format = self.calendarWidget.dateTextFormat(today)  # Get current format
        format.setForeground(QColor("#000000"))  # Set text color
        format.setFont(QFont("Roboto", 9, QFont.Bold))  # Set font
        self.calendarWidget.setDateTextFormat(today, format)
        today_str = today.toString("dd-MM-yyyy")
        self.update_chosen_date()
        self.check_events_for_date(today_str)

    def update_chosen_date(self):
        selected_date = self.calendarWidget.selectedDate()
        formatted_date = selected_date.toString("dd-MM-yyyy")
        self.ChosenDate.setText(formatted_date)
        self.check_events_for_date(formatted_date)

    def check_events_for_date(self, selected_date):
        count = self.db.count_events_by_date(selected_date)
        if count > 0:
            self.showEventButton.setText(f"Показать {count} мер.")
            self.showEventButton.show()
            self.NoEventsLabel.setText("Я пока не работаю \nС любовью, кнопка")
            self.NoEventsLabel.show()
        else:
            self.NoEventsLabel.setText("На текущую дату мероприятий нет")
            self.NoEventsLabel.show()
            self.showEventButton.hide()

    def return_to_main(self):
        self.main_window.show()
        self.hide()

class AddEventDialog(QDialog, UI_AddEvent):
    def __init__(self, parent=None, event=None): #Accept event data
        super().__init__(parent)
        self.setupUi(self)
        self.db = EventsDBControl.EventDatabase()
        self.saveEventDataBtn.clicked.connect(self.save_event)
        self.deleteEventDataBtn.clicked.connect(self.delete_event)
        self.event_id = None #to track existing event ID
        if event:
            self.headerLabelText.setText("Изменить мероприятие")
            self.deleteEventDataBtn.show()
        else:
            self.headerLabelText.setText("Добавить мероприятие")
            self.deleteEventDataBtn.hide()

        if event: #Populate fields if event is passed
            self.event_id = event[0]
            self.eventName.setText(event[1])
            self.eventDate.setDate(QDate.fromString(event[2], "dd-MM-yyyy"))
            self.eventTime.setTime(QTime.fromString(event[3], "HH:mm"))
            self.eventBudget.setText(event[4])
            is_active = event[5] == 1
            self.radioBtnIsActive.setChecked(is_active)
            self.radioBtnIsPlanned.setChecked(not is_active)

    def save_event(self):
        event_name = self.eventName.text()
        event_date = self.eventDate.date().toString("dd-MM-yyyy")
        event_time = self.eventTime.time().toString("HH:mm")
        event_budget = self.eventBudget.text()
        event_is_active = 1 if self.radioBtnIsActive.isChecked() else 0

        if not event_name:
            QMessageBox.warning(self, "Ошибка", "Поле 'Название' не может быть пустым.")
            return

        try:
            event_budget = float(event_budget)
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Неверный формат бюджета.")
            return
        if self.event_id:
            self.db.update_event(self.event_id, event_name, event_date, event_time, event_budget, event_is_active)
        else:
            self.db.add_event(event_name, event_date, event_time, event_budget, event_is_active)

        self.accept()

    def delete_event(self):
        if QMessageBox.question(self, "Подтверждение удаления",
                                "Вы действительно хотите удалить это мероприятие?",
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.db.delete_event(self.event_id)
            self.accept()  # Закрываем диалог после успешного удаления