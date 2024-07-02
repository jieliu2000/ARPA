from ARPA import ARPA
import PIL

def get_test_app_and_description():
        return "notepad.exe", ".*Notepad.*", "Notepad"

class TestARPA:

    @classmethod
    def setup_class(cls):
        cls.arpa = ARPA(debug_mode=False)


    def open_app(self):
        self.arpa.run_command(get_test_app_and_description()[0]) 
        return self.arpa.find_application(get_test_app_and_description()[1], get_test_app_and_description()[2])
     
    def test_click_ocr(self):
        self.arpa.click("ocr:./tests/unit/start.png")

    def test_find_window_by_title(self):
        image = PIL.Image.open('./tests/unit/text_and_window2.png')
        window = self.arpa.find_windows_by_title('Solution Explorer', image)
        assert window is not None

    def close_app(self):
        test_app_and_description = get_test_app_and_description()
        application = self.arpa.find_application(test_app_and_description[1], test_app_and_description[2])
        if(application is not None):
            self.arpa.close_app(application)

    def test_init(self):
        assert self.arpa is not None
        assert self.arpa.platform == "Windows"
    
    
    def test_maximize_window_by_app(self):
        app = self.open_app()
        self.arpa.maximize_window(app)
        window = app.windows[0]
        client_rect = window.client_rect()
        print(client_rect)
        self.close_app()


    def test_run_command(self):
        self.arpa.run_command(get_test_app_and_description()[0]) 
        application = self.arpa.find_application(get_test_app_and_description()[1], get_test_app_and_description()[2])
        assert application is not None
        self.close_app()

    @classmethod
    def teardown_class(cls):
        print("Tearing down the test class")
        test_app_and_description = get_test_app_and_description()
        application = cls.arpa.find_application(test_app_and_description[1], test_app_and_description[2])
        if(application is not None):
            cls.arpa.close_app(application)
