from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.core.window import Window

# Set the background color
Window.clearcolor = (0.1, 0.1, 0.1, 1)

class InputScreen(GridLayout):

    def __init__(self, **kwargs):
        super(InputScreen, self).__init__(**kwargs)
        self.cols = 1
        self.padding = [10, 10, 10, 10]
        self.spacing = 10

        self.add_widget(Label(text="Enter Text Below:", font_size='20sp', color=(0.8, 0.8, 0.8, 1)))
        
        self.text_input = TextInput(multiline=False, font_size='18sp', size_hint_y=None, height=40)
        self.add_widget(self.text_input)
        self.text_input.background_color = (0.2, 0.2, 0.2, 1)
        
        self.print_button = Button(text="Print Text", font_size='18sp', size_hint_y=None, height=50, background_color=(0.8, 0.6, 0.2, 1))
        self.print_button.bind(on_press=self.print_text)
        self.add_widget(self.print_button)

    def print_text(self, instance):
        print(self.text_input.text)


class MyApp(App):

    def build(self):
        return InputScreen()


if __name__ == "__main__":
    MyApp().run()