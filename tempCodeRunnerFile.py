    # def on_file_selected(self, selection):
    #     try:
    #         if not selection:
    #             print("No file selected")
    #             return
    #         image_path = selection[0]
    #         if not os.path.exists(image_path):
    #             print(f"File does not exist: {image_path}")
    #             return
    #         valid_extensions = ('.png', '.jpg', '.jpeg')
    #         if not image_path.lower().endswith(valid_extensions):
    #             print(f"Invalid image format: {image_path}")
    #             return

            
    #         home_screen = self.root.get_screen("home")  # Truy cập màn hình 'home'
    #         content_image = home_screen.ids.home_main_screen.img  # Lấy widget Image qua ID
    #         content_image.source = image_path  # Cập nhật đường dẫn ảnh
    #         content_image.opacity = 1  # Hiển thị ảnh

    #         print(f"Selected image: {image_path}")
                      

    #     except Exception as e:
    #         print(f"Error processing file: {e}")