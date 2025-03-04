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
        self.manager.current = "intro"

class IntroScreen(Screen):
    def __init__(self, **kwargs):
        super(IntroScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        self.welcome_label = Label(text="", font_size='40sp', color=(0.8, 0.8, 0.8, 1))
        self.layout.add_widget(self.welcome_label)

        info_label = Label(
            text="Type in DNA and the app will analyze it for you.",
            font_size='20sp',
            color=(0.8, 0.8, 0.8, 1)
        )
        self.layout.add_widget(info_label)

        start_button = Button(
            text="Start",
            font_size='18sp',
            size_hint_y=None,
            height=50,
            background_color=(0.8, 0.6, 0.2, 1)
        )
        start_button.bind(on_press=self.start_app)
        self.layout.add_widget(start_button)

        self.add_widget(self.layout)

    def on_enter(self, *args):
        if self.manager.user_gender == "Male":
            title = "Mister"
        elif self.manager.user_gender == "Female":
            title = "Miss"

        if self.manager.user_gender in ["Male", "Female"]:
            self.welcome_label.text = (
                f"{title} {self.manager.user_name}\n"
                f"Welcome to Kodinator!"
            )
        else:
            self.welcome_label.text = (
                f"Creature known as '{self.manager.user_gender}'\n"
                f"Welcome to Kodinator!"
            )
            
        super().on_enter(*args)

    def start_app(self, instance):
        self.manager.current = "input_screen"

class InputScreen(Screen):
    def __init__(self, **kwargs):
        super(InputScreen, self).__init__(**kwargs)
        layout = GridLayout(cols=1, padding=[10, 10, 10, 10], spacing=10)
        
        greeting_label = Label(text="Enter DNA sequences Below:", font_size='40sp', color=(0.8, 0.8, 0.8, 1))
        layout.add_widget(greeting_label)
        
        self.result_label = Label(text="", font_size='20sp', color=(0.8, 0.8, 0.8, 1))
        layout.add_widget(self.result_label)
        
        self.protein_label = Label(text="", font_size='20sp', color=(0.8, 0.8, 0.8, 1))
        layout.add_widget(self.protein_label)

        self.text_input = TextInput(multiline=False, font_size='18sp', size_hint_y=None, height=40,
                                    background_color=(0.2, 0.2, 0.2, 1))
        layout.add_widget(self.text_input)
        
        self.print_button = Button(text="Print Text", font_size='18sp', size_hint_y=None, height=50,
        background_color=(0.8, 0.6, 0.2, 1))
        
        self.print_button.bind(on_press=self.print_text)
        layout.add_widget(self.print_button)
        
        self.add_widget(layout)
    
    def print_text(self, instance):
        print("User Name:", self.manager.user_name)
        print("User Gender:", self.manager.user_gender)
        
        txt = list(self.text_input.text)
        solved = ""

        codon_table = {
            'UUU': 'Phenylalanine', 'UUC': 'Phenylalanine', 'UUA': 'Leucine', 'UUG': 'Leucine',
            'UCU': 'Serine', 'UCC': 'Serine', 'UCA': 'Serine', 'UCG': 'Serine',
            'UAU': 'Tyrosine', 'UAC': 'Tyrosine', 'UAA': 'STOP', 'UAG': 'STOP',
            'UGU': 'Cysteine', 'UGC': 'Cysteine', 'UGA': 'STOP', 'UGG': 'Tryptophan',
            'CUU': 'Leucine', 'CUC': 'Leucine', 'CUA': 'Leucine', 'CUG': 'Leucine',
            'CCU': 'Proline', 'CCC': 'Proline', 'CCA': 'Proline', 'CCG': 'Proline',
            'CAU': 'Histidine', 'CAC': 'Histidine', 'CAA': 'Glutamine', 'CAG': 'Glutamine',
            'CGU': 'Arginine', 'CGC': 'Arginine', 'CGA': 'Arginine', 'CGG': 'Arginine',
            'AUU': 'Isoleucine', 'AUC': 'Isoleucine', 'AUA': 'Isoleucine', 'AUG': 'Methionine',
            'ACU': 'Threonine', 'ACC': 'Threonine', 'ACA': 'Threonine', 'ACG': 'Threonine',
            'AAU': 'Asparagine', 'AAC': 'Asparagine', 'AAA': 'Lysine', 'AAG': 'Lysine',
            'AGU': 'Serine', 'AGC': 'Serine', 'AGA': 'Arginine', 'AGG': 'Arginine',
            'GUU': 'Valine', 'GUC': 'Valine', 'GUA': 'Valine', 'GUG': 'Valine',
            'GCU': 'Alanine', 'GCC': 'Alanine', 'GCA': 'Alanine', 'GCG': 'Alanine',
            'GAU': 'Aspartic acid', 'GAC': 'Aspartic acid', 'GAA': 'Glutamic acid', 'GAG': 'Glutamic acid',}
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
                self.result_label.text = "Wrong letter"
                return False

        # Continue processing if all characters are valid

        self.result_label.text = f"mRNA: {solved}"

        # Decode codons
        codons = [solved[i:i+3] for i in range(0, len(solved), 3)]
        protein = []
        has_stop_codon = False
        
        for codon in codons:
            if len(codon) < 3:
                # Skip incomplete codons at the end
                continue
            if codon in codon_table:
                amino_acid = codon_table[codon]
                if amino_acid == "STOP":
                    has_stop_codon = True
                    break
                protein.append(amino_acid)
            else:
                self.result_label.text = "Invalid codon sequence"
                return False

        if protein:
            self.protein_label.text = f"Protein: {'-'.join(protein)}"
        else:
            if has_stop_codon:
                self.protein_label.text = "Protein: None (sequence contains only STOP codon)"
            else:
                self.protein_label.text = "Protein: None"

class MyApp(App):
    def build(self):
        sm = ScreenManager()
        # Create shared variables for name and gender.
        sm.user_name = ""
        sm.user_gender = ""
        sm.add_widget(WelcomeScreen(name="welcome"))
        sm.add_widget(IntroScreen(name="intro"))
        sm.add_widget(InputScreen(name="input_screen"))
        sm.current = "welcome"
        return sm

if __name__ == "__main__":
    MyApp().run()

# Requirements:
# pip install kivy