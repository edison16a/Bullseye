from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QSlider, QCheckBox, QPushButton, 
                             QFrame, QStackedWidget, QSpacerItem, QSizePolicy)
from PyQt5.QtCore import Qt, QSize, QRect, QTimer
from PyQt5.QtGui import QPixmap, QIcon, QColor, QPainter, QPen
import sys

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

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        screen_center = self.rect().center()
        pen = QPen(QColor.fromHsv(self.hue, 255, 255), 2)
        painter.setPen(pen)
        painter.drawEllipse(screen_center, self.radius, self.radius)

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
            *:focus { outline: none; }
        """)
        self.widgets = {
            "Aimbot": {
                "Aiming": [
                    QCheckBox("Target Players"),
                    QCheckBox("Visible Check"),
                    self.create_slider("Smooth"),
                    self.create_slider("Curve"),
                    self.create_slider("Aim Distance")
                ]
            },
            "Visuals": {
                "Field of View": [
                    QCheckBox("Enable Silent Aim"),
                    self.create_slider("Field of View"),
                    QCheckBox("FOV Circle")
                ]
            },
            "Misc": {
                "Environment Control": [
                    self.create_slider("Time of Day"),
                    QCheckBox("Weather Control"),
                    QCheckBox("Spawn NPCs"),
                    self.create_slider("Gravity Control")
                ]
            },
            "Model": {
                "Manage Lists": [
                    QCheckBox("Manage Player List"),
                    QCheckBox("Blacklist"),
                    QCheckBox("Friend List"),
                    QCheckBox("Whitelist")
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
        self.fov_overlay = ol(radius=150)
        self.fov_overlay.show()

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.oldPos:
            delta = event.globalPos() - self.oldPos
            self.move(self.pos() + delta)
            self.oldPos = event.globalPos()

    def mouseReleaseEvent(self, event):
        self.oldPos = None

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
        layout.setSpacing(15)
        version_label = QLabel("ur cheat name v1.0.0")
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet("color: #ff8c00; font-size: 16px; font-weight: bold;")
        layout.addWidget(version_label)
        for box_name, widgets in self.widgets[tab_name].items():
            card = self.create_card(box_name, widgets)
            layout.addWidget(card)
        layout.addStretch()
        return tab

    def create_card(self, box_name, widgets):
        card = QFrame()
        card.setObjectName("card")
        card.setProperty("class", "card")
        layout = QVBoxLayout(card)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        label = QLabel(box_name)
        label.setStyleSheet("color: #ff8c00; font-size: 16px; font-weight: bold;")
        layout.addWidget(label)
        for widget in widgets:
            if isinstance(widget, QCheckBox):
                layout.addWidget(widget)
            elif isinstance(widget, QSlider):
                slider_layout = QHBoxLayout()
                slider_layout.addWidget(QLabel(widget.toolTip()))
                slider_layout.addWidget(widget)
                value_label = QLabel(str(widget.value()))
                slider_layout.addWidget(value_label)
                widget.valueChanged.connect(lambda value, label=value_label: label.setText(str(value)))
                layout.addLayout(slider_layout)
        layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        return card

    def create_slider(self, label_text):
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(0)
        slider.setMaximum(100)
        slider.setValue(50)
        slider.setToolTip(label_text)
        return slider

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('')
    window = SettingsMenu()
    window.show()
    sys.exit(app.exec_())
