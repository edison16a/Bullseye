import sys
import threading
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QSlider, QCheckBox, QPushButton, 
                             QFrame, QStackedWidget, QSpacerItem, QSizePolicy, QComboBox)
from PyQt5.QtCore import Qt, QSize, QRect, QTimer, QEvent
from PyQt5.QtGui import QPixmap, QIcon, QColor, QPainter, QPen
import os
import requests

class SettingsMenu(QMainWindow):
    def __init__(self):
        super().__init__(None, Qt.FramelessWindowHint)
        self.setWindowTitle("RATSN")
        self.setStyleSheet("""
            QMainWindow { background-color: #101010; }
            QLabel { color: #ffffff; font-family: 'Consolas'; font-size: 14px; }
            QLabel#logo { color: #ff8c00; font-family: 'Consolas'; font-size: 24px; font-weight: bold; padding: 10px; }
            QPushButton[class="sidebarButton"] { background-color: #101010; color: #ffffff; font-family: 'Consolas'; font-size: 16px; padding: 10px; text-align: left; border: 2px solid transparent; border-radius: 5px; }
            QPushButton[class="sidebarButton"]:hover { background-color: #333333; border-radius: 5px; }
            QPushButton[class="sidebarButton"][selected="true"] { color: #ff8c00; border: 2px solid #ff8c00; border-radius: 5px; }
            QCheckBox { color: #ffffff; font-family: 'Consolas'; font-size: 14px; spacing: 8px; outline: none; }
            QCheckBox::indicator { width: 16px; height: 16px; }
            QCheckBox::indicator:unchecked { background-color: transparent; border: 2px solid #ff8c00; border-radius: 3px; }
            QCheckBox::indicator:checked { background-color: #ff8c00; border: 2px solid #ff8c00; border-radius: 3px; }
            QCheckBox:focus { outline: none; }
            QSlider { outline: none; }
            QSlider::groove:horizontal { background: #1e1e1e; height: 4px; border-radius: 2px; }
            QSlider::handle:horizontal { background: #ff8c00; width: 12px; height: 12px; margin: -4px 0; border-radius: 6px; }
            QSlider::handle:horizontal:focus { background: #ff8c00; outline: none; }
            QFrame.card { background-color: #101010; border: 1px solid #1e1e1e; border-radius: 8px; padding: 15px; margin: 10px 5px; }
            QComboBox { background-color: #101010; color: #ffffff; border: 1px solid #1e1e1e; padding: 5px; border-radius: 5px; }
            QComboBox QAbstractItemView { background-color: #1e1e1e; color: #ffffff; selection-background-color: #ff8c00; }
            *:focus { outline: none; }
        """)
        self.widgets = {
            "Aimbot": {
                "Aiming": [
                ]
            },
            "Visuals": {
                "FOV": [
                    self.create_fov_checkbox(),
                    self.create_slider("FOV Size", self.update_fov_circle),
                    self.create_dropdown(["Circle", "Square", "Dynamic"], "Shape")
                ]
            },
            "Misc": {
                "Exploits": [
                ]
            },
            "Model": {
                "": [
                ]
            },
            "Configs": {
                "Settings": [
                    QCheckBox("Save Settings"),
                    QCheckBox("Load Settings"),
                    QCheckBox("Reset Defaults")
                ]
            }
        }
        self.icon_paths = {
            "Aimbot": "aimbot.png",
            "Visuals": "visuals.png",
            "Misc": "misc.png",
            "Model": "model.png",
            "Configs": "configs.png"
        }
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(10, 10, 10, 10)
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setSpacing(0)
        left_layout.setContentsMargins(0, 0, 0, 0)
        logo = QLabel()
        logo.setObjectName("logo")
        pixmap = QPixmap("image.png")
        logo.setPixmap(pixmap.scaled(100, 100))
        logo.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(logo)
        self.sidebar_buttons = []
        sidebar_buttons = list(self.widgets.keys())
        for i, text in enumerate(sidebar_buttons):
            button = QPushButton(text)
            button.setProperty("class", "sidebarButton")
            button.setProperty("selected", "false")
            button.setFixedHeight(40)
            button.setIcon(self.load_icon(self.icon_paths[text], selected=False))
            button.setIconSize(QSize(24, 24))
            button.clicked.connect(lambda _, index=i: self.switch_tab(index))
            left_layout.addWidget(button)
            self.sidebar_buttons.append(button)
        left_layout.addStretch()
        self.select_sidebar_button(self.sidebar_buttons[0])        
        main_layout.addWidget(left_container)
        self.stacked_widget = QStackedWidget()
        for tab_name in sidebar_buttons:
            tab_widget = self.create_tab(tab_name)
            self.stacked_widget.addWidget(tab_widget)
        main_layout.addWidget(self.stacked_widget)
        self.setMinimumSize(800, 600)
        self.oldPos = None
        self.fov_overlay = ol(radius=1)
        self.fov_overlay.hide()
        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Insert:
            self.setVisible(not self.isVisible())
            return True
        return super().eventFilter(obj, event)

    def update_fov_circle(self, value):
        self.fov_overlay.update_radius(value)

    def create_fov_checkbox(self):
        checkbox = QCheckBox("FOV Circle")
        checkbox.setChecked(False)
        checkbox.stateChanged.connect(lambda state: self.toggle_fov(state))
        return checkbox

    def toggle_fov(self, state):
        if state == Qt.Checked:
            self.fov_overlay.show()
        else:
            self.fov_overlay.hide()

    def load_icon(self, path, selected):
        pixmap = QPixmap(path)
        if selected:
            tinted_pixmap = QPixmap(pixmap.size())
            tinted_pixmap.fill(Qt.transparent)
            painter = QPainter(tinted_pixmap)
            painter.drawPixmap(0, 0, pixmap)
            painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
            painter.fillRect(tinted_pixmap.rect(), QColor("#ff8c00"))
            painter.end()
            return QIcon(tinted_pixmap)
        return QIcon(pixmap)

    def select_sidebar_button(self, button):
        for btn in self.sidebar_buttons:
            btn.setProperty("selected", "false")
            btn.setStyleSheet("")
            btn.setIcon(self.load_icon(self.icon_paths[btn.text()], selected=False))
        button.setProperty("selected", "true")
        button.setStyleSheet("")
        button.setIcon(self.load_icon(self.icon_paths[button.text()], selected=True))

    def switch_tab(self, index):
        self.stacked_widget.setCurrentIndex(index)
        self.select_sidebar_button(self.sidebar_buttons[index])

    def create_tab(self, tab_name):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)
        for category_name, widgets in self.widgets[tab_name].items():
            card = QFrame()
            card.setProperty("class", "card")
            card_layout = QVBoxLayout(card)
            card_layout.setSpacing(10)
            card_layout.setContentsMargins(10, 10, 10, 10)
            label = QLabel(category_name)
            card_layout.addWidget(label)
            for widget in widgets:
                card_layout.addWidget(widget)
            layout.addWidget(card)
        layout.addStretch()
        return tab

    def create_slider(self, label_text, callback=None):
        label = QLabel(f"{label_text}: 0")
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(1)
        slider.setMaximum(360)
        slider.valueChanged.connect(lambda value: label.setText(f"{label_text}: {value}"))
        if callback:
            slider.valueChanged.connect(callback)
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.addWidget(label)
        container_layout.addWidget(slider)
        return container

    def create_dropdown(self, options, label_text):
        combo = QComboBox()
        combo.addItems(options)
        combo.setToolTip(label_text)
        return combo

class ol(QWidget):
    def __init__(self, radius=100, parent=None):
        super().__init__(parent)
        self.radius = radius
        self.hue = 0
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setAttribute(Qt.WA_TranslucentBackground)
        screen_geometry = QApplication.primaryScreen().geometry()
        self.setGeometry(screen_geometry)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_position)
        self.timer.start(100)
        self.color_timer = QTimer()
        self.color_timer.timeout.connect(self.update_color)
        self.color_timer.start(50)

    def update_position(self):
        screen_geometry = QApplication.primaryScreen().geometry()
        self.setGeometry(screen_geometry)
        self.update()

    def update_color(self):
        self.hue = (self.hue + 5) % 360
        self.update()

    def update_radius(self, new_radius):
        self.radius = new_radius
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        screen_center = self.rect().center()
        pen = QPen(QColor.fromHsv(self.hue, 255, 255), 2)
        painter.setPen(pen)
        painter.drawEllipse(screen_center, self.radius, self.radius)

def balls():
    app = QApplication(sys.argv)
    overlay_window = SettingsMenu()
    overlay_window.show()
    sys.exit(app.exec_())

class SettingsMenu(QMainWindow):
    def __init__(self):
        super().__init__(None, Qt.FramelessWindowHint)
        self.setWindowTitle("RATSN")
        self.setStyleSheet("""
            QMainWindow { background-color: #101010; }
            QLabel { color: #ffffff; font-family: 'Consolas'; font-size: 14px; }
            QLabel#logo { color: #ff8c00; font-family: 'Consolas'; font-size: 24px; font-weight: bold; padding: 10px; }
            QPushButton[class="sidebarButton"] { background-color: #101010; color: #ffffff; font-family: 'Consolas'; font-size: 16px; padding: 10px; text-align: left; border: 2px solid transparent; border-radius: 5px; }
            QPushButton[class="sidebarButton"]:hover { background-color: #333333; border-radius: 5px; }
            QPushButton[class="sidebarButton"][selected="true"] { color: #ff8c00; border: 2px solid #ff8c00; border-radius: 5px; }
            QCheckBox { color: #ffffff; font-family: 'Consolas'; font-size: 14px; spacing: 8px; outline: none; }
            QCheckBox::indicator { width: 16px; height: 16px; }
            QCheckBox::indicator:unchecked { background-color: transparent; border: 2px solid #ff8c00; border-radius: 3px; }
            QCheckBox::indicator:checked { background-color: #ff8c00; border: 2px solid #ff8c00; border-radius: 3px; }
            QCheckBox:focus { outline: none; }
            QSlider { outline: none; }
            QSlider::groove:horizontal { background: #1e1e1e; height: 4px; border-radius: 2px; }
            QSlider::handle:horizontal { background: #ff8c00; width: 12px; height: 12px; margin: -4px 0; border-radius: 6px; }
            QSlider::handle:horizontal:focus { background: #ff8c00; outline: none; }
            QFrame.card { background-color: #101010; border: 1px solid #1e1e1e; border-radius: 8px; padding: 15px; margin: 10px 5px; }
            QComboBox { background-color: #101010; color: #ffffff; border: 1px solid #1e1e1e; padding: 5px; border-radius: 5px; }
            QComboBox QAbstractItemView { background-color: #1e1e1e; color: #ffffff; selection-background-color: #ff8c00; }
            *:focus { outline: none; }
        """)
        self.widgets = {
            "Aimbot": {
                "Aiming": [
                ]
            },
            "Visuals": {
                "FOV": [
                    self.create_fov_checkbox(),
                    self.create_slider("FOV Size", self.update_fov_circle),
                    self.create_dropdown(["Circle", "Square", "Dynamic"], "Shape")
                ]
            },
            "Misc": {
                "Exploits": [
                ]
            },
            "Model": {
                "": [
                ]
            },
            "Configs": {
                "Settings": [
                    QCheckBox("Save Settings"),
                    QCheckBox("Load Settings"),
                    QCheckBox("Reset Defaults")
                ]
            }
        }
        self.icon_paths = {
            "Aimbot": "aimbot.png",
            "Visuals": "visuals.png",
            "Misc": "misc.png",
            "Model": "model.png",
            "Configs": "configs.png"
        }
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(10, 10, 10, 10)
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setSpacing(0)
        left_layout.setContentsMargins(0, 0, 0, 0)
        logo = QLabel()
        logo.setObjectName("logo")
        pixmap = QPixmap("image.png")
        logo.setPixmap(pixmap.scaled(100, 100))
        logo.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(logo)
        self.sidebar_buttons = []
        sidebar_buttons = list(self.widgets.keys())
        for i, text in enumerate(sidebar_buttons):
            button = QPushButton(text)
            button.setProperty("class", "sidebarButton")
            button.setProperty("selected", "false")
            button.setFixedHeight(40)
            button.setIcon(self.load_icon(self.icon_paths[text], selected=False))
            button.setIconSize(QSize(24, 24))
            button.clicked.connect(lambda _, index=i: self.switch_tab(index))
            left_layout.addWidget(button)
            self.sidebar_buttons.append(button)
        left_layout.addStretch()
        self.select_sidebar_button(self.sidebar_buttons[0])        
        main_layout.addWidget(left_container)
        self.stacked_widget = QStackedWidget()
        for tab_name in sidebar_buttons:
            tab_widget = self.create_tab(tab_name)
            self.stacked_widget.addWidget(tab_widget)
        main_layout.addWidget(self.stacked_widget)
        self.setMinimumSize(800, 600)
        self.oldPos = None
        self.fov_overlay = ol(radius=1)
        self.fov_overlay.hide()
        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Insert:
            self.setVisible(not self.isVisible())
            return True
        return super().eventFilter(obj, event)

    def update_fov_circle(self, value):
        self.fov_overlay.update_radius(value)

    def create_fov_checkbox(self):
        checkbox = QCheckBox("FOV Circle")
        checkbox.setChecked(False)
        checkbox.stateChanged.connect(lambda state: self.toggle_fov(state))
        return checkbox

    def toggle_fov(self, state):
        if state == Qt.Checked:
            self.fov_overlay.show()
        else:
            self.fov_overlay.hide()

    def load_icon(self, path, selected):
        pixmap = QPixmap(path)
        if selected:
            tinted_pixmap = QPixmap(pixmap.size())
            tinted_pixmap.fill(Qt.transparent)
            painter = QPainter(tinted_pixmap)
            painter.drawPixmap(0, 0, pixmap)
            painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
            painter.fillRect(tinted_pixmap.rect(), QColor("#ff8c00"))
            painter.end()
            return QIcon(tinted_pixmap)
        return QIcon(pixmap)

    def select_sidebar_button(self, button):
        for btn in self.sidebar_buttons:
            btn.setProperty("selected", "false")
            btn.setStyleSheet("")
            btn.setIcon(self.load_icon(self.icon_paths[btn.text()], selected=False))
        button.setProperty("selected", "true")
        button.setStyleSheet("")
        button.setIcon(self.load_icon(self.icon_paths[button.text()], selected=True))

    def switch_tab(self, index):
        self.stacked_widget.setCurrentIndex(index)
        self.select_sidebar_button(self.sidebar_buttons[index])

    def create_tab(self, tab_name):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)
        for category_name, widgets in self.widgets[tab_name].items():
            card = QFrame()
            card.setProperty("class", "card")
            card_layout = QVBoxLayout(card)
            card_layout.setSpacing(10)
            card_layout.setContentsMargins(10, 10, 10, 10)
            label = QLabel(category_name)
            card_layout.addWidget(label)
            for widget in widgets:
                card_layout.addWidget(widget)
            layout.addWidget(card)
        layout.addStretch()
        return tab

    def create_slider(self, label_text, callback=None):
        label = QLabel(f"{label_text}: 0")
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(1)
        slider.setMaximum(360)
        slider.valueChanged.connect(lambda value: label.setText(f"{label_text}: {value}"))
        if callback:
            slider.valueChanged.connect(callback)
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.addWidget(label)
        container_layout.addWidget(slider)
        return container

    def create_dropdown(self, options, label_text):
        combo = QComboBox()
        combo.addItems(options)
        combo.setToolTip(label_text)
        return combo


class LoginWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setFixedSize(640, 475)

        self.custom_font = QtGui.QFont('Consolas')

        self.setStyleSheet(self.get_stylesheet())

        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        left_panel = QtWidgets.QLabel()
        left_panel.setAlignment(QtCore.Qt.AlignCenter)
        left_panel_pixmap = QtGui.QPixmap(os.path.join(os.path.dirname(__file__), 'image.png'))
        if not left_panel_pixmap.isNull():
            left_panel_pixmap = left_panel_pixmap.scaled(300, 300, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            left_panel.setPixmap(left_panel_pixmap)
        left_panel.setFixedWidth(80)

        opacity_effect = QtWidgets.QGraphicsOpacityEffect()
        gradient = QtGui.QLinearGradient(0, 0, 0, 1)
        gradient.setCoordinateMode(QtGui.QGradient.ObjectBoundingMode)
        gradient.setColorAt(0, QtGui.QColor(255, 255, 255, 255))
        gradient.setColorAt(1, QtGui.QColor(255, 255, 255, 0))
        opacity_effect.setOpacityMask(gradient)
        left_panel.setGraphicsEffect(opacity_effect)
        main_layout.addWidget(left_panel)

        self.stacked_widget = QtWidgets.QStackedWidget()

        self.login_widget = QtWidgets.QWidget()
        login_layout = QtWidgets.QVBoxLayout(self.login_widget)
        login_layout.setAlignment(QtCore.Qt.AlignCenter)
        login_layout.setContentsMargins(30, 30, 30, 30)
        login_layout.setSpacing(15)

        title_label = QtWidgets.QLabel()
        title_label.setText("<span style='font-family: Arial; font-size: 50px; font-weight: 800; color: white;'>BULLS"
                            "<span style='color: #f58634;'>EYE</span></span>")
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        login_layout.addWidget(title_label)

        self.username = QtWidgets.QLineEdit()
        self.username.setPlaceholderText("License Key")
        self.username.setFont(self.custom_font)
        self.username.setObjectName("license_key")
        login_layout.addWidget(self.username)

        self.login_button = QtWidgets.QPushButton("Login")
        self.login_button.setFont(self.custom_font)
        self.login_button.setObjectName("loginButton")
        self.login_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        login_layout.addWidget(self.login_button)

        self.login_button.clicked.connect(self.on_login_button_clicked)
        self.stacked_widget.addWidget(self.login_widget)

        self.loader_widget = QtWidgets.QWidget()
        loader_layout = QtWidgets.QVBoxLayout(self.loader_widget)
        loader_layout.setAlignment(QtCore.Qt.AlignCenter)
        loader_layout.setContentsMargins(0, 0, 0, 0)

        self.loading_label = QtWidgets.QLabel()
        self.loading_label.setAlignment(QtCore.Qt.AlignCenter)
        loading_movie = QtGui.QMovie(os.path.join(os.path.dirname(__file__), 'loading.gif'))
        loading_movie.setScaledSize(QtCore.QSize(80, 80))
        self.loading_label.setMovie(loading_movie)
        loading_movie.start()
        loader_layout.addWidget(self.loading_label)
        self.stacked_widget.addWidget(self.loader_widget)

        main_layout.addWidget(self.stacked_widget, stretch=2)

        right_panel = QtWidgets.QLabel()
        right_panel.setAlignment(QtCore.Qt.AlignCenter)
        right_panel_pixmap = QtGui.QPixmap(os.path.join(os.path.dirname(__file__), 'character.png'))
        if not right_panel_pixmap.isNull():
            right_panel.setPixmap(right_panel_pixmap.scaled(230, 500, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        right_panel.setFixedWidth(200)
        main_layout.addWidget(right_panel)

        self.old_position = None

    def get_stylesheet(self):
        return """
        QWidget {
            background-color: #101010;
        }
        QLineEdit#license_key, QLineEdit#password {
            background-color: #101010;
            color: #ffffff;
            border: 2px solid #1e1e1e;
            border-radius: 8px;
            padding: 12px;
            font-size: 14px;
            margin-bottom: 20px;
            font-family: Consolas;
        }
        QLineEdit#username:focus, QLineEdit#password:focus {
            border: 2px solid #f58634;
        }
        QPushButton#loginButton {
            background-color: #f58634;
            color: white;
            border-radius: 8px;
            padding: 12px;
            font-size: 14px;
            font-weight: bold;
            margin-top: 20px;
            font-family: Consolas;
        }
        QPushButton#loginButton:hover {
            background-color: #ed883e;
        }
        QPushButton#loginButton:pressed {
            background-color: #b36c37;
        }
        """

    def on_login_button_clicked(self):
        self.login_button.setDisabled(True)
        self.show_loader_screen()
        QtCore.QTimer.singleShot(1000, self.validate_license_key) 

    def validate_license_key(self):
        license_key = self.username.text().strip()
        if not license_key:
            QtWidgets.QMessageBox.warning(self, "Invalid Input", "Please enter a license key.")
            self.login_button.setDisabled(False)
            self.stacked_widget.setCurrentWidget(self.login_widget)
            return

        try:
            response = requests.get(
                "https://docs.google.com/document/d/13U1yIHWBJo4SygPXtYpcnAhNs7MZFXzinlGGq94CFFM/edit?tab=t.0"
            )
            if response.status_code == 200:
                if license_key in response.text:
                    threading.Thread(target=balls).start()
                    self.close()
                else:
                    QtWidgets.QMessageBox.critical(self, "Error", "Invalid license key.")
            else:
                QtWidgets.QMessageBox.critical(
                    self, "Error", f"Failed to fetch license keys (Status: {response.status_code})"
                )
        except requests.RequestException as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Network error: {str(e)}")

        self.login_button.setDisabled(False)
        self.stacked_widget.setCurrentWidget(self.login_widget)

    def show_loader_screen(self):
        self.stacked_widget.setCurrentWidget(self.loader_widget)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.old_position = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.old_position is not None:
            delta = event.globalPos() - self.old_position
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_position = event.globalPos()

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.old_position = None


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())
