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
from kivy.uix.widget import Widget

from database import add_user, validate_user, change_password,save_measurements,get_existing_names,save_measurements_clothing,get_existing_names, add_wardrobe, get_wardrobes,delete_wardrobe,get_wardrobe_count,get_latest_baby_measurements,get_clothing_count_per_wardrobe
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
            wardrobe_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
            btn = Button(text=wardrobe, size_hint_y=None, height=40)
            spacer = Widget(size_hint_x=None, width=10)
            delete_btn = Button(text='Eliminar', size_hint_y=None, height=40)
            delete_btn.bind(on_press=lambda x, w=wardrobe: self.delete_wardrobe(username, w))
            wardrobe_box.add_widget(btn)
            wardrobe_box.add_widget(spacer) 
            wardrobe_box.add_widget(delete_btn)
            self.ids.wardrobe_grid.add_widget(wardrobe_box)
        
        add_wardrobe_btn = Button(text='Añadir Nuevo Armario', size_hint_y=None, height=40)
        add_wardrobe_btn.bind(on_press=self.show_add_wardrobe_popup)
        self.ids.wardrobe_grid.add_widget(add_wardrobe_btn)

    def show_add_wardrobe_popup(self, instance):
        content = BoxLayout(orientation='vertical', padding=10)
        text_input = TextInput(hint_text='Nombre del nuevo armario', multiline=False)
        content.add_widget(text_input)
        save_button = Button(text='Guardar', size_hint_y=None, height=40, on_press=lambda x: self.add_wardrobe(text_input.text))
        content.add_widget(save_button)
        popup = Popup(title='Añadir Nuevo Armario', content=content, size_hint=(None, None), size=(300, 200))
        popup.open()
        self.popup = popup  # Guardar la referencia al popup para cerrarlo más tarde

    def add_wardrobe(self, wardrobe_name):
        if not wardrobe_name.strip():
            error_popup = Popup(title='Error', content=Label(text='El nombre del armario no puede estar vacío'), size_hint=(None, None), size=(300, 200))
            error_popup.open()
            return

        username = self.manager.get_screen('login').ids.username.text
        add_wardrobe(username, wardrobe_name)
        self.display_wardrobes(username)
        self.popup.dismiss()  # Cerrar el popup después de añadir el armario

    def delete_wardrobe(self, username, wardrobe_name):
        delete_wardrobe(username, wardrobe_name)
        self.display_wardrobes(username)

class HomeScreen(Screen):
    pass
class MesureScreen(Screen):
    def on_pre_enter(self, *args):
        self.update_wardrobe_spinner()

    def update_wardrobe_spinner(self):
        username = self.manager.get_screen('login').ids.username.text
        wardrobes = get_wardrobes(username)
        self.ids.wardrobe_spinner.values = wardrobes

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
        try:
            username = self.manager.get_screen('login').ids.username.text
            wardrobe = self.ids.wardrobe_spinner.text
            if not wardrobe or wardrobe == 'Seleccione un armario':
                raise ValueError("Por favor, seleccione un armario")

            if not clothing_type or clothing_type == 'Seleccionar prenda':
                raise ValueError("Por favor, seleccione un tipo de prenda")

            save_measurements_clothing(username, clothing_type, wardrobe, height, chest_circumference, waist_circumference, torso_length, leg_length)
            
            popup = Popup(title='Medidas Guardadas',
                          content=Label(text='Las medidas han sido guardadas correctamente'),
                          size_hint=(None, None), size=(400, 400))
            popup.open()
        except Exception as e:
            popup = Popup(title='Error',
                          content=Label(text=f'Ocurrió un error: {str(e)}'),
                          size_hint=(None, None), size=(400, 400))
            popup.open()

class AccountScreen(Screen):
    def display_account_info(self, username):
        wardrobe_count = get_wardrobe_count(username)
        clothing_counts = get_clothing_count_per_wardrobe(username)
        latest_measurements = get_latest_baby_measurements(username)

        info = f"Nombre de usuario: {username}\n\n"
        info += f"Número de armarios: {wardrobe_count}\n\n"
        info += "Número de prendas por armario:\n"
        for wardrobe, count in clothing_counts:
            info += f"{wardrobe}: {count}\n"
        
        info += "\nÚltimas medidas del bebé:\n"
        if latest_measurements:
            _, height, chest, waist, torso, leg = latest_measurements
            info += f"Altura: {height} cm\n"
            info += f"Circunferencia del pecho: {chest} cm\n"
            info += f"Circunferencia de la cintura: {waist} cm\n"
            info += f"Largo del torso: {torso} cm\n"
            info += f"Largo de la pierna: {leg} cm\n"
        else:
            info += "No hay medidas disponibles.\n"

        popup = Popup(title='Información de la cuenta',
                      content=Label(text=info),
                      size_hint=(None, None), size=(400, 400))
        popup.open()



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
        # Validar que todos los campos estén llenos
        if not all([selected_name, height, chest_circumference, waist_circumference, torso_length, leg_length]) or selected_name == "Seleccionar o Nuevo":
            popup = Popup(title='Error',
                          content=Label(text='Todos los campos deben estar llenos'),
                          size_hint=(None, None), size=(400, 400))
            popup.open()
            return

        username = self.manager.get_screen('login').ids.username.text  # Obtener el nombre de usuario del campo de inicio de sesión
        baby_name = new_name if selected_name == "Nuevo" else selected_name
        
        try:
            save_measurements(username, baby_name, height, chest_circumference, waist_circumference, torso_length, leg_length)
            popup = Popup(title='Medidas Guardadas',
                          content=Label(text='Las medidas del bebé han sido guardadas correctamente'),
                          size_hint=(None, None), size=(400, 400))
            popup.open()
            self.manager.current = 'mesure'
        except Exception as e:
            popup = Popup(title='Error',
                          content=Label(text=f'Ocurrió un error: {str(e)}'),
                          size_hint=(None, None), size=(400, 400))
            popup.open()

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
