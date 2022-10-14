import os
import sys
import time
import ctypes

from functools import partial
from interface import Ui_MainWindow

from PyQt5.QtCore import Qt, pyqtSignal, QThread
from PyQt5.QtGui import QColor, QKeySequence
from PyQt5.QtWidgets import QApplication, QMainWindow, QShortcut


#        MainWindow.setFixedSize(550, 545)
class POINT(ctypes.Structure):
    _fields_ = [('x', ctypes.c_long),
                ('y', ctypes.c_long)]


class Monitor(QThread):
    signal = pyqtSignal(list)
    
    def __init__(self, event, e, checked, parent=None):
        QThread.__init__(self, parent)
        self._event = event
        self.e = e
        self.c = checked
        self.dc = ctypes.windll.user32.GetDC(0)

    def _winPosition(self):
        cursor = POINT()
        ctypes.windll.user32.GetCursorPos(ctypes.byref(cursor))
        return (cursor.x, cursor.y)

    def _winGetPixel(self, x, y):
        colorRef = ctypes.windll.gdi32.GetPixel(self.dc, x, y)
        red = colorRef % 256
        colorRef //= 256
        green = colorRef % 256
        colorRef //= 256
        blue = colorRef
        return (red, green, blue)

    def run(self):
        while True:
            if self.e == "lines":
                x, y = self._winPosition()
                self.signal.emit([x, y, self._winGetPixel(x, y)])
                time.sleep(0.03)

            elif self.e == "btns":
                if self.c == True:
                    for sec in range(3, -1, -1):
                        self.signal.emit([self._event, str(sec)])
                        time.sleep(1)
                    break
                else:
                    self.signal.emit([self._event, "n"])
                    break


class MouseInfoWindow(QMainWindow):
    colorChanged = pyqtSignal(QColor)

    def __init__(self, parent = None):
        super().__init__(parent)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.save_log_path = os.getcwd() + "\\mouseInfoLog.txt"
        self.clipboard = QApplication.clipboard()

        self._bindHotkeys()
        self._connectBtns()
        self.ui.SavePathLine.setText(self.save_log_path)
        self._startSignal(None, "lines", self._displayData)

    def _displayData(self, args):
        x, y = (args[0], args[1])
        r, g, b = args[2][0], args[2][1], args[2][2]
        rHex = hex(r)[2:].upper().rjust(2, '0')
        gHex = hex(g)[2:].upper().rjust(2, '0')
        bHex = hex(b)[2:].upper().rjust(2, '0')
        hexColor = '#%s%s%s' % (rHex, gHex, bHex)
        
        self.ui.RGBLine.setText(f"{r}, {g}, {b}")
        self.ui.HexLine.setText(hexColor)
        self.ui.ColorFrame.setStyleSheet(f"""border: 1px solid gray;
                                            \nbackground-color: {hexColor}""")
        self.ui.XYLine.setText(f"{x}, {y}")

    def _connectBtns(self):
        self.ui.CopyAllBtn.clicked.connect(partial(self._startSignal, event="copyAll", e="btns", callback=self._clickHandler))
        self.ui.CopyXYBtn.clicked.connect(partial(self._startSignal, event="copyXY", e="btns", callback=self._clickHandler))
        self.ui.CopyRGBBtn.clicked.connect(partial(self._startSignal, event="copyRGB", e="btns", callback=self._clickHandler))
        self.ui.CopyHexBtn.clicked.connect(partial(self._startSignal, event="copyHex", e="btns", callback=self._clickHandler))

        self.ui.LogAllBtn.clicked.connect(partial(self._startSignal, event="logAll", e="btns", callback=self._clickHandler))
        self.ui.LogXYBtn.clicked.connect(partial(self._startSignal, event="logXY", e="btns", callback=self._clickHandler))
        self.ui.LogRGBBtn.clicked.connect(partial(self._startSignal, event="logRGB", e="btns", callback=self._clickHandler))
        self.ui.LogHexBtn.clicked.connect(partial(self._startSignal, event="logHex", e="btns", callback=self._clickHandler))

        self.ui.SaveLogBtn.clicked.connect(self._saveLog)

    def _bindHotkeys(self):
        self.f1 = QShortcut(QKeySequence("F1"), self)
        self.f2 = QShortcut(QKeySequence("F2"), self)
        self.f3 = QShortcut(QKeySequence("F3"), self)
        self.f4 = QShortcut(QKeySequence("F4"), self)
        self.f5 = QShortcut(QKeySequence("F5"), self)
        self.f6 = QShortcut(QKeySequence("F6"), self)
        self.f7 = QShortcut(QKeySequence("F7"), self)
        self.f8 = QShortcut(QKeySequence("F8"), self)

        self.f1.activated.connect(partial(self._startSignal, event="copyAll", e="btns", callback=self._clickHandler))
        self.f2.activated.connect(partial(self._startSignal, event="copyXY", e="btns", callback=self._clickHandler))
        self.f3.activated.connect(partial(self._startSignal, event="copyRGB", e="btns", callback=self._clickHandler))
        self.f4.activated.connect(partial(self._startSignal, event="copyHex", e="btns", callback=self._clickHandler))
        self.f5.activated.connect(partial(self._startSignal, event="logAll", e="btns", callback=self._clickHandler))
        self.f6.activated.connect(partial(self._startSignal, event="logXY", e="btns", callback=self._clickHandler))
        self.f7.activated.connect(partial(self._startSignal, event="logRGB", e="btns", callback=self._clickHandler))
        self.f8.activated.connect(partial(self._startSignal, event="logHex", e="btns", callback=self._clickHandler))

    def _startSignal(self, event, e, callback):
        checked = self.ui.checkBox.isChecked()
        
        self.monitor = Monitor(event, e, checked)
        self.monitor.signal.connect(callback)
        self.monitor.start()
    
    def _clickHandler(self, signal):
        event = signal[0]
        sec = signal[1]

        if self.ui.checkBox.isChecked():
            if event == "copyAll": self.ui.CopyAllBtn.setText("Copy in " + sec)
            if event == "copyXY": self.ui.CopyXYBtn.setText("Copy in " + sec)
            if event == "copyRGB": self.ui.CopyRGBBtn.setText("Copy in " + sec)
            if event == "copyHex": self.ui.CopyHexBtn.setText("Copy in " + sec)
            if event == "logAll": self.ui.LogAllBtn.setText("Log in " + sec)
            if event == "logXY": self.ui.LogXYBtn.setText("Log in " + sec)
            if event == "logRGB": self.ui.LogRGBBtn.setText("Log in " + sec)
            if event == "logHex": self.ui.LogHexBtn.setText("Log in " + sec)

        if sec == "0" or sec == "n":
            all = str("x,y -> " + self.ui.XYLine.text() + "; " +
                    "rgb -> " + self.ui.RGBLine.text() + "; " +
                    "hex -> " + self.ui.HexLine.text())
            xy = "x,y -> " + str(self.ui.XYLine.text())
            rgb = "rgb -> " + str(self.ui.RGBLine.text())
            as_hex = "hex -> " + str(self.ui.HexLine.text())

            if event == "copyAll":
                self.ui.CopyAllBtn.setText("Copy All (F1)")
                self.clipboard.setText(all)
                self.ui.SavedLogLine.setText("Copied " + all)

            if event == "copyXY": 
                self.ui.CopyXYBtn.setText("Copy XY (F2)")
                self.clipboard.setText(xy)
                self.ui.SavedLogLine.setText("Copied " + xy)

            if event == "copyRGB":
                self.ui.CopyRGBBtn.setText("Copy RGB (F3)")
                self.clipboard.setText(rgb)
                self.ui.SavedLogLine.setText("Copied " + rgb)

            if event == "copyHex": 
                self.ui.CopyHexBtn.setText("Copy RGB as Hex (F4)")
                self.clipboard.setText(as_hex)
                self.ui.SavedLogLine.setText("Copied " + as_hex)

            if event == "logAll": 
                self.ui.LogAllBtn.setText("Log All (F5)")
                self.ui.LogLine.appendPlainText(all)

            if event == "logXY": 
                self.ui.LogXYBtn.setText("Log XY (F6)")
                self.ui.LogLine.appendPlainText(xy)

            if event == "logRGB": 
                self.ui.LogRGBBtn.setText("Log RGB (F7)")
                self.ui.LogLine.appendPlainText(rgb)

            if event == "logHex": 
                self.ui.LogHexBtn.setText("Log RGB as Hex (F8)")
                self.ui.LogLine.appendPlainText(as_hex)

    def _saveLog(self):
        path = self.ui.SavePathLine.text()
        logs = self.ui.LogLine.toPlainText()

        with open(path, "w+") as log_file:
            log_file.write(logs)
        
        self.ui.SavedLogLine.setText("Log file saved to " + path)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MouseInfoWindow()
    window.setWindowFlag(Qt.WindowStaysOnTopHint)
    window.show()
    sys.exit(app.exec_())