from kivymd.app import MDApp
import kivy
from kivymd.uix.filemanager import MDFileManager
import os
import cv2
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivymd.uix.label import MDLabel
from kivy.core.window import Window
import random
import string
kivy.require('2.2.0')


class Mainscreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.watermark_path = ""
        self.image_path = ""
        self.name_file = ""
        self.active_run = True
        self.save_imag = False
        self.passon = False
        self.random_string = ''
        self.selected_folder = ""
        self.logo = ''
        self.label = MDLabel(opacity=0, halign="center",
                             theme_text_color="Custom",
                             text_color="#E57C23",
                             font_size="60sp",
                             pos_hint={"center_x": .5, "center_y": .5},
                             bold=True)
        self.add_widget(self.label)

        self.manager_open = False
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager)

    def file_manager_open(self, checker):
        # output manager to the screen
        self.file_manager.show(os.path.expanduser("~\\Desktop"))
        self.manager_open = True
        if checker == "mainimage":
            self.file_manager.select_path = self.image_maker
        elif (checker == "filepath"):
            self.file_manager.select_path = self.make_path
        else:
            self.file_manager.select_path = self.logo_maker

    def exit_manager(self, *args):
        '''Called when the user reaches the root of the directory tree.'''
        self.manager_open = False
        self.file_manager.close()

    def make_path(self, path: str):
        self.selected_folder = path
        self.file_manager.close()
        self.ids.savepath.text = self.selected_folder

    def create_name(self):
        self.random_string = "".join(random.choices(
            string.ascii_lowercase + string.digits, k=8))
        filename = f"{self.random_string}.jpg"
        self.name_file = os.path.join(self.selected_folder, filename)

    def logo_maker(self, path: str):
        self.exit_manager()
        self.watermark_path = path
        imagetext = os.path.basename(path)
        self.ids.marktext.text = imagetext

    def image_maker(self, path: str):
        self.exit_manager()
        self.ids.imagebox.source = path
        self.image_path = path
        imagetext = os.path.basename(path)
        self.ids.phototext.text = imagetext
        self.ids.photoname.text = imagetext

    def prestart(self):
        if self.image_path != "" and self.watermark_path != "":
            self.img = cv2.imread(self.image_path)
            self.logo = cv2.imread(self.watermark_path)
            if self.img.size != self.logo.size:
                self.logo = self.resize_logo(self.logo, self.img)
        # print(imagetext)

    def events(self, instance, keyboard, keycode, text, modifiers):
        '''Called when buttons are pressed on the mobile device.'''

        if keyboard in (1001, 27):
            if self.manager_open:
                self.file_manager.back()
        return True

    def set_item(self, text_item):
        self.ids.drop_item.set_item(text_item)
        self.menu.dismiss()

    def checker(self):
        if self.image_path == "" and self.watermark_path == "" and self.selected_folder == "":
            self.passon = False
            self.label.text = "Insert Image and Icon and Select the location"
            self.label.opacity = 1

        elif self.image_path == "" and self.watermark_path == "" and self.selected_folder != "":
            self.passon = False
            self.label.text = "Insert Image and Icon"
            self.label.opacity = 1

        elif self.image_path == "" and self.watermark_path != "" and self.selected_folder == "":
            self.passon = False
            self.label.text = "Insert Image and select a location"
            self.label.opacity = 1

        elif self.image_path != "" and self.watermark_path == "" and self.selected_folder == "":
            self.passon = False
            self.label.text = "Insert Icon and select a location"
            self.label.opacity = 1

        elif self.image_path == "" and self.watermark_path != "" and self.selected_folder != "":
            self.passon = False
            self.label.text = "Insert Image"
            self.label.opacity = 1

        elif self.image_path != "" and self.watermark_path == "" and self.selected_folder != "":
            self.passon = False
            self.label.text = "Insert Icon"
            self.label.opacity = 1

        elif self.image_path != "" and self.watermark_path != "" and self.selected_folder == "":
            self.passon = False
            self.label.text = "select a location to save the file"
            self.label.opacity = 1

        else:
            self.label.opacity = 0
            self.passon = True

    def start(self):
        self.checker()
        opacity_change = self.ids.opacity_slider.value
        size_change = self.ids.size_slider.value
        opacity = 0.5
        size = 1
        image = self.image_path
        if self.passon:
            self.prestart()
            if opacity == opacity_change and size == size_change:

                self.makewatermark(
                    self.image_path, self.logo, opacity, size)
            elif (opacity != opacity_change and size != size_change or size != size_change or opacity != opacity_change):
                size = size_change
                opacity = opacity_change

                self.makewatermark(
                    self.image_path, self.logo, opacity, size)

    def makewatermark(self, image, WMlogo, opacity, size):
        if self.active_run:
            img = cv2.imread(image)
            logo = WMlogo
            h_img, w_img = img.shape[:2]
            h_logo, w_logo = logo.shape[:2]
            center_x = int(w_img / 2)
            center_y = int(h_img / 2)
            scaled_w_logo = int(w_logo * size)
            scaled_h_logo = int(h_logo * size)

            left_x = center_x - int(scaled_w_logo / 2)
            left_y = center_y - int(scaled_h_logo / 2)
            right_x = center_x + int(scaled_w_logo / 2)
            right_y = center_y + int(scaled_h_logo / 2)

            roi = img[left_y:right_y, left_x:right_x]
            resized_roi = cv2.resize(roi, (scaled_w_logo, scaled_h_logo))

            resized_logo = cv2.resize(logo, (scaled_w_logo, scaled_h_logo))

            result = cv2.addWeighted(resized_roi, 1, resized_logo, opacity, 0)
            result = cv2.resize(result, (right_x - left_x, right_y - left_y))

            img[left_y:right_y, left_x:right_x] = result
            self.progress_img = img

            file = "temp.jpg"
            cv2.imwrite(file, img)
            self.ids.imagebox.source = file
            self.ids.imagebox.reload()
            os.remove(file)

    def save_image(self):
        self.create_name()
        cv2.imwrite(self.name_file, self.progress_img)
        self.ids.saveid.text = f"Photo saved at {self.name_file}"

    def resize_logo(self, logo, target_image):
        target_height, target_width = target_image.shape[:2]
        logo_width = int(target_width / 2)
        resized_logo = cv2.resize(logo, (logo_width, int(
            logo_width * (logo.shape[0] / logo.shape[1]))))

        return resized_logo


class watermark(MDApp):
    def build(self):
        return Mainscreen()


if __name__ == "__main__":
    Window.size = (1200, 600)
    Builder.load_file("main.kv")
    watermark().run()
