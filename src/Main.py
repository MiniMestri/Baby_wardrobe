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
from kivy.properties import StringProperty
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.uix.filechooser import FileChooserListView
from PIL import Image as PILImage
import uuid



from database import get_all_clothes,update_clothing_details,get_clothes_by_category,get_clothing_info,delete_clothing_from_wardrobe,add_user, validate_user, change_password,save_measurements,get_existing_names,save_measurements_clothing,get_existing_names, add_wardrobe, get_wardrobes,delete_wardrobe,get_wardrobe_count,get_latest_baby_measurements,get_clothing_count_per_wardrobe,get_clothes_in_wardrobe
import sqlite3


Window.size = (375, 667)

IMAGE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),'..', 'assets')
PROCESS_IMAGES_DIR = os.path.join(IMAGE_DIR, 'process_images')

if not os.path.exists(PROCESS_IMAGES_DIR):
    os.makedirs(PROCESS_IMAGES_DIR)

class ImageButton(ButtonBehavior, Image):
    pass

class LoginScreen(Screen):
    pass

class RegisterScreen(Screen):
    pass

class ImageButton(ButtonBehavior, Image):
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
            btn.bind(on_press=lambda x, w=wardrobe: self.show_wardrobe_details(username, w))
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

    def show_wardrobe_details(self, username, wardrobe_name):
        self.manager.current_wardrobe = wardrobe_name
        self.manager.current = 'wardrobe_details'

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

class WardrobeDetailsScreen(Screen):
    def on_pre_enter(self, *args):
        self.display_clothes(self.manager.current_wardrobe)

    def display_clothes(self, wardrobe_name):
        self.ids.clothing_grid.clear_widgets()
        username = self.manager.get_screen('login').ids.username.text
        clothes = get_clothes_in_wardrobe(username, wardrobe_name)
        for clothing_id, clothing in clothes:
            clothing_info = get_clothing_info(clothing_id)
            image_path = clothing_info['image'] if clothing_info and clothing_info['image'] else 'default_image_path'
            img = ImageButton(source=image_path, size_hint_y=None, height=200)
            img.bind(on_press=lambda x, cid=clothing_id: self.edit_clothing(cid))
            self.ids.clothing_grid.add_widget(img)

    def edit_clothing(self, clothing_id):
        edit_screen = self.manager.get_screen('edit_clothing')
        edit_screen.clothing_id = clothing_id
        self.manager.previous_screen = 'wardrobe_details'
        self.manager.current = 'edit_clothing'




class HomeScreen(Screen):
    def show_category(self, category):
        self.manager.current_category = category
        self.manager.current = 'category_details'

    def on_pre_enter(self, *args):
        self.display_unfit_clothes()

    def display_unfit_clothes(self):
        self.ids.unfit_clothes_grid.clear_widgets()
        username = self.manager.get_screen('login').ids.username.text
        baby_measurements = get_latest_baby_measurements(username)
        
        if not baby_measurements:
            print("No baby measurements found")
            return

        print("Baby measurements found:", baby_measurements)
        _, baby_height, baby_chest, baby_waist, baby_torso, baby_leg = baby_measurements

        clothes = get_all_clothes(username)
        total_clothes = 0
        for clothing_id in clothes:
            clothing_info = get_clothing_info(clothing_id[0])
            if clothing_info:
                if (clothing_info['height'] and clothing_info['height'] < baby_height) or \
                   (clothing_info['chest_circumference'] and clothing_info['chest_circumference'] < baby_chest) or \
                   (clothing_info['waist_circumference'] and clothing_info['waist_circumference'] < baby_waist) or \
                   (clothing_info['torso_length'] and clothing_info['torso_length'] < baby_torso) or \
                   (clothing_info['leg_length'] and clothing_info['leg_length'] < baby_leg):
                    image_path = clothing_info['image'] if clothing_info['image'] else 'default_image_path'
                    img = ImageButton(source=image_path, size_hint=(None, None), size=(150, 150))
                    img.bind(on_press=lambda x, cid=clothing_id[0]: self.edit_clothing(cid))
                    self.ids.unfit_clothes_grid.add_widget(img)
                    total_clothes += 1
        
        self.ids.unfit_clothes_grid.width = total_clothes * 160  

    def edit_clothing(self, clothing_id):
        edit_screen = self.manager.get_screen('edit_clothing')
        edit_screen.clothing_id = clothing_id
        self.manager.previous_screen = 'home'
        self.manager.current = 'edit_clothing'

class CategoryDetailsScreen(Screen):
    def on_pre_enter(self, *args):
        self.display_category_items(self.manager.current_category)
        self.update_category_title(self.manager.current_category)

    def display_category_items(self, category):
        self.ids.category_grid.clear_widgets()
        username = self.manager.get_screen('login').ids.username.text
        clothes = get_clothes_by_category(username, category)
        for clothing_id, clothing in clothes:
            clothing_info = get_clothing_info(clothing_id)
            image_path = clothing_info['image'] if clothing_info else None
            if image_path and os.path.exists(image_path):
                img = ImageButton(source=image_path, size_hint_y=None, height=100, on_press=lambda x, cid=clothing_id: self.edit_clothing(cid))
            else:
                img = Button(text=clothing, size_hint_y=None, height=100)
                img.bind(on_press=lambda x, cid=clothing_id: self.edit_clothing(cid))
            self.ids.category_grid.add_widget(img)

    def update_category_title(self, category):
        self.ids.category_title.text = f'{category}'

    def edit_clothing(self, clothing_id):
        edit_screen = self.manager.get_screen('edit_clothing')
        edit_screen.clothing_id = clothing_id
        self.manager.previous_screen = 'category_details'
        self.manager.current = 'edit_clothing'



class EditClothingScreen(Screen):
    clothing_id = None
    temp_image_path = None

    def on_pre_enter(self):
        self.clear_measurement_widgets()
        self.load_clothing_details()

    def load_clothing_details(self):
        if self.clothing_id is not None:
            clothing_info = get_clothing_info(self.clothing_id)
            if clothing_info:
                self.ids.edit_type.text = clothing_info['type']
                self.ids.edit_custom_name.text = clothing_info['custom_name'] or ''
                self.ids.edit_image.source = clothing_info['image'] or ''
                self.ids.edit_height.text = str(clothing_info['height'])
                self.ids.edit_chest_circumference.text = str(clothing_info['chest_circumference'])
                self.ids.edit_waist_circumference.text = str(clothing_info['waist_circumference'])
                self.ids.edit_torso_length.text = str(clothing_info['torso_length'])
                self.ids.edit_leg_length.text = str(clothing_info['leg_length'])
                self.update_fields(clothing_info['type'])

    def update_fields(self, clothing_type):
        self.ids.edit_height.disabled = True
        self.ids.edit_chest_circumference.disabled = True
        self.ids.edit_waist_circumference.disabled = True
        self.ids.edit_torso_length.disabled = True
        self.ids.edit_leg_length.disabled = True

        if clothing_type == 'Body':
            self.ids.edit_height.disabled = False
            self.ids.edit_chest_circumference.disabled = False
            self.ids.edit_torso_length.disabled = False
        elif clothing_type == 'Buzos':
            self.ids.edit_height.disabled = False
            self.ids.edit_chest_circumference.disabled = False
        elif clothing_type == 'Cubrepañales':
            self.ids.edit_waist_circumference.disabled = False
            self.ids.edit_leg_length.disabled = False
        elif clothing_type == 'Vestidos':
            self.ids.edit_height.disabled = False
            self.ids.edit_chest_circumference.disabled = False
            self.ids.edit_torso_length.disabled = False
        elif clothing_type == 'Jesusitos':
            self.ids.edit_height.disabled = False
            self.ids.edit_chest_circumference.disabled = False
            self.ids.edit_torso_length.disabled = False
            self.ids.edit_waist_circumference.disabled = False
        elif clothing_type == 'Peleles':
            self.ids.edit_height.disabled = False
            self.ids.edit_chest_circumference.disabled = False
            self.ids.edit_torso_length.disabled = False
            self.ids.edit_leg_length.disabled = False
        elif clothing_type == 'Petos':
            self.ids.edit_height.disabled = False
            self.ids.edit_chest_circumference.disabled = False
            self.ids.edit_torso_length.disabled = False
            self.ids.edit_leg_length.disabled = False
        elif clothing_type == 'Ranitas':
            self.ids.edit_height.disabled = False
            self.ids.edit_chest_circumference.disabled = False
            self.ids.edit_torso_length.disabled = False

    def clear_measurement_widgets(self):
        self.ids.edit_height.text = ''
        self.ids.edit_chest_circumference.text = ''
        self.ids.edit_waist_circumference.text = ''
        self.ids.edit_torso_length.text = ''
        self.ids.edit_leg_length.text = ''
        self.ids.edit_image.source = ''
        self.ids.edit_custom_name.text = ''
        self.ids.edit_type.text = 'Seleccionar prenda'

    def save_clothing_details(self):
        clothing_info = get_clothing_info(self.clothing_id)
        old_image_path = clothing_info['image'] if clothing_info else None

        update_clothing_details(self.clothing_id,
                                self.ids.edit_type.text,
                                self.ids.edit_custom_name.text,
                                self.temp_image_path if self.temp_image_path else self.ids.edit_image.source,
                                self.ids.edit_height.text,
                                self.ids.edit_chest_circumference.text,
                                self.ids.edit_waist_circumference.text,
                                self.ids.edit_torso_length.text,
                                self.ids.edit_leg_length.text)
        
        # Eliminar la imagen antigua si se ha actualizado
        if self.temp_image_path and old_image_path and old_image_path != self.ids.edit_image.source:
            if os.path.exists(old_image_path):
                os.remove(old_image_path)

        # Actualizar la ruta de la imagen y limpiar la imagen temporal
        if self.temp_image_path:
            self.ids.edit_image.source = self.temp_image_path
            self.temp_image_path = None

        if self.manager.previous_screen == 'wardrobe_details':
            self.manager.current = 'wardrobe_details'
        elif self.manager.previous_screen == 'home':
            self.manager.current = 'home'
        else:
            self.manager.current = 'category_details'

    def cancel_edit(self):
        # Eliminar la imagen temporal si existe
        if self.temp_image_path and os.path.exists(self.temp_image_path):
            os.remove(self.temp_image_path)
        self.temp_image_path = None

        # Regresar a la pantalla anterior
        if self.manager.previous_screen == 'wardrobe_details':
            self.manager.current = 'wardrobe_details'
        elif self.manager.previous_screen == 'home':
            self.manager.current = 'home'
        else:
            self.manager.current = 'category_details'

    def delete_clothing(self):
        try:
            clothing_info = get_clothing_info(self.clothing_id)
            image_path = clothing_info['image'] if clothing_info else None

            delete_clothing_from_wardrobe(self.clothing_id)

            if image_path and os.path.exists(image_path):
                os.remove(image_path)

            if self.manager.previous_screen == 'wardrobe_details':
                self.manager.current = 'wardrobe_details'
            elif self.manager.previous_screen == 'home':
                self.manager.current = 'home'
            else:
                self.manager.current = 'category_details'

        except Exception as e:
            popup = Popup(title='Error al eliminar la prenda',
                          content=Label(text=f'Ocurrió un error al eliminar la prenda: {str(e)}'),
                          size_hint=(None, None), size=(400, 400))
            popup.open()

    def upload_image(self):
        content = BoxLayout(orientation='vertical')
        self.filechooser = FileChooserListView()
        content.add_widget(self.filechooser)
        
        select_button = Button(text='Seleccionar Imagen', size_hint_y=None, height=40)
        select_button.bind(on_press=self.select_image)
        content.add_widget(select_button)

        close_button = Button(text='Cerrar', size_hint_y=None, height=40)
        close_button.bind(on_press=lambda x: self.popup.dismiss())
        content.add_widget(close_button)

        self.popup = Popup(title='Seleccionar imagen', content=content, size_hint=(0.9, 0.9))
        self.popup.open()

    def select_image(self, instance):
        selection = self.filechooser.selection
        if selection:
            self.process_image(selection[0])
        self.popup.dismiss()

    def process_image(self, image_path):
        try:
            original_image = PILImage.open(image_path)
            resized_image = original_image.resize((335, 250))
            unique_filename = f"imagen_almacenamiento_id_{self.clothing_id}.jpg"
            temp_path = os.path.join(PROCESS_IMAGES_DIR, f"temp_{unique_filename}")
            resized_image.save(temp_path)
            self.temp_image_path = temp_path
            self.ids.edit_image.source = temp_path
        except Exception as e:
            popup = Popup(title='Error al procesar la imagen',
                          content=Label(text=f'Ocurrió un error al procesar la imagen: {str(e)}'),
                          size_hint=(None, None), size=(400, 400))
            popup.open()


class MesureScreen(Screen):
    temp_image_path = None

    def on_pre_enter(self, *args):
        self.update_wardrobe_spinner()

    def on_pre_leave(self, *args):
        # Eliminar la imagen temporal si existe
        if self.temp_image_path and os.path.exists(self.temp_image_path):
            os.remove(self.temp_image_path)
        self.temp_image_path = None

    def update_wardrobe_spinner(self):
        username = self.manager.get_screen('login').ids.username.text
        wardrobes = get_wardrobes(username)
        self.ids.wardrobe_spinner.values = wardrobes

    def on_spinner_select(self, text):
        # Limpiar todos los widgets de entrada y eliminar imagen temporal
        self.clear_measurement_widgets()
        
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

    def clear_measurement_widgets(self):
        # Eliminar la imagen temporal si existe
        if self.temp_image_path and os.path.exists(self.temp_image_path):
            os.remove(self.temp_image_path)
        self.temp_image_path = None
        
        self.ids.height.text = ''
        self.ids.chest_circumference.text = ''
        self.ids.waist_circumference.text = ''
        self.ids.torso_length.text = ''
        self.ids.leg_length.text = ''
        self.ids.image.source = ''
        self.ids.custom_name.text = ''

    def save_measurements(self, clothing_type, custom_name, image, height, chest_circumference, waist_circumference, torso_length, leg_length):
        try:
            username = self.manager.get_screen('login').ids.username.text
            wardrobe = self.ids.wardrobe_spinner.text
            if not wardrobe or wardrobe == 'Seleccione un armario':
                raise ValueError("Por favor, seleccione un armario")

            if not clothing_type or clothing_type == 'Seleccionar prenda':
                raise ValueError("Por favor, seleccione un tipo de prenda")

            save_measurements_clothing(username, clothing_type, wardrobe, custom_name, self.temp_image_path if self.temp_image_path else image, height, chest_circumference, waist_circumference, torso_length, leg_length)
            
            popup = Popup(title='Medidas Guardadas',
                          content=Label(text='Las medidas han sido guardadas correctamente'),
                          size_hint=(None, None), size=(400, 400))
            popup.open()
            
            # Actualizar la ruta de la imagen
            if self.temp_image_path:
                self.ids.image.source = self.temp_image_path
                self.temp_image_path = None

        except Exception as e:
            popup = Popup(title='Error',
                          content=Label(text=f'Ocurrió un error: {str(e)}'),
                          size_hint=(None, None), size=(400, 400))
            popup.open()

    def upload_image(self):
        content = BoxLayout(orientation='vertical')
        self.filechooser = FileChooserListView()
        content.add_widget(self.filechooser)
        
        select_button = Button(text='Seleccionar Imagen', size_hint_y=None, height=40)
        select_button.bind(on_press=self.select_image)
        content.add_widget(select_button)

        close_button = Button(text='Cerrar', size_hint_y=None, height=40)
        close_button.bind(on_press=lambda x: self.popup.dismiss())
        content.add_widget(close_button)

        self.popup = Popup(title='Seleccionar imagen', content=content, size_hint=(0.9, 0.9))
        self.popup.open()

    def select_image(self, instance):
        selection = self.filechooser.selection
        if selection:
            self.process_image(selection[0])
        self.popup.dismiss()

    def process_image(self, image_path):
        try:
            # Generar un nombre de archivo único
            unique_id = str(uuid.uuid4())
            unique_filename = f"imagen_almacenamiento_id_{unique_id}.jpg"

            # Abrir la imagen original
            original_image = PILImage.open(image_path)
            # Redimensionar la imagen
            resized_image = original_image.resize((335, 250))
            # Crear el path de destino
            temp_path = os.path.join(PROCESS_IMAGES_DIR, unique_filename)
            # Guardar la imagen redimensionada
            resized_image.save(temp_path)
            # Actualizar la imagen en la interfaz y guardar la ruta temporal
            self.temp_image_path = temp_path
            self.ids.image.source = temp_path
        except Exception as e:
            popup = Popup(title='Error al procesar la imagen',
                          content=Label(text=f'Ocurrió un error al procesar la imagen: {str(e)}'),
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
    current_category = StringProperty('')
    current_wardrobe = StringProperty('')
    previous_screen = StringProperty('')
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
        sm.add_widget(WardrobeDetailsScreen(name='wardrobe_details'))
        sm.add_widget(CategoryDetailsScreen(name='category_details'))
        sm.add_widget(EditClothingScreen(name='edit_clothing'))
        return sm

    def get_image_path(self, filename):
        return os.path.join(self.assets_dir, filename)

if __name__ == '__main__':
    BabyWardrobeApp().run()
