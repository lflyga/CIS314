"""
Author: L. Flygare
Description: will ask user for input, populate a new window in the same position of the previous window when terminated
                and show input and ask user to confirm it is correct, if user responds no, process will repeat until 
                user confirms input as correct
"""
# python -m pip install PyQt6 <- run in terminal if PyQt6 not recognized

import sys
from PyQt6.QtWidgets import QApplication, QDialog, QLabel, QTextEdit, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt

class InputBox(QDialog):
    """dialog box to collect user text input"""
    def __init__(self, start_position = None, parent = None):
        super().__init__(parent)

        self.setWindowTitle("Enter Your Text")

        #create widgets
        self.label = QLabel("What is the answer to the Ulitmate Question of Life, the Universe, and Everything?")
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Enter response here")
        self.submit_button = QPushButton("Submit")
        self.cancel_button = QPushButton("Cancel")

        #button layouts
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.submit_button)
        button_layout.addWidget(self.cancel_button)

        #box layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.label)
        main_layout.addWidget(self.text_edit)
        main_layout.addLayout(button_layout)

        #setting layout
        self.setLayout(main_layout)

        #button actions
        self.submit_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        #restore position of previous window (if applicable)
        if start_position is not None:
            self.move(start_position)

    def get_text(self):
        return self.text_edit.toPlainText().strip()
    

class ConfirmBox(QDialog):
    """dialog box to confirm user input"""
    def __init__(self, text, start_position = None, parent = None):
        super().__init__(parent)

        self.setWindowTitle("Confirm Your Text")

        #create widgets
        self.label = QLabel("Please confirm this text is correct: ")
        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)
        self.text_display.setPlainText(text)
        self.yes_button = QPushButton("Yes, it is correct")
        self.no_button = QPushButton("No, let me correct it")

        #button layouts
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.yes_button)
        button_layout.addWidget(self.no_button)

        #box layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.label)
        main_layout.addWidget(self.text_display)
        main_layout.addLayout(button_layout)
        
        #setting layout
        self.setLayout(main_layout)

        #button actions
        self.yes_button.clicked.connect(self.accept)
        self.no_button.clicked.connect(self.reject)

        #restore position of previous window (if applicable)
        if start_position is not None:
            self.move(start_position)

    
def main():
    app = QApplication(sys.argv)

    last_position = None

    while True:
        #asks for input
        input_box = InputBox(start_position = last_position)
        result = input_box.exec()

        #exits if user cancels input
        if result != QDialog.DialogCode.Accepted:
            sys.exit(0)

        #save position of box when closed
        last_position = input_box.frameGeometry().topLeft()
        user_text = input_box.get_text()

        #show confirmation box
        confirm_box = ConfirmBox(text = user_text, start_position = last_position)
        confirm_result = confirm_box.exec()

        #update position with position of current box when closed
        last_position = confirm_box.frameGeometry().topLeft()

        if confirm_result == QDialog.DialogCode.Accepted:
            if user_text.strip() == "42":
                surprise = QDialog()
                surprise.setWindowTitle("Surprise!!!")
                msg = QLabel("You have discovered the meaning of life faster than a super computer!")
                ok = QPushButton("Why yes, I am super smart and amazing!")

                layout = QVBoxLayout()
                layout.addWidget(msg)
                layout.addWidget(ok)
                surprise.setLayout(layout)

                ok.clicked.connect(surprise.accept)

                surprise.move(last_position)
                surprise.exec()
            else:
                interesting = QDialog()
                interesting.setWindowTitle("How Interesting")
                msg = QLabel("What wise ponderings you have presented.")
                ok = QPushButton("I am quite the thinker.")

                layout = QVBoxLayout()
                layout.addWidget(msg)
                layout.addWidget(ok)
                interesting.setLayout(layout)

                ok.clicked.connect(interesting.accept)

                interesting.move(last_position)
                interesting.exec()
            break
        else:
            continue

    sys.exit(0)


if __name__ == "__main__":
    main()

    