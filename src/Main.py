import os
from kivy.app import App
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout

from database import add_user, validate_user, change_password,save_measurements,get_existing_names,save_measurements_clothing,get_existing_names, add_wardrobe, get_wardrobes
import sqlite3


Window.size = (375, 667)
class ImageButton(ButtonBehavior, Image):
    pass

class LoginScreen(Screen):
    pass

class RegisterScreen(Screen):
    pass

class WardrobeScreen(Screen):
    def on_pre_enter(self, *args):
        username = self.manager.get_screen('login').ids.username.text
        self.display_wardrobes(username)

    def display_wardrobes(self, username):
        self.ids.wardrobe_grid.clear_widgets()
        wardrobes = get_wardrobes(username)
        for wardrobe in wardrobes:
            btn = Button(text=wardrobe, size_hint_y=None, height=40)
            btn.bind(on_press=self.select_wardrobe)
            self.ids.wardrobe_grid.add_widget(btn)
        
        add_wardrobe_btn = Button(text='Añadir Nuevo Armario', size_hint_y=None, height=40)
        add_wardrobe_btn.bind(on_press=self.show_add_wardrobe_popup)
        self.ids.wardrobe_grid.add_widget(add_wardrobe_btn)

    def select_wardrobe(self, instance):
        print(f"Armario seleccionado: {instance.text}")
        # Aquí puedes agregar la lógica para manejar la selección de un armario

    def show_add_wardrobe_popup(self, instance):
        content = BoxLayout(orientation='vertical', padding=10)
        text_input = TextInput(hint_text='Nombre del nuevo armario', multiline=False)
        content.add_widget(text_input)
        content.add_widget(Button(text='Guardar', size_hint_y=None, height=40, on_press=lambda x: self.add_wardrobe(text_input.text)))
        popup = Popup(title='Añadir Nuevo Armario', content=content, size_hint=(None, None), size=(300, 200))
        popup.open()

    def add_wardrobe(self, wardrobe_name):
        username = self.manager.get_screen('login').ids.username.text
        add_wardrobe(username, wardrobe_name)
        self.display_wardrobes(username)

class HomeScreen(Screen):
    pass
class MesureScreen(Screen):
    def on_spinner_select(self, text):
        self.ids.height.disabled = True
        self.ids.chest_circumference.disabled = True
        self.ids.waist_circumference.disabled = True
        self.ids.torso_length.disabled = True
        self.ids.leg_length.disabled = True

        if text == 'Body':
            self.ids.height.disabled = False
            self.ids.chest_circumference.disabled = False
            self.ids.torso_length.disabled = False
        elif text == 'Buzos':
            self.ids.height.disabled = False
            self.ids.chest_circumference.disabled = False
        elif text == 'Cubrepañales':
            self.ids.waist_circumference.disabled = False
            self.ids.leg_length.disabled = False
        elif text == 'Vestidos':
            self.ids.height.disabled = False
            self.ids.chest_circumference.disabled = False
            self.ids.torso_length.disabled = False
        elif text == 'Jesusitos':
            self.ids.height.disabled = False
            self.ids.chest_circumference.disabled = False
            self.ids.torso_length.disabled = False
            self.ids.waist_circumference.disabled = False
        elif text == 'Peleles':
            self.ids.height.disabled = False
            self.ids.chest_circumference.disabled = False
            self.ids.torso_length.disabled = False
            self.ids.leg_length.disabled = False
        elif text == 'Petos':
            self.ids.height.disabled = False
            self.ids.chest_circumference.disabled = False
            self.ids.torso_length.disabled = False
            self.ids.leg_length.disabled = False
        elif text == 'Ranitas':
            self.ids.height.disabled = False
            self.ids.chest_circumference.disabled = False
            self.ids.torso_length.disabled = False

    def save_measurements(self, clothing_type, height, chest_circumference, waist_circumference, torso_length, leg_length):
        save_measurements_clothing(clothing_type, height, chest_circumference, waist_circumference, torso_length, leg_length)
        popup = Popup(title='Medidas Guardadas',
                      content=Label(text='Las medidas han sido guardadas correctamente'),
                      size_hint=(None, None), size=(400, 400))
        popup.open()

class AccountScreen(Screen):
    pass



class ChangePasswordScreen(Screen):
    def change_password(self, username, old_password, new_password):
        if change_password(username, old_password, new_password):
            popup = Popup(title='Cambio Exitoso',
                          content=Label(text='Contraseña cambiada correctamente'),
                          size_hint=(None, None), size=(400, 400))
            popup.open()
            self.manager.current = 'account'
        else:
            popup = Popup(title='Error',
                          content=Label(text='Usuario o contraseña incorrectos'),
                          size_hint=(None, None), size=(400, 400))
            popup.open()

class BabyMeasurementsScreen(Screen):
    def on_pre_enter(self, *args):
        self.ids.spinner_name.values = get_existing_names() + ["Nuevo"]
        self.ids.spinner_name.text = "Seleccionar o Nuevo"

    def save_measurements(self, selected_name, new_name, height, chest_circumference, waist_circumference, torso_length, leg_length):
        username = new_name if selected_name == "Nuevo" else selected_name
        save_measurements(username, height, chest_circumference, waist_circumference, torso_length, leg_length)
        popup = Popup(title='Medidas Guardadas',
                      content=Label(text='Las medidas del bebé han sido guardadas correctamente'),
                      size_hint=(None, None), size=(400, 400))
        popup.open()
        self.manager.current = 'account'

    def on_spinner_select(self, text):
        if text == "Nuevo":
            self.ids.new_name.disabled = False
        else:
            self.ids.new_name.disabled = True
class WindowManager(ScreenManager):
    def login(self, username, password):
        if validate_user(username, password):
            self.current = 'home'
        else:
            popup = Popup(title='Error de Inicio de Sesión',
                          content=Label(text='Nombre de usuario o contraseña incorrectos'),
                          size_hint=(None, None), size=(400, 400))
            popup.open()

    def register(self, username, password):
        try:
            add_user(username, password)
            popup = Popup(title='Registro Exitoso',
                          content=Label(text='Usuario registrado correctamente'),
                          size_hint=(None, None), size=(400, 400))
            popup.open()
            self.current = 'login'
        except sqlite3.IntegrityError:
            popup = Popup(title='Error de Registro',
                          content=Label(text='El nombre de usuario ya existe'),
                          size_hint=(None, None), size=(400, 400))
            popup.open()

    def logout(self):
        App.get_running_app().stop()

class BabyWardrobeApp(App):
    def build(self):
        self.assets_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets', 'iconos'))
        Builder.load_file('babywardrobe.kv')
        sm = WindowManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(RegisterScreen(name='register'))
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(WardrobeScreen(name='wardrobe'))
        sm.add_widget(MesureScreen(name='mesure'))
        sm.add_widget(AccountScreen(name='account'))
        sm.add_widget(ChangePasswordScreen(name='change_password'))
        sm.add_widget(BabyMeasurementsScreen(name='baby_measurements'))
        return sm

    def get_image_path(self, filename):
        return os.path.join(self.assets_dir, filename)

if __name__ == '__main__':
    BabyWardrobeApp().run()
