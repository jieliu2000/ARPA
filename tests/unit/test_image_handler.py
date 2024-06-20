from ARPA import ImageHandler
import PIL

class TestImageHandler:
    
    
    @classmethod
    def setup_class(cls):
        cls.handler = ImageHandler(debug_mode=True)


    def test_find_image_location(self):
         screen = PIL.ImageGrab.grab(all_screens=True)
         start_img = PIL.Image.open('./tests/unit/start.png')
         
         # Find the location of the start image on the screen
         start_location = self.handler.find_image_location( start_img, screen)
         assert start_location is not None, "Start image not found on the screen"