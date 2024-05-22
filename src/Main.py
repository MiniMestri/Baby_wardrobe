import os
from kivy.app import App
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.core.window import Window

from database import add_user, validate_user
import sqlite3


Window.size = (375, 667)
class ImageButton(ButtonBehavior, Image):
    pass

class LoginScreen(Screen):
    pass

class RegisterScreen(Screen):
    pass

class WardrobeScreen(Screen):
    pass

class HomeScreen(Screen):
    pass
class MesureScreen(Screen):
    pass
class AccountScreen(Screen):
    pass

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

class BabyWardrobeApp(App):
    def build(self):
        self.assets_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets', 'iconos'))
        Builder.load_file('babywardrobe.kv')
        sm = WindowManager()
        #sm.add_widget(LoginScreen(name='login'))
        #sm.add_widget(RegisterScreen(name='register'))
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(WardrobeScreen(name='wardrobe'))
        sm.add_widget(MesureScreen(name='mesure'))
        sm.add_widget(AccountScreen(name='account'))
        return sm

    def get_image_path(self, filename):
        return os.path.join(self.assets_dir, filename)

if __name__ == '__main__':
    BabyWardrobeApp().run()
