# ui.py

from importlib import resources

from PySide6.QtCore import QDir, QFile, QSettings
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication, QFileDialog

import keys
from . import version
from . import key

DATA = resources.files(keys) / "data"
ICONS = DATA / "icons"
UI = DATA / "ui"

HOME = QDir.homePath()
PRIV_KEY = f"{HOME}/Private key.pem"
PUB_KEY = f"{HOME}/Public key.pem"


def browse_key(dialog):
    if file_name := QFileDialog.getOpenFileName(
        dialog, dir=HOME, filter="RSA keys (*.pem)"
    )[0]:
        dialog.button_key.setText(file_name)


def browse_priv_key(dialog):
    if file_name := QFileDialog.getSaveFileName(
        dialog, dir=PRIV_KEY, filter="RSA keys (*.pem)"
    )[0]:
        dialog.button_priv_key.setText(file_name)


def browse_pub_key(dialog):
    if file_name := QFileDialog.getSaveFileName(
        dialog, dir=PUB_KEY, filter="RSA keys (*.pem)"
    )[0]:
        dialog.button_pub_key.setText(file_name)


def licence_key(ui_loader, window):
    try:
        licence = key.licence_key(window)
    except OSError as err:
        dialog = ui_loader.load(UI / "error.ui", window)
        dialog.label_error.setText("An error occurred while loading your private key")
        dialog.label_description.setText(
            f"[Error #{err.errno}] {err.strerror}<br /><em>{err.filename}</em>"
        )
        dialog.exec()
    except ValueError as err:
        dialog = ui_loader.load(UI / "error.ui", window)
        dialog.label_error.setText("An error occurred while loading your private key")
        dialog.label_description.setText(str(err))
        dialog.exec()
    else:
        window.edit_licence_key.setPlainText(licence)


def show_about(ui_loader, window):
    dialog = ui_loader.load(UI / "about.ui", window)
    dialog.label_icon.setPixmap(QPixmap(ICONS / "icon.png"))
    dialog.label_version.setText(version())
    dialog.exec()


def show_new_rsa_keys(ui_loader, window):
    dialog = ui_loader.load(UI / "new_rsa_keys.ui", window)

    if not QFile.exists(PUB_KEY):
        dialog.button_pub_key.setText(PUB_KEY)

    if not QFile.exists(PRIV_KEY):
        dialog.button_priv_key.setText(PRIV_KEY)

    dialog.button_pub_key.clicked.connect(lambda: browse_pub_key(dialog))
    dialog.button_priv_key.clicked.connect(lambda: browse_priv_key(dialog))

    if dialog.exec():
        try:
            key.new_keys(dialog)
        except OSError as err:
            dialog = ui_loader.load(UI / "error.ui", window)
            dialog.label_error.setText("An error occurred while saving your keys")
            dialog.label_description.setText(
                f"[Error #{err.errno}] {err.strerror}<br /><em>{err.filename}</em>"
            )
            dialog.exec()
        else:
            window.settings.setValue("priv_key", dialog.button_priv_key.text())


def show_priv_key(ui_loader, window):
    dialog = ui_loader.load(UI / "priv_key.ui", window)

    if QFile.exists(priv_key := window.settings.value("priv_key")):
        dialog.button_key.setText(priv_key)

    dialog.button_key.clicked.connect(lambda: browse_key(dialog))

    if dialog.exec():
        window.settings.setValue("priv_key", dialog.button_key.text())


def main():
    ui_loader = QUiLoader()

    app = QApplication([])
    app.setApplicationName("Yocto Keys")
    app.setWindowIcon(QIcon(f"{ICONS}/icon.png"))

    window = ui_loader.load(UI / "main.ui")
    window.settings = QSettings("Yocto", "Keys")

    window.action_new_rsa_keys.triggered.connect(
        lambda: show_new_rsa_keys(ui_loader, window)
    )
    window.action_priv_key.triggered.connect(lambda: show_priv_key(ui_loader, window))
    window.action_about.triggered.connect(lambda: show_about(ui_loader, window))
    window.button_sign.clicked.connect(lambda: licence_key(ui_loader, window))

    window.show()

    if not window.settings.allKeys():
        window.action_new_rsa_keys.trigger()

    app.exec()
