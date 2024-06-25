# -*- coding: utf-8 -*-

import clr
clr.AddReference("System.Windows.Forms")
clr.AddReference("System.Drawing")

from System.Windows.Forms import Form, Label, TextBox, Button, DialogResult, CheckBox, MessageBox, Screen
from System.Drawing import Point, Size


class BayForm(Form):
    def __init__(self):
        self.Text = "Find bays"

        form_height = Screen.PrimaryScreen.Bounds.Height * 0.5
        form_width = form_height * 0.6
        self.Size = Size(int(form_width), int(form_height))

        labels = [
            ("Bay: 0,154 m", True),
            ("Bay: 0,390 m", True),
            ("Bay: 0,450 m", True),
            ("Bay: 0,732 m", True),
            ("Bay: 1,088 m", True),
            ("Bay: 1,400 m", True),
            ("Bay: 1,572 m", True),
            ("Bay: 2,072 m", True),
            ("Bay: 2,572 m", True),
            ("Bay: 3,072 m", False),
        ]

        self.check_boxes = []
        y_offset = form_height / 25

        for label_text, default_value in labels:
            label = Label()
            label.Text = label_text
            label.AutoSize = True
            label.Location = Point(form_width / 25, y_offset)
            self.Controls.Add(label)

            checkbox = CheckBox()
            checkbox.Location = Point(form_width / 2, y_offset)
            checkbox.Checked = default_value
            self.Controls.Add(checkbox)
            self.check_boxes.append(checkbox)
            
            y_offset += form_height / 15

        targeted_distance_label = Label()
        targeted_distance_label.Text = "Targeted distance"
        targeted_distance_label.AutoSize = True
        targeted_distance_label.Location = Point(form_width / 25, y_offset)
        self.Controls.Add(targeted_distance_label)

        self.targeted_distance_textbox = TextBox()
        self.targeted_distance_textbox.Location = Point(form_width / 2, y_offset)
        self.targeted_distance_textbox.Size = Size(form_width / 4, y_offset)
        self.targeted_distance_textbox.Text = "30000"
        self.Controls.Add(self.targeted_distance_textbox)
        
        y_offset += form_height / 15

        tolerance_label = Label()
        tolerance_label.Text = "Tolerance"
        tolerance_label.AutoSize = True
        tolerance_label.Location = Point(form_width / 25, y_offset)
        self.Controls.Add(tolerance_label)

        self.tolerance_textbox = TextBox()
        self.tolerance_textbox.Location = Point(form_width / 2, y_offset)
        self.tolerance_textbox.Size = Size(form_width / 4, y_offset)
        self.tolerance_textbox.Text = "100"
        self.Controls.Add(self.tolerance_textbox)
        
        y_offset += form_height / 12

        self.ok_button = Button()
        self.ok_button.Text = "OK"
        self.ok_button.Location = Point(form_width * 0.25, y_offset)
        self.ok_button.Size = Size(form_width * 0.2, form_height / 20)
        self.ok_button.Click += self.ok_button_click
        self.Controls.Add(self.ok_button)

        self.cancel_button = Button()
        self.cancel_button.Text = "Cancel"
        self.cancel_button.Location = Point(form_width * 0.55, y_offset)
        self.cancel_button.Size = Size(form_width * 0.2, form_height / 20)
        self.cancel_button.Click += self.cancel_button_click
        self.Controls.Add(self.cancel_button)

    def ok_button_click(self, sender, event):
        self.DialogResult = DialogResult.OK
        self.Close()

    def cancel_button_click(self, sender, event):
        self.DialogResult = DialogResult.Cancel
        self.Close()

def show_bay_form():
    form = BayForm()
    result = form.ShowDialog()
    if result == DialogResult.OK:
        distance = validate_text_input(form.targeted_distance_textbox.Text)
        tolerance = validate_text_input(form.tolerance_textbox.Text)

        if distance is None:
            MessageBox.Show("Invalid input for targeted distance. Please enter a valid number.") 
            return None

        if tolerance is None:
            MessageBox.Show("Invalid input for tolerance. Please enter a valid number.") 
            return None        

        bay_filters = [checkbox.Checked for checkbox in form.check_boxes]
        return distance, tolerance, bay_filters
    else:
        return None

def validate_text_input(input_str):
    input_str = input_str.replace(",", ".")
    
    try:
        value = int(float(input_str))

        if value >= 0:
            return value
        
        return None
    except (ValueError, KeyError):
        return None