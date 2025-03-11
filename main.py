#import string  # Removed unused import
import base64
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.core.clipboard import Clipboard

# RSA encryption imports from PyCryptodome
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

# bg color
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
    
    def on_gender_change(self, _, text):
        if text == "Other":
            self.other_gender_input.opacity = 1
            self.other_gender_input.disabled = False
        else:
            self.other_gender_input.opacity = 0
            self.other_gender_input.disabled = True

    def start_app(self, _):
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

        # Button to show private key
        private_key_button = Button(
            text="Copy Private Key",
            font_size='18sp',
            size_hint_y=None,
            height=50,
            background_color=(0.8, 0.6, 0.2, 1)
        )
        private_key_button.bind(on_press=self.show_private_key)
        self.layout.add_widget(private_key_button)

        # Label to display private key (initially empty)
        self.private_key_label = Label(text="", font_size='12sp', color=(0.8, 0.8, 0.8, 1))
        self.layout.add_widget(self.private_key_label)

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

    def start_app(self, _):
        self.manager.current = "input_screen"

    def show_private_key(self, _):
        # Show PEM formatted private key
        private_key_pem = self.manager.rsa_key.export_key().decode("utf-8")
        Clipboard.copy(private_key_pem)
        self.private_key_label.text = "Private key copied to clipboard."


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
        
        self.print_button = Button(text="Solve", font_size='18sp', size_hint_y=None, height=50,
                                     background_color=(0.8, 0.6, 0.2, 1))
        self.print_button.bind(on_press=self.print_text)
        layout.add_widget(self.print_button)
        
        # Button to copy the encrypted mRNA solution
        self.copy_button = Button(text="Copy Encrypted", font_size='18sp', size_hint_y=None, height=50,
                                    background_color=(0.8, 0.6, 0.2, 1))
        self.copy_button.bind(on_press=self.copy_encrypted)
        layout.add_widget(self.copy_button)
        
        self.add_widget(layout)
    
    def print_text(self, _):
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
            'GAU': 'Aspartic acid', 'GAC': 'Aspartic acid', 'GAA': 'Glutamic acid', 'GAG': 'Glutamic acid',
        }
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

        self.result_label.text = f"mRNA: {solved}"

        # Decode codons
        codons = [solved[i:i+3] for i in range(0, len(solved), 3)]
        protein = []
        has_stop_codon = False
        
        for codon in codons:
            if len(codon) < 3:
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
    
    def copy_encrypted(self, _):
        if not self.result_label.text.startswith("mRNA:"):
            self.result_label.text = "No mRNA result to encrypt"
            return
        mRNA = self.result_label.text[len("mRNA:"):].strip()
        try:
            encrypted = self.manager.public_cipher.encrypt(mRNA.encode("utf-8"))
        except ValueError as e:
            self.result_label.text = f"Encryption error: {str(e)}"
            return
        encrypted_b64 = base64.b64encode(encrypted).decode("utf-8")
        Clipboard.copy(encrypted_b64)
        self.result_label.text += "\n[Encrypted solution copied]"

class MyApp(App):
    def build(self):
        sm = ScreenManager()
        sm.user_name = ""
        sm.user_gender = ""
        # Generate RSA key pair once and store in the ScreenManager.
        sm.rsa_key = RSA.generate(2048)
        sm.public_cipher = PKCS1_OAEP.new(sm.rsa_key.publickey())
        sm.private_cipher = PKCS1_OAEP.new(sm.rsa_key)
        
        sm.add_widget(WelcomeScreen(name="welcome"))
        sm.add_widget(IntroScreen(name="intro"))
        sm.add_widget(InputScreen(name="input_screen"))
        sm.current = "welcome"
        return sm

if __name__ == "__main__":
    MyApp().run()