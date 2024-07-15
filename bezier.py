from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QComboBox, QLineEdit, QLabel, QInputDialog, QScrollArea, QErrorMessage, QSlider
from PyQt5.QtCore import Qt
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import numpy as np
import random

class BezierApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()
        self.input_layout = QVBoxLayout()

        self.degree_label = QLabel("Select degree:")
        self.combo = QComboBox()
        self.combo.addItems(["1 (Linear)", "2 (Quadratic)", "3 (Cubic)", "4 (Quartic)", "n-th degree"])

        self.generate_button = QPushButton("Generate random values")
        self.clear_button = QPushButton("Clear input fields")
        self.generate_plot_button = QPushButton("Plot")

        self.wid = QWidget()
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.wid)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFixedHeight(300)

        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvasQTAgg(self.fig)
        self.axes = self.fig.add_subplot(111)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setValue(50)

        self.slider_value_label = QLabel(f"Current t value: {self.slider.value() / 100}")

        self.index = self.combo.currentIndex() + 2
        self.previous_index = self.combo.currentIndex()
        self.control_points = []

        self.setup_initial_input_fields()

        self.combo.activated.connect(self.modifyGUI)
        self.slider.valueChanged.connect(self.slider_value_changed)
        self.generate_button.clicked.connect(self.generate_values)
        self.clear_button.clicked.connect(self.clear_fields)
        self.generate_plot_button.clicked.connect(self.generate_plot)

        self.layout.addWidget(self.degree_label)
        self.layout.addWidget(self.combo)
        self.layout.addWidget(self.scroll_area)
        self.layout.addWidget(self.clear_button)
        self.layout.addWidget(self.generate_button)
        self.layout.addWidget(self.generate_plot_button)
        self.layout.addWidget(self.canvas)
        self.layout.addWidget(self.slider)
        self.layout.addWidget(self.slider_value_label)

        self.wid.setLayout(self.input_layout)
        self.setLayout(self.layout)
        self.show()

    def setup_initial_input_fields(self):
        for ind in range(self.index):
            row = QWidget()
            layout_row = QHBoxLayout()
            layout_row.setContentsMargins(0, 0, 0, 0)
            row.setLayout(layout_row)
            label = QLabel(f'P{ind + 1}')
            layout_row.addWidget(label)

            line_edit1 = QLineEdit()
            line_edit1.setPlaceholderText('Set x')
            line_edit1.setFixedSize(100, 20)
            layout_row.addWidget(line_edit1)

            line_edit2 = QLineEdit()
            line_edit2.setPlaceholderText('Set y')
            line_edit2.setFixedSize(100, 20)
            layout_row.addWidget(line_edit2)

            self.input_layout.addWidget(row)

    def modifyGUI(self):
        count = 0
        i = self.input_layout.count() - 1

        if self.combo.currentIndex() != 4:
            while i >= 0:
                item = self.input_layout.itemAt(i)
                if item.widget() is not None:
                    item.widget().deleteLater()
                    self.input_layout.removeWidget(item.widget())
                    i -= 1

        if self.combo.currentIndex() == 4:
            num, ok = QInputDialog.getInt(self, "Degree input dialog", "Enter a degree", value=5, min=5, max=100)
            if ok:
                count = num
                while i >= 0:
                    item = self.input_layout.itemAt(i)
                    if item.widget() is not None:
                        item.widget().deleteLater()
                        self.input_layout.removeWidget(item.widget())
                        i -= 1
            else:
                self.combo.setCurrentIndex(self.previous_index)
                return
        else:
            count = self.combo.currentIndex() + 1

        for j in range(count + 1):
            row = QWidget()
            layout_row = QHBoxLayout()
            layout_row.setContentsMargins(0, 0, 0, 0)
            row.setLayout(layout_row)
            label = QLabel(f'P{j + 1}')
            layout_row.addWidget(label)

            line_edit1 = QLineEdit()
            line_edit1.setPlaceholderText('Set x')
            line_edit1.setFixedSize(100, 20)
            layout_row.addWidget(line_edit1)

            line_edit2 = QLineEdit()
            line_edit2.setPlaceholderText('Set y')
            line_edit2.setFixedSize(100, 20)
            layout_row.addWidget(line_edit2)

            row.setFixedHeight(20)
            self.input_layout.addWidget(row)

        self.wid.adjustSize()
        self.adjustSize()
        self.previous_index = self.combo.currentIndex()

    def linear_interp(self, p1, p2, t):
        return (1 - t) * p1 + t * p2

    def de_casteljau(self, control_points, t):
        points = np.array(control_points)
        n = len(points)
        intermediate_points = []
        for r in range(1, n):
            new_points = []
            for i in range(n - r):
                new_point = self.linear_interp(points[i], points[i + 1], t)
                new_points.append(new_point)
            points = np.array(new_points)
            intermediate_points.append(points.copy())
        return points[0], intermediate_points

    def slider_value_changed(self):
        t = self.slider.value() / 100
        self.slider_value_label.setText(f"Current t value: {t}")
        if self.control_points:
            self.update_plot(t)

    def generate_plot(self):
        self.control_points = []
        t = self.slider.value() / 100

        for i in range(self.input_layout.count()):
            row_widget = self.input_layout.itemAt(i).widget()
            row_layout = row_widget.layout()
            x_input_edit = row_layout.itemAt(1).widget()
            y_input_edit = row_layout.itemAt(2).widget()
            x_input = x_input_edit.text()
            y_input = y_input_edit.text()

            try:
                x = float(x_input)
                y = float(y_input)
                point = [x, y]
                self.control_points.append(point)
            except ValueError:
                err = QErrorMessage()
                err.showMessage("Invalid input. Please input numerical values.")
                err.exec_()
                return

        if len(self.control_points) == self.input_layout.count():
            self.update_plot(t)

    def update_plot(self, t):
        self.axes.clear()
        bezier_curve_points_list = []
        id = 1
        control_points_arr = np.array(self.control_points)
        self.axes.plot(control_points_arr[:, 0], control_points_arr[:, 1], 'ro-', label='Control points')
        final, points = self.de_casteljau(control_points_arr, t)
        for q in range(101):
            point = self.de_casteljau(control_points_arr, q / 100)[0]
            bezier_curve_points_list.append(point)
        bezier_curve = np.array(bezier_curve_points_list)
        for intermediate in points:
            self.axes.plot(intermediate[:, 0], intermediate[:, 1], marker='o', linestyle='-', label=f'Segment{id}')
            id += 1
        self.axes.plot(bezier_curve[:, 0], bezier_curve[:, 1], linestyle='--', color='black', label='Bezier curve')
        self.axes.legend()
        self.canvas.draw()

    def generate_values(self):
        for i in range(self.input_layout.count()):
            row_widget = self.input_layout.itemAt(i).widget()
            row_layout = row_widget.layout()
            row_layout.itemAt(1).widget().setText(str(random.randrange(-200, 200)))
            row_layout.itemAt(2).widget().setText(str(random.randrange(-200, 200)))

    def clear_fields(self):
        for i in range(self.input_layout.count()):
            row_widget = self.input_layout.itemAt(i).widget()
            row_layout = row_widget.layout()
            row_layout.itemAt(1).widget().setText("")
            row_layout.itemAt(2).widget().setText("")


if __name__ == '__main__':
    app = QApplication([])
    ex = BezierApp()
    app.exec_()
