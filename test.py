from kivymd.app import MDApp
from kivy.lang import Builder

KV = '''
MDScreen:
    MDBoxLayout:
        orientation: 'vertical'

        MDTopAppBar:
            title: "Test MDList"
            elevation: 4

        MDScrollView:
            MDList:
                OneLineIconListItem:
                    text: "Convert to Grayscale"
                    IconLeftWidget:
                        icon: "image-filter-black-white"

                OneLineIconListItem:
                    text: "Apply Sepia"
                    IconLeftWidget:
                        icon: "image-filter"

                OneLineIconListItem:
                    text: "Rotate Image"
                    IconLeftWidget:
                        icon: "rotate-right"
'''

class TestApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Red"
        return Builder.load_string(KV)

TestApp().run()
