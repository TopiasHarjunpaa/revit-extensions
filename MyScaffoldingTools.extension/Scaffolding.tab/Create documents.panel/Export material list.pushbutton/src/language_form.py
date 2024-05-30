import clr
import System

clr.AddReference("System")
clr.AddReference("System.Windows.Forms")
clr.AddReference("System.Drawing")

from System.Windows.Forms import Form, RadioButton, Button
from System.Drawing import Point, Size

class LanguageForm(Form):
    def __init__(self, languages=["FIN", "ENG", "SWE"]):
        self.languages = languages
        self.selected_language = None
        self.InitializeComponent()
    
    def InitializeComponent(self):
        self.Text = "Select Language"
        self.ClientSize = Size(300, 150)
        self.FormBorderStyle = System.Windows.Forms.FormBorderStyle.FixedDialog
        self.MaximizeBox = False
        self.MinimizeBox = False
        self.StartPosition = System.Windows.Forms.FormStartPosition.CenterScreen

        self.radio_buttons = []
        for index, lang in enumerate(self.languages):
            radio_button = RadioButton()
            radio_button.Text = lang
            radio_button.Location = Point(10, 20 + 30 * index)
            radio_button.Checked = (index == 0)
            self.Controls.Add(radio_button)
            self.radio_buttons.append(radio_button)

        self.btnCalculate = Button()
        self.btnCalculate.Text = "Calculate"
        self.btnCalculate.Location = Point(150, 110)
        self.btnCalculate.Click += self.on_calculate
        self.Controls.Add(self.btnCalculate)

        self.btnCancel = Button()
        self.btnCancel.Text = "Cancel"
        self.btnCancel.Location = Point(50, 110)
        self.btnCancel.Click += self.on_cancel
        self.Controls.Add(self.btnCancel)
    
    def get_main_language(self):
        return self.selected_language

    def on_calculate(self, sender, event):
        for radio_button in self.radio_buttons:
            if radio_button.Checked:
                self.selected_language = radio_button.Text
                break
        self.Close()

    def on_cancel(self, sender, event):
        self.selected_language = None
        self.Close()