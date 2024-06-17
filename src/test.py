from ARPA import ARPA, ImageHandler
import time

arpa = ARPA(5, False)

'''

arpa.run_command('start devenv')
time.sleep(10)
arpa.click_by_text('Create a new project')
time.sleep(5)        


arpa.enter_in_field('Search for templates', 'Console App')
arpa.click_by_text('Console App')        
arpa.click_by_text('Next') 
arpa.enter_in_field('Project name', 'ConsoleAPP3')
arpa.click_by_text('Next')
arpa.click_by_text('Create')
'''

# arpa.click_by_text_inside_window('Program.cs', 'Solution Explorer', 'right')

app = arpa.find_application('.*Microsoft Visual Studio.*')
#arpa.maximize_window(app, '.*Microsoft Visual Studio.*')

arpa.click_by_text('internal class Program')
arpa.send_keys('^a')
arpa.input_text('aaa\nbbb')
