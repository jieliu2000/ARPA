
import PIL.Image
from robot.api.deco import keyword, library, not_keyword
from robot.api import logger
import re
import PIL
from pywinauto import mouse, keyboard, findwindows, Application
import pyautogui
import time
import platform
from datetime import datetime
from .image_handler import ImageHandler
import os
__version__ = '0.1'

@library(scope='GLOBAL', auto_keywords=True)
class ARPA:
    '''ARPA is a library for Robot Framework that provides a set of keywords to interact with Windows applications.'''
    def __init__(self, step_pause_interval = 3, debug_mode = False):
        self.platform = platform.system()
        self.debug_mode = debug_mode
        if(self.platform != 'Windows'):
            raise Exception('This version currently only supports Windows. Other platforms will be supported in the future.')
        self.image_handler = ImageHandler(debug_mode)
        self.step_pause_interval = step_pause_interval

    def run_command(self, command, noblock = True):
        '''Run a system command. The noblock parameter specify whether this function need to be blocked when executing the command.'''
        self.sleep()
        if(noblock):
            return os.popen(command)
        else:
            return os.system(command)
        
    def sleep(self, seconds = 0):
        '''Sleep for a specific time.'''
        if(seconds == 0):
            seconds = self.step_pause_interval
        if(seconds <= 0):
            return
        else:
            time.sleep(seconds)

    def find_windows_by_title(self, title, image=None):
        '''Find a window by its title. This function will return the window if it exists, otherwise it will return None.'''
        if image is None:
            image = self.take_screenshot()
        text_location = self.image_handler.find_text_in_image(image, title)
        if(text_location is None):
            return None
        else:
            rects = self.image_handler.find_rects_outside_position(image, text_location)
            return rects

    def find_control_near_text(self, text):
        '''Find a control near a specific text. This function will return the control if it exists, otherwise it will return None.'''
        img = self.take_screenshot()
        location = self.image_handler.find_text_in_image(img, text)
        if(location is None):
            return None
        else:
            return self.image_handler.find_control_near_position(img, location[0])

    def take_screenshot(self, all_screens = True, filename = None):
        '''Take a screenshot and save it to a file. If the filename parameter is not specified, the screenshot will be saved to a file with a random name.'''
        img = PIL.ImageGrab.grab(all_screens=True)
        if filename is not None:
            img.save(filename)
        return img

    def wait_until_text_exists(self, text, filter_args_in_parent=None, parent_control = None, search_in_image = None, timeout = 30):
        '''Wait until a specific text exists in the current screen. This function will return the location if the text exists, otherwise it will return None.'''
        start_time = datetime.now()
        while(True):
            location = self.validate_text_exists(text, filter_args_in_parent, parent_control, search_in_image)
            if(location is not None):
                return location 
            else:
                diff = datetime.now() - start_time
                if(diff.seconds > timeout):
                    raise AssertionError('Timeout waiting for text: ' + text)
                self.sleep(1)
                search_in_image = None
    
        
    def validate_text_exists(self, text, filter_args_in_parent=None, parent_control = None, img = None):
        '''Validate whether a specific text exists in the current screen. This function will return True if the text exists, otherwise it will return False.'''
        if img is None:
            img = self.take_screenshot()
        
        location = self.image_handler.find_text_in_rects(img, text, filter_args_in_parent, parent_control)
        if(location is None or location[0] is None or location[1] is None):
            return None
        else:
            return location
        
    @not_keyword
    def build_app_params(self, title, class_name = None):
        params = {}
        if(title is not None and title != ""):
            params["title_re"] = title
        if(class_name is not None and class_name != ""):
            params["class_name"] = class_name
        return params

    def find_application(self, title, class_name = None):
        '''Find an application by its title keyword.'''
        params = self.build_app_params(title, class_name)
    
        windows = findwindows.find_elements(**params)
        if(len(windows) == 0):
            return None
        else:
            process_id = windows[0].process_id
            return Application().connect(process = process_id)

    @not_keyword
    def get_app(self, app_or_keyword):
        app = app_or_keyword
        if(type(app_or_keyword) == str):
            app = self.find_application(app_or_keyword, None)
        return app

    def close_app(self, app_or_keyword, force_quit = False):
        '''Close an application. The parameter could be the app instance or the app's title keyword. The force_quit parameter specify whether this function need to be forced quit just like what we did in task manager.'''
        app = self.get_app(app_or_keyword)
        if(app is None):
            pass
        else:
            app.kill(not(force_quit))

   
    def maximize_window(self, app_or_keyword, window_title_pattern = None):
        '''Maximize the window of the application.'''
        app = self.get_app(app_or_keyword)
                
        if window_title_pattern is not None:
            window = app.window(title_re=window_title_pattern)
            if window is not None:
                window.maximize()
                self.sleep()
            

    def click(self, locator,  button='left', double_click= False):
        '''Click on a control. The parameter could be a locator or the control's text (like the button text or the field name)'''
        if(isinstance(locator, str) and locator.startswith('ocr:')):
            path = locator.split('ocr:')[1]
            logger.debug('Clicking OCR:', path)

            self.click_by_image(path, button, double_click)
        pass

    def click_by_image(self, image_path, button='left', double_click= False):
        img = PIL.Image.open(image_path)
        screenshot = self.take_screenshot()
            
        location = self.image_handler.find_image_location(img, screenshot)
        if(location is not None):
                self.click_by_position(int(location[0]) + 2, int(location[1]) + 2)

    def click_by_text_inside_window(self, text, window_title, button='left', double_click= False):
        '''Click the positon of a string on screen. '''
        logger.debug('Click by text inside window:' + text + " window title: " + window_title)
        img = self.take_screenshot(window_title)
        rects = self.find_windows_by_title(window_title, img)
        if(rects is None or len(rects) ==0):
            return None
        else:
            location = self.validate_text_exists(text, rects, img)
            if(location is not None and location[0]):
                self.click_by_position(int(location[0]), int(location[1]), button, double_click)
            self.sleep()


        self.sleep()

    def click_by_text(self, text, button='left', double_click=False, filter_args_in_parent=None):
        '''Click the positon of a string on screen. '''
        logger.debug('Click by text:', text)
        location = self.wait_until_text_exists(text, filter_args_in_parent)
        if(location is not None and location[0]):
            self.click_by_position(int(location[0]), int(location[1]), button, double_click)
        self.sleep()

      
    def click_by_position(self, x:int, y:int, button='left', double_click=False):
        '''Click the positon based on the coordinates. '''
        logger.debug('Click by position: {}, {}, {}, {}'.format(x, y, type(x), type(y)))
        mouse.move((x, y))
        self.sleep(1)
        if(double_click):
            mouse.double_click(button, (x, y))
        else:
            mouse.click(button, (x,y))
        self.sleep()

    def send_keys(self, keys):
        '''Simulate the keyboard action to send keys. It uses pywinauto's send_keys method. See https://pywinauto.readthedocs.io/en/latest/code/pywinauto.keyboard.html for details.

You can use any Unicode characters (on Windows) and some special keys listed below. The module is also available on Linux.

Available key codes: 

{SCROLLLOCK}, {VK_SPACE}, {VK_LSHIFT}, {VK_PAUSE}, {VK_MODECHANGE},{BACK}, {VK_HOME}, {F23}, {F22}, {F21}, {F20}, {VK_HANGEUL}, {VK_KANJI},{VK_RIGHT}, {BS}, {HOME}, {VK_F4}, {VK_ACCEPT}, {VK_F18}, {VK_SNAPSHOT},{VK_PA1}, {VK_NONAME}, {VK_LCONTROL}, {ZOOM}, {VK_ATTN}, {VK_F10}, {VK_F22},{VK_F23}, {VK_F20}, {VK_F21}, {VK_SCROLL}, {TAB}, {VK_F11}, {VK_END},{LEFT}, {VK_UP}, {NUMLOCK}, {VK_APPS}, {PGUP}, {VK_F8}, {VK_CONTROL},{VK_LEFT}, {PRTSC}, {VK_NUMPAD4}, {CAPSLOCK}, {VK_CONVERT}, {VK_PROCESSKEY},{ENTER}, {VK_SEPARATOR}, {VK_RWIN}, {VK_LMENU}, {VK_NEXT}, {F1}, {F2},{F3}, {F4}, {F5}, {F6}, {F7}, {F8}, {F9}, {VK_ADD}, {VK_RCONTROL},{VK_RETURN}, {BREAK}, {VK_NUMPAD9}, {VK_NUMPAD8}, {RWIN}, {VK_KANA},{PGDN}, {VK_NUMPAD3}, {DEL}, {VK_NUMPAD1}, {VK_NUMPAD0}, {VK_NUMPAD7},{VK_NUMPAD6}, {VK_NUMPAD5}, {DELETE}, {VK_PRIOR}, {VK_SUBTRACT}, {HELP},{VK_PRINT}, {VK_BACK}, {CAP}, {VK_RBUTTON}, {VK_RSHIFT}, {VK_LWIN}, {DOWN},{VK_HELP}, {VK_NONCONVERT}, {BACKSPACE}, {VK_SELECT}, {VK_TAB}, {VK_HANJA},{VK_NUMPAD2}, {INSERT}, {VK_F9}, {VK_DECIMAL}, {VK_FINAL}, {VK_EXSEL},{RMENU}, {VK_F3}, {VK_F2}, {VK_F1}, {VK_F7}, {VK_F6}, {VK_F5}, {VK_CRSEL},{VK_SHIFT}, {VK_EREOF}, {VK_CANCEL}, {VK_DELETE}, {VK_HANGUL}, {VK_MBUTTON},{VK_NUMLOCK}, {VK_CLEAR}, {END}, {VK_MENU}, {SPACE}, {BKSP}, {VK_INSERT},{F18}, {F19}, {ESC}, {VK_MULTIPLY}, {F12}, {F13}, {F10}, {F11}, {F16},{F17}, {F14}, {F15}, {F24}, {RIGHT}, {VK_F24}, {VK_CAPITAL}, {VK_LBUTTON},{VK_OEM_CLEAR}, {VK_ESCAPE}, {UP}, {VK_DIVIDE}, {INS}, {VK_JUNJA},{VK_F19}, {VK_EXECUTE}, {VK_PLAY}, {VK_RMENU}, {VK_F13}, {VK_F12}, {LWIN},{VK_DOWN}, {VK_F17}, {VK_F16}, {VK_F15}, {VK_F14}
~ is a shorter alias for {ENTER}

Modifiers:

* '+': {VK_SHIFT}
* '^': {VK_CONTROL}
* '%': {VK_MENU} a.k.a. Alt key
        '''
        keyboard.send_keys(keys)
        self.sleep()


    def input_text(self, text):
        pyautogui.write(text)
        self.sleep()

    def enter_in_field(self, field_name, text):
        img = self.take_screenshot()
        location = self.wait_until_text_exists(field_name)
        if(location is None):
            logger.error('Cannot find field:', field_name)
            return
        (x,y,w,h) = self.image_handler.find_control_near_position(img, location)
        self.click_by_position(x+3, y+3)
        self.input_text(text)
        self.sleep()
