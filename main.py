import kivy
import random
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.properties import StringProperty, ListProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.core.text import LabelBase
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
from functools import partial
import sqlite3



kivy.require('1.9.0')
Window.clearcolor = (1, 1, 1, 1)
Window.size = (432, 807)
def show_menu(obj):
    obj.clear_widgets()
courses = ['economy', 'geography','government','history','laws','symbols']
class Manager(FloatLayout):
    active_acc = StringProperty(None)
    def __init__(self, **kwargs):
        super(Manager, self).__init__(**kwargs)

    #Parent class for all submenus
    def show_menu(self,b):
        #Clears all active widgets and goes back to the menu
        self.clear_widgets()
        self.add_widget(Menu())

class CourseManager(Manager):
    #Submenu for course access
    def show_course(self, course):
        #Clear all active widgets and shows the selected course
        self.clear_widgets()
        #To make code more readable
        self.add_widget(Course(content=open('coursesC.txt', encoding='UTF8').read().replace('\n',' ').split("##")[courses.index(course.lower().strip())], name=course))
        #Creates a Course object that accesses the element of the list made from the text file corresponding to the required course


class QuizManager(Manager):
    def __init__(self, **kwargs):
        super(QuizManager, self).__init__(**kwargs)
        self.show_quiz()
    def show_quiz(self):
        app = App.get_running_app()
        self.clear_widgets()
        if app.account:
            conn = sqlite3.connect('batadase.db')
            cursor = conn.cursor()
            options = cursor.execute("""
            SELECT economy, geography, government, history, laws, symbols FROM userdata
            WHERE username = ?
            """, [app.get_running_app().account]).fetchone()
            quiz = options.index(min(options))
            #Finds the lowest value in the list of scores corresponding to user
        else:
            quiz = random.randint(0,5)
            #Picks a random subject
        question_data = random.choice([x for x in open('qs.txt', 'r', encoding='UTF8').read().replace('\n','').split('##')[quiz].split('!!') if x.split('::')!=['']]).split('::')
        #Picks a random question from the appropriate subject
        current_quiz = Quiz(questions=question_data)
        current_quiz.name = courses[quiz]
        self.add_widget(current_quiz)


class HelpManager(Manager):
    def show_help(self, help):
        self.clear_widgets()
        self.add_widget(Help(content=help + '.txt'))

class AccountManager(Manager):
    def __init__(self, **kwargs):
        app = App.get_running_app()
        super(AccountManager, self).__init__(**kwargs)
    def login_screen(self):
        self.clear_widgets()
        self.add_widget(Login())
    def signup_screen(self):
        self.clear_widgets()
        self.add_widget(Signup())
    def logout(self):
        app = App.get_running_app()
        app.account = None
        open('config.txt', 'w').write('None')
        self.show_menu('1')

class DetailsManager(Manager):
    def get_score(self, index):
        app = App.get_running_app()
        if app.account:
            conn = sqlite3.connect('batadase.db')
            cursor = conn.cursor()
            scores = cursor.execute(
                """SELECT economy, geography, government, history, laws, symbols FROM userdata
                            WHERE username = ?
                            """, [app.get_running_app().account]).fetchone()
            return scores[index]
        else:
            self.show_menu(1)
            not_logged_in = Label(text='You are not \nlogged in.\nPlease log in to \nuse this function')
            popup = Popup(title="Log in", content=not_logged_in,size_hint=(0.5, 0.5), pos_hint={'x':0.25, 'y':0.25}, auto_dismiss=True)
            popup.open()
            return 'NO DATA'









class Quiz(FloatLayout):
    questions = ListProperty(random.choice(open('default.txt', 'r', encoding='UTF8').readlines()).replace('\n', '').split('::'))
    #Picks a random line from the question file, and splits it by '::' turning it into a ListProperty for use in the .kv file
    def __init__(self, **kwargs):
        super(Quiz, self).__init__(**kwargs)
        #Used to make a kwarg to access the question file needed

    def rerun(self, b):
        self.clear_widgets()
        self.add_widget(QuizManager())
        #Gives the user a new question

    def show_menu(self,b):
        self.clear_widgets()
        self.add_widget(Menu())
        #Takes the user back to the menu

    def is_correct(self, a1, a2):
        app = App.get_running_app()
        self.clear_widgets()
        button1 = Button(text='Take me back to the menu',size_hint=(0.5, 0.1), pos_hint={'x': 0.25, 'y': 0.5}, border=(30,30,30,30),
                         font_name='MuseoSans',font_size=15, background_normal='button.png', background_down='buttonDown.png',
                         text_size=(self.width, None), halign='center')
        button1.bind(on_press=partial(self.show_menu))
        #Creates a button to send the user back to the main menu
        self.add_widget(button1)
        button2 = Button(text='Ask me another question', size_hint=(0.5, 0.1), pos_hint={'x': 0.25, 'y': 0.25}, border=(30,30,30,30),
                        font_name='MuseoSans', font_size=15, background_normal='button.png', background_down='buttonDown.png',
                         text_size=(self.width, None), halign='center')
        button2.bind(on_press=partial(self.rerun))
        #Creates a button to ask the user another question
        self.add_widget(button2)
        if a1 == a2:
            self.add_widget(Label(text='You got it right!', pos_hint={'x':0.25,'y':0.8}, size_hint=(0.5, 0.1),
                                               font_name='MuseoSans', color=[0,1,0,1],font_size=40))
            sound = SoundLoader.load('Good Job.mp3')
            #Plays a congratulatory sound effect and text indicating the user is correct
            sound.play()
            if app.account:
                conn = sqlite3.connect('batadase.db')
                cursor = conn.cursor()
                query =f"""
                UPDATE userdata
                SET {self.name} = {self.name}+50
                WHERE username = ?"""
                #fstring of SQL code because Python variables cannot be normally inputted in the middle of the line in sqlite
                cursor.execute(query, [app.account])
                conn.commit()
                conn.close()
                #Updates SQL database with new proficiency score
        else:
            self.add_widget(Label(text='You got it wrong... \nThe correct answer was\n' + a2, pos_hint={'x':0.25,'y':0.8}, size_hint=(0.5, 0.1),
                                               font_name='MuseoSans', color=[1,0,0,1],font_size=30))
            sound = SoundLoader.load('Bad Job.mp3')
            # Plays a disappointed sound effect and text indicating the user is incorrect
            sound.play()
            return False

class Help(GridLayout):
    content = StringProperty('default.txt')
    def __init__(self, **kwargs):
        super(Help, self).__init__(**kwargs)
    def show_menu(self):
        self.clear_widgets()
        self.add_widget(HelpManager())

class Course(GridLayout):
    content = StringProperty('default.txt')
    name = StringProperty('default')
    #The file accessed for the course
    def __init__(self, **kwargs):
        super(Course, self).__init__(**kwargs)
        #Used to make a kwarg to access individual courses
    def show_quiz(self):
        self.clear_widgets()
        processed_qs = open('qs.txt', 'r', encoding='UTF8').read().replace('\n', '').split('##')
        question_data = random.choice([x for x in processed_qs[courses.index(self.name.lower().strip())].split('!!') if x.split('::')!=['']]).split('::')
        #Accesses a random question from the appropriate subject
        this_quiz = CourseQuiz(questions=question_data)
        #Add a CourseQuiz() and clears all widgets
        this_quiz.name = courses.index(self.name.lower().strip())
        #Used in order to access the specific quiz for the CourseQuiz()
        self.add_widget(this_quiz)
        #Adds the CourseQuiz()

class CourseQuiz(Quiz):
    def show_manager(self, b):
        self.clear_widgets()
        self.add_widget(CourseManager())
        #Clears all widgets and adds the CourseManager()

    def rerun(self, b):
        self.clear_widgets()
        this_quiz = CourseQuiz(questions=random.choice([x for x in open('qs.txt', 'r', encoding='UTF8').read().replace('\n','').split('##')[self.name].split('!!') if x.split('::')!=['']]).split('::'))
        this_quiz.name = self.name
        self.add_widget(this_quiz)
        #Adds another question with the same subject

    def is_correct(self, a1, a2):
        if a1 == a2:
            sound = SoundLoader.load('Good Job.mp3')
            sound.play()
            #Plays a congratulatory sound effect
            button1 = Button(text='Take me \nback to the \n menu',size_hint=(0.2, 0.1), pos_hint={'x': 0.1, 'y': 0}, border=(30,30,30,30),
                           font_name='MuseoSans', font_size=14, background_normal='button.png', background_down='buttonDown.png',
                         text_size=(self.width-20, None), halign='center')
            button1.bind(on_press=partial(self.show_menu))
            #Button to return the user to the main menu
            self.add_widget(button1)
            button2 = Button(text='Ask me \nanother \n question', size_hint=(0.2, 0.1), pos_hint={'x': 0.4, 'y': 0}, border=(30,30,30,30),
                            font_name='MuseoSans', font_size=14, background_normal='button.png', background_down='buttonDown.png',
                         text_size=(self.width, None), halign='center')
            button2.bind(on_press=partial(self.rerun))
            #Button to ask the user a question from the same course
            self.add_widget(button2)
            button3 = Button(text='Take me \nback to the \n course menu', size_hint=(0.2, 0.1), pos_hint={'x': 0.7, 'y': 0}, border=(30,30,30,30),
                            font_name='MuseoSans', font_size=14, background_normal='button.png', background_down='buttonDown.png',
                         text_size=(self.width, None), halign='center')
            button3.bind(on_press=partial(self.show_manager))
            #Button to return the user to the course selector
            self.add_widget(button3)
            return True
        else:
            return False
        #Creates a menu upon answering the question in order to go back to the main menu, show another question on the same subject, or the course manager

class Signup(FloatLayout):
    #Class for signup screen
    def make_account(self):
        app = App.get_running_app()
        #Creates an account
        conn = sqlite3.connect('batadase.db')
        cursor = conn.cursor()
        cursor.execute("""SELECT username
                         FROM userdata
                         WHERE username=?""",
                    ([self.ids.user_name.text]))
        #Checks if username is in use
        result = cursor.fetchone()
        if result:
            self.ids.user_name.text = ''
            self.ids.user_name.hint_text = 'That username is already in use'
        else:
            cursor.execute(''' INSERT INTO userdata (username, password, history, geography, economy, government, laws, symbols)
            VALUES (?, ?, 0, 0, 0, 0, 0, 0)
            ''', (self.ids.user_name.text, self.ids.pass_word.text) )
            app.account = self.ids.user_name.text
            open('config.txt', 'w').write(str(self.ids.user_name.text))
            #Creates a new user row in the table
            conn.commit()
            conn.close()
            self.clear_widgets()
            self.add_widget(AccountManager(active_acc=app.account))
            #Sends user back to account screen
    def quit(self):
        app = App.get_running_app()
        self.clear_widgets()
        self.add_widget(AccountManager(active_acc=app.account))


class Login(FloatLayout):
    #Class for login screen
    def access_account(self):
        app = App.get_running_app()
        #Allows user to log in to account
        conn = sqlite3.connect('batadase.db')
        cursor = conn.cursor()
        result = cursor.execute("""SELECT username,password
                                 FROM userdata
                                 WHERE username=?
                                    AND password=?""",
                      (self.ids.user_name.text,self.ids.pass_word.text)).fetchall()
        #Looks for a username and password corresponding to the column in the table
        if result:
            app.account = self.ids.user_name.text
            open('config.txt', 'w').write(str(self.ids.user_name.text))
            conn.commit()
            conn.close()
            self.clear_widgets()
            self.add_widget(AccountManager(active_acc=app.account))
            #Updates variable for app.account to current username
        else:
            self.ids.user_name.text = ''
            self.ids.pass_word.text = ''
            self.ids.user_name.hint_text = 'This is not an existing username or password'
    def quit(self):
        app = App.get_running_app()
        self.clear_widgets()
        self.add_widget(AccountManager(active_acc = app.account))





classDict = {'QuizManager':QuizManager,'CourseManager':CourseManager, 'HelpManager':HelpManager, 'AccountManager':AccountManager, 'DetailsManager':DetailsManager}


class Menu(FloatLayout):
    def show_option(self, option):
        self.clear_widgets()
        self.add_widget(classDict[option]())

    def exit(self):
        pass


class CanadaApp(App):
    olduser = open('config.txt', 'r').read()
    account = None if olduser == 'None' else olduser
    #Accesses the last account logged in to.
    #App wide variable representing the username of the current account in use
    def build(self):
        try:
            con = sqlite3.connect('batadase.db')
            #Creating a connection between the database and program
            cur = con.cursor()
            #Creating a cursor to perform queries and creation  of tables in the database
            cur.execute(""" CREATE TABLE userdata(
                            username text,
                            password text,
                            history integer,
                            geography integer,
                            economy integer,
                            government integer,
                            laws integer,
                            symbols integer)
                            """)
            #Creates a table with columns for username, password, and all user stats
            con.commit()
            #Commits all changes to the file
            con.close()
            #Closes the connection between the program and file
        except  sqlite3.OperationalError:
            #This makes sure the program does not attempt to create a table that already exists
            pass
        LabelBase.register(name='MuseoSans',
                           fn_regular='MuseoSansRounded700.otf')
        #Registers a font for use in the GUI

        return Menu()


if __name__ == '__main__':
    CanadaApp().run()
