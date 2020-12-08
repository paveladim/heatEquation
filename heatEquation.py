import numpy as np
from matplotlib import cm
import matplotlib.pyplot as plt

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import interface
import sys

def phi(x, t):
    value = 1 - x * x
    return value

def mu1(x, t):
    value = np.cos(t)
    return value

def mu2(x, t):
    value = np.sin(4 * t)
    return value

def g(x, t):
    value = np.cos(np.pi * x) * t / (t + 1)
    return value

def solveLayer(j, x, t, solMatr, h, tau, M, N):
    if (j == 0):
        for i in range(0, N + 1):
            solMatr[j][i] = phi(x, t)
            x += h

        x = 0
        t += tau
        return x, t

    solMatr[j][0] = mu1(x, t)
    x += h
    for i in range(1, N):
        F = g(x, t)
        V1 = solMatr[j - 1][i - 1]
        V2 = solMatr[j - 1][i]
        V3 = solMatr[j - 1][i + 1]

        value = ((3 * (V1 - 2 * V2 + V3) / (h * h)) + F) * tau + V2
        solMatr[j][i] = value;
        x += h

    solMatr[j][N] = mu2(x, t)
    x = 0
    t += tau
    return x, t

def heatEqSolver(solMatr, h, tau, M, N):
    x = 0
    t = 0
    for j in range(M + 1):
        x, t = solveLayer(j, x, t, solMatr, h, tau, M, N)

    return solMatr

class Example(QMainWindow, interface.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Задание 10. Петров Павел, гр. 381803-1, команда 1.")
        self.buildSolution.clicked.connect(self.buttonClicked)

    def buttonClicked(self):

        if (self.lineEditForN.text() == ""):
            QMessageBox.question(self, 'Ошибка!', "Не введено число разбиений по пространству!", QMessageBox.Ok, QMessageBox.Ok)
            
        if (self.lineEditForM.text() == ""):
            QMessageBox.question(self, 'Ошибка!', "Не введено число разбиений по времени!", QMessageBox.Ok, QMessageBox.Ok)
            
        if (self.lineEditForT.text() == ""):
            QMessageBox.question(self, 'Ошибка!', "Не введена правая граница промежутка времени!", QMessageBox.Ok, QMessageBox.Ok)
            
        # считываю разбиение по пространству
        temp = int(self.lineEditForN.text())
        N = temp

        # считываю разбиение по времени
        temp = int(self.lineEditForM.text())
        M = temp

        # считываю конечный промежуток времени
        temp = float(self.lineEditForT.text())
        T = temp

        self.tableForSolution.setRowCount(M+1)
        self.tableForSolution.setColumnCount(N+1)

        head = []
        for i in range(0, M+1):
            temp = "Слой " + str(i)
            head.append(temp)

        self.tableForSolution.setVerticalHeaderLabels(head)

        head.clear()
        for i in range(0, N+1):
            temp = "Компонента решения " + str(i)
            head.append(temp)

        self.tableForSolution.setHorizontalHeaderLabels(head)
        self.tableForSolution.resizeColumnsToContents()

        h = 1.0 / N
        tau = T / M
        
        if (6 * tau >= h * h):
            QMessageBox.question(self, 'Ошибка!', "Нарушено ограничение на шаг по времени!", QMessageBox.Ok, QMessageBox.Ok)

        solMatr = np.zeros((M + 1, N + 1))
        solMatr = heatEqSolver(solMatr, h, tau, M, N)
        
        for j in range(M + 1):
            for i in range(N + 1):
                temp = str(solMatr[j][i])
                newItem = QTableWidgetItem(temp)
                self.tableForSolution.setItem(j, i, newItem)
                
        # создаём полотно для рисунка
        fig = plt.figure(figsize=(10, 10))

        # создаём рисунок пространства с поверхностью
        ax = fig.add_subplot(1, 1, 1, projection='3d')

        # размечаем границы осей для аргументов
        xval = np.linspace(0, 1, N + 1)
        yval = np.linspace(0, T, M + 1)

        # создаём массив с xval столбцами и yval строками
        # - в этом массиве будут храниться значения z
        x, y = np.meshgrid(xval, yval)
        
        # создаём поверхность
        surf = ax.plot_surface(
            # отмечаем аргументы и уравнение поверхности
            x, y, solMatr,
            # шаг прорисовки сетки
            # - чем меньше значение, тем плавнее
            # - будет градиент на поверхности
            rstride=N + 1,
            cstride=M + 1,
            # цветовая схема plasma
            cmap=cm.plasma)

        ax.set_xlabel('Сечение стержня x')
        ax.set_ylabel('Время t')
        ax.set_zlabel('Температура стержня u(x,t)')
        ax.set_title('Изменение температуры стержня с течением времени')

        fig.canvas.set_window_title('Визуализация решения')
        fig.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = Example()
    form.show()
    app.exec()

