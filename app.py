from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.image import Image
from kivymd.app import MDApp
from plyer import filechooser
import os
import cv2
import numpy as np
from io import BytesIO
from PIL import Image as PILImage
from kivy.core.image import Image as CoreImage
import mysql.connector
from kivymd.toast import toast

Window.size = (360, 640)

class Shutter(MDApp):
    def build(self):
        self.current_image_cv = None  # lưu ảnh hiện tại
        self.original_image_cv = None  # lưu ảnh gốc
        self.brightness_value = 0
        self.contrast_value = 0
        self.edit_history = []
       
        try:
            kv = Builder.load_file("user_interface.kv")          
            return kv
        except Exception as e:
            print(f"Error loading KV file: {e}")
            return None

    @staticmethod
    def connect_db():

            db = mysql.connector.connect(
                host='localhost',
                user='root',
                password='vohoainam10012005',
                database='login_database'
            )
            return db

    def create_account(self):
        regisdb = self.connect_db()
        contro = regisdb.cursor()
        username = self.root.ids.username_register.text.strip()
        password = self.root.ids.pass_register.text.strip()
        try:
            contro.execute("INSERT INTO users(username, password) VALUES (%s, %s)", (username,password))
            regisdb.commit()
            toast("Tạo tài khoản thành công!")
            self.root.current = 'login'
            self.root.transition.direction = "left"
        except mysql.connector.IntegrityError: #xu li loi rang buoc(UNIQUE, Not NUll trong sql)
            toast("Tài khoản đã tồn tại")
        finally:
            regisdb.close()
            contro.close()

    def sign_in(self):
        username = self.root.ids.username_login.text.strip()
        password = self.root.ids.pass_login.text.strip()

        if not username or not password:
            toast("Vui lòng nhập tài khoản và mật khẩu")
            return

        conn = self.connect_db()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
            user = cursor.fetchone()
            if user:
                toast(f"Welcome, {username}!")
                self.root.current = 'home'
            else:
                toast("Sai tài khoản hoặc mật khẩu")
            cursor.close()
            conn.close()

    def on_upload_pressed(self):
        filechooser.open_file(
            title="Select an image",
            filters=[("Image files", "*.png", "*.jpg", "*.jpeg")],
            on_selection=self.on_file_selected
        )

    def on_file_selected(self, selection):
        try:
            if not selection:
                print("No file selected")
                return

            image_path = selection[0]
            print("Image selected:", image_path)
                      
            image_widget = None
            if 'img' in self.root.ids:
                image_widget = self.root.ids.img
            else:
                home_screen = self.root.get_screen("home")
                if 'img' in home_screen.ids:
                    image_widget = home_screen.ids.img
                else:
                    if 'main_box' in home_screen.ids:
                        main_box = home_screen.ids.main_box
                        for child in main_box.walk(restrict=False):
                            if isinstance(child, Image) and child.id == "img":
                                image_widget = child
                                break

            if not image_widget:
                print("Image widget not found.")
                return

            image_widget.source = image_path
            image_widget.opacity = 1
            # Lưu ảnh gốc và ảnh hiện tại
            img = cv2.imread(image_path)
            self.original_image_cv = img.copy()
            self.current_image_cv = img.copy()

        except Exception as e:
            print(f"Error processing file: {e}")

    def toggle_edit_menu(self):
        try:
            menu_container = self.root.ids.edit_menu_container
            menu_container.opacity = 1 if menu_container.opacity == 0 else 0
            menu_container.disabled = not menu_container.disabled
        except Exception as e:
            print(f"Error toggling edit menu: {e}")

    def adjust_brightness(self):
        slider = self.root.ids.edit_slider
        slider.opacity = 1
        slider.disabled = False
        slider.height = "30dp"
        slider.value = 0
        slider.min = -100
        slider.max = 100
        slider.bind(value=lambda instance, value: self.apply_edit("brightness", value))
        self.apply_edit("brightness", 0)

    def adjust_contrast(self):
        slider = self.root.ids.edit_slider_ct
        slider.opacity = 1
        slider.disabled = False
        slider.height = "30dp"
        slider.min = -100
        slider.max = 100
        slider.value = 0
        slider.bind(value=lambda instance, value: self.apply_edit("contrast", value))
        self.apply_edit("contrast", 0)

    def restore_original(self):
        if self.original_image_cv is not None:
            self.current_image_cv = self.original_image_cv.copy()
            self.brightness_value = 0
            self.contrast_value = 0
            self.edit_history = []
            pil_img = PILImage.fromarray(cv2.cvtColor(self.current_image_cv, cv2.COLOR_BGR2RGB))
            buffer = BytesIO()
            pil_img.save(buffer, format='PNG')
            buffer.seek(0)
            self.root.ids.img.texture = CoreImage(buffer, ext='png').texture

    def apply_edit(self, edit_type, value=None):

        try:
            image_widget = self.root.ids.img

            if self.original_image_cv is None:
                print("No image loaded.")
                return

            img = self.original_image_cv.copy()

            # Nếu là chỉnh brightness hoặc contrast thì cập nhật giá trị
            if edit_type == "brightness":
                self.brightness_value = int(value) if value is not None else 0
            elif edit_type == "contrast":
                self.contrast_value = int(value) if value is not None else 0
            elif edit_type not in ["brightness", "contrast"]:
                self.edit_history.append((edit_type, value))

            # Áp brightness trước
            if self.brightness_value != 0:
                hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
                h, s, v = cv2.split(hsv)
                v = cv2.add(v, self.brightness_value)
                v = np.clip(v, 0, 255)
                img = cv2.merge((h, s, v))
                img = cv2.cvtColor(img, cv2.COLOR_HSV2BGR)

            # Áp contrast tiếp theo
            if self.contrast_value != 0:
                f = 131 * (self.contrast_value + 127) / (127 * (131 - self.contrast_value + 1e-5))
                img = cv2.addWeighted(img, f, img, 0, 127 * (1 - f))

            # Áp các hiệu ứng khác từ lịch sử
            for hist_type, hist_value in self.edit_history:
                if hist_type == "grayscale":
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
                elif hist_type == "rotate":
                   
                    pil_img = PILImage.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
                    pil_img = pil_img.rotate(-90, expand=True)
                    img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
                elif hist_type == "crop":
                    height, width = img.shape[:2]
                    crop_width = int(width * 0.9)
                    crop_height = int(height * 0.9)
                    x1 = (width - crop_width) // 2
                    y1 = (height - crop_height) // 2
                    x2 = x1 + crop_width
                    y2 = y1 + crop_height
                    img = img[y1:y2, x1:x2]
                elif hist_type == "split":
                    b, g, r = cv2.split(img)
                    zeros = np.zeros_like(b)
                    red_img = cv2.merge([zeros, zeros, r])
                    green_img = cv2.merge([zeros, g, zeros])
                    blue_img = cv2.merge([b, zeros, zeros])
                    img = np.hstack((red_img, green_img, blue_img))
                elif hist_type == "detect_faces":
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
                    for (x, y, w, h) in faces:
                        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Hiển thị kết quả
            pil_img = PILImage.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            buffer = BytesIO()
            pil_img.save(buffer, format='PNG')
            buffer.seek(0)
            image_widget.texture = CoreImage(buffer, ext='png').texture
            self.current_image_cv = img.copy()




        except Exception as e:
            print(f"Error applying edit: {e}")

    def save_image_to_device(self):
        if self.current_image_cv is None:
            toast("Chưa có ảnh để lưu!")
            return

        def on_path_selected(selection):
            if selection:
                save_path = os.path.join(selection[0], "edited_image.png")
                try:
                    cv2.imwrite(save_path, self.current_image_cv)

                except Exception as e:
                    toast(f"Lỗi khi lưu ảnh: {e}")


        filechooser.choose_dir(on_selection=on_path_selected)

if __name__ == '__main__':
    Shutter().run()
