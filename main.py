import sys
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QIcon, QPixmap, QColor, QPainter
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QMessageBox
from app.storage import load, save
from app.monitor import Monitor
from app.widget import Widget
from app.settings import Settings
from app.windows_usage import UsageReader
from app.monitor import size
from app.layout import remaining_text
from app.topmost import keep_above_taskbar


def icon():
    pix = QPixmap(64,64); pix.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pix); painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setBrush(QColor('#2589c9')); painter.setPen(Qt.PenStyle.NoPen); painter.drawEllipse(2,2,60,60)
    painter.setPen(QColor('white')); painter.drawText(pix.rect(), Qt.AlignmentFlag.AlignCenter, '↓')
    painter.end(); return QIcon(pix)


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    if not QSystemTrayIcon.isSystemTrayAvailable():
        QMessageBox.critical(None, '启动失败', '系统托盘不可用'); return 1
    state = load()
    monitor = Monitor(state)
    widget = Widget(state); widget.setWindowOpacity(state['opacity'])
    reader = UsageReader(app)
    def received(result, error):
        if result is not None:
            widget.system_usage = result
        elif state.get('usage_source') == 'windows':
            widget.system_usage = None
        if error and state.get('usage_source') == 'windows':
            tray.setToolTip(error[:120])
        if widget.isVisible(): widget.update()
    reader.result.connect(received)
    def refresh_system():
        if state.get('usage_source') == 'windows' and not reader.isRunning():
            reader.start()
    tray = QSystemTrayIcon(icon(), app)
    menu = QMenu()
    settings_action = menu.addAction('打开设置')
    quiet = '--quiet' in sys.argv[1:]
    toggle = menu.addAction('隐藏悬浮窗' if state['visible'] and not quiet else '显示悬浮窗')
    reset_action = menu.addAction('重置流量数据')
    menu.addSeparator()
    exit_action = menu.addAction('退出软件')

    def open_settings():
        dialog = Settings(state, widget)
        dialog.exec()
        refresh_system()

    def toggle_widget():
        state['visible'] = not widget.isVisible()
        widget.setVisible(state['visible'])
        toggle.setText('隐藏悬浮窗' if state['visible'] else '显示悬浮窗')
        save(state)

    def reset():
        if QMessageBox.question(None, '确认重置', '确定清零本机累计流量吗？Windows 提供的用量无法通过本软件重置。') == QMessageBox.StandardButton.Yes:
            state['daily'] = state['monthly'] = 0
            monitor.sample(initial=True)
            widget.update(); save(state)

    def tick():
        old_speed = widget.speed
        old_daily, old_monthly = state['daily'], state['monthly']
        widget.speed = monitor.sample()
        if widget.isVisible() and (size(old_speed) != size(widget.speed) or
                                   size(old_daily) != size(state['daily']) or
                                   remaining_text(state['limit_gb']*1024**3 - old_monthly) !=
                                   remaining_text(state['limit_gb']*1024**3 - state['monthly'])):
            widget.update()
        tray.setToolTip(f'下载 {widget.speed/1024:.1f} KB/s')

    settings_action.triggered.connect(open_settings)
    toggle.triggered.connect(toggle_widget)
    reset_action.triggered.connect(reset)
    exit_action.triggered.connect(app.quit)
    def persist():
        state['x'], state['y'] = widget.x(), widget.y()
        save(state)
        if reader.isRunning(): reader.wait(18000)

    app.aboutToQuit.connect(persist)
    app.commitDataRequest.connect(lambda manager: persist())
    tray.setContextMenu(menu)
    tray.activated.connect(lambda reason: open_settings() if reason == QSystemTrayIcon.ActivationReason.DoubleClick else None)
    tray.show()
    if state['visible'] and not quiet: widget.show()
    timer = QTimer(app); timer.timeout.connect(tick); timer.start(1000)
    save_timer = QTimer(app); save_timer.timeout.connect(lambda: save(state)); save_timer.start(10000)
    system_timer = QTimer(app); system_timer.timeout.connect(refresh_system); system_timer.start(300000)
    layer_timer = QTimer(app); layer_timer.timeout.connect(lambda: keep_above_taskbar(widget)); layer_timer.start(400)
    refresh_system()
    return app.exec()

if __name__ == '__main__':
    sys.exit(main())
