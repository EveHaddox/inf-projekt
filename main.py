import string
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window

# Set the background color
Window.clearcolor = (0.1, 0.1, 0.1, 1)

class WelcomeScreen(Screen):
    def __init__(self, **kwargs):
        super(WelcomeScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Name input
        name_label = Label(text="Enter Your Name:", font_size='20sp', color=(0.8, 0.8, 0.8, 1))
        self.layout.add_widget(name_label)
        
        self.name_input = TextInput(multiline=False, font_size='18sp', size_hint_y=None, height=40,
                                    background_color=(0.2, 0.2, 0.2, 1))
        self.layout.add_widget(self.name_input)
        
        # Gender selection
        gender_label = Label(text="Select Your Gender:", font_size='20sp', color=(0.8, 0.8, 0.8, 1))
        self.layout.add_widget(gender_label)
        
        self.gender_spinner = Spinner(
            text="Select",
            values=["Male", "Female", "Other"],
            size_hint_y=None,
            height=40
        )
        self.gender_spinner.bind(text=self.on_gender_change)
        self.layout.add_widget(self.gender_spinner)
        
        # Additional input if "Other" is selected.
        self.other_gender_input = TextInput(multiline=False, font_size='18sp', size_hint_y=None, height=40,
                                          background_color=(0.2, 0.2, 0.2, 1),
                                          hint_text="Enter your gender")
        # Initially hidden
        self.other_gender_input.opacity = 0
        self.other_gender_input.disabled = True
        self.layout.add_widget(self.other_gender_input)
        
        # Start button
        start_button = Button(text="Start", font_size='18sp', size_hint_y=None, height=50,
                              background_color=(0.8, 0.6, 0.2, 1))
        start_button.bind(on_press=self.start_app)
        self.layout.add_widget(start_button)
        
        self.add_widget(self.layout)
    
    def on_gender_change(self, spinner, text):
        if text == "Other":
            self.other_gender_input.opacity = 1
            self.other_gender_input.disabled = False
        else:
            self.other_gender_input.opacity = 0
            self.other_gender_input.disabled = True

    def start_app(self, instance):
        # Save the name and gender into the screen manager for use in other screens.
        self.manager.user_name = self.name_input.text.strip()
        if self.gender_spinner.text == "Other":
            self.manager.user_gender = self.other_gender_input.text.strip()
        else:
            self.manager.user_gender = self.gender_spinner.text
        self.manager.current = "input_screen"

class InputScreen(Screen):
    def __init__(self, **kwargs):
        super(InputScreen, self).__init__(**kwargs)
        layout = GridLayout(cols=1, padding=[10, 10, 10, 10], spacing=10)
        
        greeting_label = Label(text="Enter Text Below:", font_size='20sp', color=(0.8, 0.8, 0.8, 1))
        layout.add_widget(greeting_label)
        
        self.text_input = TextInput(multiline=False, font_size='18sp', size_hint_y=None, height=40,
                                    background_color=(0.2, 0.2, 0.2, 1))
        layout.add_widget(self.text_input)
        
        self.print_button = Button(text="Print Text", font_size='18sp', size_hint_y=None, height=50,
                                   background_color=(0.8, 0.6, 0.2, 1))
        self.print_button.bind(on_press=self.print_text)
        layout.add_widget(self.print_button)
        
        self.add_widget(layout)
    
    def print_text(self, instance):
        # Output the name and gender along with the processed text.
        print("User Name:", self.manager.user_name)
        print("User Gender:", self.manager.user_gender)
        
        txt = list(self.text_input.text)
        solved = ""
        for x in txt:
            x = x.capitalize()
            if x == "A":
                solved += "U"
            elif x == "T":
                solved += "A"
            elif x == "C":
                solved += "G"
            elif x == "G":
                solved += "C"
            else:
                print("wrong letter")
                return False
        print(solved)

class MyApp(App):
    def build(self):
        sm = ScreenManager()
        # Create shared variables for name and gender.
        sm.user_name = ""
        sm.user_gender = ""
        sm.add_widget(WelcomeScreen(name="welcome"))
        sm.add_widget(InputScreen(name="input_screen"))
        sm.current = "welcome"
        return sm

if __name__ == "__main__":
    MyApp().run()

# Requirements:
# pip install kivy