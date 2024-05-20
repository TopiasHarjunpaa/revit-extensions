# -*- coding: utf-8 -*-

import clr
clr.AddReference("System.Windows.Forms")
clr.AddReference("System.Drawing")

from System.Windows.Forms import Form, Label, TextBox, Button, DialogResult, MessageBox, RadioButton, GroupBox
from System.Drawing import Point, Size

class InputForm(Form):
    def __init__(self):
        self.Text = "Calculate Load Information"
        self.Size = Size(530, 550)

        labels = [
            ["A1", "National Annex", ["FIN", "ENG", "SWE"]],
            ["A2", "Imposed load (kg/m2)", "150"],
            ["A3", "Snow load (kg/m2)", "25"],
            ["A4", "Consequence class", ["CC1", "CC2", "CC3"]],
            ["B1", "Fundamental basic wind velocity (m/s)", "21"],
            ["B2", "Select terrain category", ["0", "I", "II", "III", "IV"]],
            ["B3", "Return period (years)", "5"],
            ["B4", "Seasonal factor", "1"],
            ["B5", "Orography factor", "1"],
            ["C1", "Building height (m)", "20"],
            ["C2", "Roof width (mm)", "32500"],
            ["C3", "Bay length (mm)", "2572"],
            ["C4", "Roof angle (°)", "18"],
        ]

        self.text_boxes = {}
        self.radio_buttons = {}
        y_offset = 40

        for label_info in labels:
            if len(label_info) == 3:
                label = Label()
                label.Text = "{}. {}".format(label_info[0], label_info[1])
                label.AutoSize = True
                label.MaximumSize = Size(300, 0)
                label.Location = Point(30, y_offset)
                self.Controls.Add(label)

                if isinstance(label_info[2], list):
                    group_box = GroupBox()
                    group_box.Text = ""
                    group_box.Location = Point(300, y_offset - 10)
                    group_box.Size = Size(180, 30)
                    self.Controls.Add(group_box)
                    x_offset = 10
                    self.radio_buttons[label_info[0]] = []
                    
                    for idx, option in enumerate(label_info[2]):
                        radio_button = RadioButton()
                        radio_button.Text = option
                        radio_button.AutoSize = True
                        radio_button.Location = Point(x_offset, 10)
                        group_box.Controls.Add(radio_button)
                        self.radio_buttons[label_info[0]].append(radio_button)
                        
                        if idx == 0:
                            radio_button.Checked = True
                        
                        if len(label_info[2]) == 3:
                            x_offset += 60

                        else:
                            x_offset += 33
                        
                else:
                    textbox = TextBox()
                    textbox.Location = Point(300, y_offset)
                    textbox.Size = Size(180, 30)
                    textbox.Text = label_info[2]
                    self.Controls.Add(textbox)
                    self.text_boxes[label_info[0]] = textbox

                y_offset += 30

        y_offset += 20

        self.ok_button = Button()
        self.ok_button.Text = "Calculate"
        self.ok_button.Location = Point(175, y_offset)
        self.ok_button.Click += self.ok_button_click
        self.Controls.Add(self.ok_button)

        self.cancel_button = Button()
        self.cancel_button.Text = "Cancel"
        self.cancel_button.Location = Point(260, y_offset)
        self.cancel_button.Click += self.cancel_button_click
        self.Controls.Add(self.cancel_button)

    def ok_button_click(self, sender, event):
        self.DialogResult = DialogResult.OK
        self.Close()

    def cancel_button_click(self, sender, event):
        self.DialogResult = DialogResult.Cancel
        self.Close()

def show_input_form():
    form = InputForm()
    result = form.ShowDialog()
    if result == DialogResult.OK:
        input_values = {}
        
        for label, text_box in form.text_boxes.items():
            value = validate_text_input(label, text_box.Text)
            
            if value is None:
                MessageBox.Show("Invalid input for {}. Please enter a valid number.".format(label), "Invalid Input")
                return None

            input_values[label] = value
        
        for label, radio_buttons in form.radio_buttons.items():
            for radio_button in radio_buttons:
                if radio_button.Checked:
                    value = convert_radio_button_values(label, radio_button.Text)
                    input_values[label] = value
                    break
        
        return input_values
    else:
        return None

def convert_radio_button_values(key, input_str):
        mapping = {
            "A1": {"FIN": 1, "ENG": 2, "SWE": 3},
            "A4": {"CC1": 1, "CC2": 2, "CC3": 3},
            "B2": {"0": 0, "I": 1, "II": 2, "III": 3, "IV": 4}
        }

        return mapping[key][input_str]

def validate_text_input(key, input_str):
    input_str = input_str.replace(",", ".")

    try:
        if key in ["A2", "A3", "B1", "B3"]:
            value = int(float(input_str))
            if value >= 0:
                return value
            else:
                return None
        else:
            value = float(input_str)
            if value >= 0.0:
                return value
            else:
                return None
    except (ValueError, KeyError):
        return None