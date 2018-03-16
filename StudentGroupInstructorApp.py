from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.properties import NumericProperty, ObjectProperty, StringProperty
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.listview import ListView
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.graphics import Line
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.adapters.listadapter import ListAdapter
from kivy.uix.listview import ListItemButton, ListView
from kivy.uix.popup import Popup

import string
import random
import datetime




"""
things to add
show number of students in a group

- show list of students in a group ?
- remove students ?

add / remove groups ?

- check random name is unique


things to fix
if new instructor in instructors_init_list - no update requires

"""



sm=''
current_group = ''

global_group_data_dict={}
all_instructors=[]
instructors_init_list=[]
instructors_new_list=[]
instructor_widgets =[]

list_students_in_group = []

from dbcon import DbCon


class Main_Screen(Screen):
    layout_content = ObjectProperty(None)
    def __init__(self, **kwargs):
        global all_instructors
        all_instructors = DbCon().get_all_instrutors()
        self.programs = DbCon().get_programs()
        self.filter = 'Form'
        self.program = self.programs[0]
        super(Main_Screen, self).__init__(**kwargs)


    def on_enter(self):
        print ('entered main screen')
        if self.ids.spinner_program.text !='Select Program':
            self.list_groups()


    def on_spinner_program(self,spinner_program_text):
        self.program = spinner_program_text
        self.list_groups()




    def prepare_group_data(self):
        global global_group_data_dict

        # print ('get groups for program /n and instructors for each group')

        global_group_data_dict = {}

        if self.filter == 'Form':
            filter = " AND form_batch ='form'"

        elif self.filter == 'Class':
            filter = " AND COALESCE(form_batch, '') <>  'form'"

        else:
            filter = " AND form_batch = 'activity'"

        groups_in_program = DbCon().get_groups_in_program(self.program, filter)

        for group in groups_in_program:
            # attatch instructor_list to dictonary for this group
            global_group_data_dict[group]=  DbCon().get_instructors_for_group(group)

        return global_group_data_dict

    def list_groups(self):
        #print ('display groups for program and associated instructors')
        self.ids.layout_content.clear_widgets()

        global_group_data_dict = self.prepare_group_data()

        for group_name in global_group_data_dict:
            wdg = ClassInstuctorWidget()
            wdg.set_data(group_name, global_group_data_dict[group_name])
            self.ids.layout_content.add_widget(wdg)

    def on_filter(self, text):
        self.filter = text
        self.list_groups()


class Group_Instructors_Screen(Screen):
    """
    Group_Instructors_Screen

    screen layout

    group name label | save button  | cancel button

    add new  button
        instructor widget
        instructor widget
    ---------------------
    on pre entry the add button is dissabled untill screen fully populated

    a widget for each instructor is added to scroll view/boxlayout
    and the widget to a list_of_widgets
    instructors name is added to instructor_init_list
    instructors name is added to instructor_new__list

    on_add_new
    a widget is added to id:layout_contents
    and the widget to a list_of_widgets

    on_remove (called by the child widget)
    remove widget from id:layout_contents
    delete widget from list_of_widgets

    on_save
    iterate through instructor_init_list
    if name not in instructor_new__list
        Delete from table
    else:
        Delete from instructor_new__list

    iterate through any remaining in instructor_new__list
    Insert into table



    """

    layout_input_content = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(Group_Instructors_Screen, self).__init__(**kwargs)

    def on_pre_enter(self):
        print ('pre enter')
        global instructors_init_list, instructors_new_list,instructors_for_group, instructor_widgets
        # make sure all containers are empty
        # clear the screen
        # and disable 'add' button
        instructors_new_list = []# , instructors_new_list
        instructors_init_list = []
        instructors_for_group = []
        instructor_widgets = []
        self.ids.layout_insructors_content.clear_widgets()
        self.ids.btn_add_widget.disabled=True

    def on_enter(self):
        global instructors_init_list, instructors_new_list, instructor_widgets

        instructors_for_group = global_group_data_dict[current_group]
        print ('on_enter ; add a widget for each instructor in group ',current_group,  instructors_for_group)

        for instructor in instructors_for_group:
            self.add_instructor_widget(instructor)
            instructors_init_list.append(instructor)

        print('on enter instructors_init_list= ', instructors_init_list)

        # enable the 'add' button
        self.ids.btn_add_widget.disabled = False


    def add_instructor_widget(self,instructor=''):
        global instructor_widgets
        print ("+ add instructor widget for ", instructor)

        wdg = SelectInstructorWidget()
        wdg.spinner_instructor_name.values = all_instructors

        self.ids.layout_insructors_content.add_widget(wdg)
        instructor_widgets.append(wdg)

        if instructor:
            wdg.id = instructor
            wdg.spinner_instructor_name.values = all_instructors
            wdg.spinner_instructor_name.text = instructor

        return wdg


    def id_generator(self, size=6, chars=string.ascii_letters + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))



    def save(self):
        print ('SAVE')
        """
        prepare instructor_new__list by inspecting widgets in id:layout_contents
        
        iterate through instructor_init_list
        if name not in instructor_new__list
            Delete from table
        else:
            Delete from instructor_new__list
            
        iterate through any remaining in instructor_new__list
        Insert into table
        """

        # prepare instructors_from_wdg_list by inspecting widgets in id:layout_contents
        instructors_from_wdg_list = []

        instructor_widgets = self.ids.layout_insructors_content.children
        for wdg in instructor_widgets:
            name = wdg.ids.spinner_instructor_name.text
            if  name != 'select instructor':
                instructors_from_wdg_list.append(name)

        print ('instructors found in widgets',  instructors_from_wdg_list)

        now = datetime.datetime.now()
        user_email='apwatts@chandrakumala.com' # tempory # use user login email

        new_instuctors_list = []
        # iterate through instructor_init_list
        print('iterate through initial list of instructors ', instructors_init_list)

        keep=[]
        for instructor_name in instructors_init_list:
            print ('an init name')

            if instructor_name in instructors_from_wdg_list:
                keep.append(instructor_name)

            else:
                sql = "DELETE FROM `tabStudent Group Instructor`  \
                        WHERE parent ='%s' \
                          AND instructor_name ='%s'" % (current_group, instructor_name)
                print ('delete ', instructor_name)
                DbCon().exec(sql)

        for instructor_name in instructors_from_wdg_list:
            if instructor_name not in keep:
                sql = "INSERT INTO `tabStudent Group Instructor`  \
                                    (name,  \
                                    creation, modified, \
                                    modified_by, owner, \
                                    parent, instructor_name) \
                           VALUES ( '%s', \
                                    '%s', '%s', \
                                    '%s', '%s', \
                                    '%s', '%s')" % (
                                    self.rnd_number_for_tabStudent_Group_Instructor(),
                                    now,        now,
                                    user_email, user_email,
                                    current_group, instructor_name)

                print('INSERT ', instructor_name)
                DbCon().exec(sql)

        # if no errors
        # on_release: root.manager.current = "main_screen"
        print ('to main screen')
        sm.current = 'main_screen'

    def rnd_number_for_tabStudent_Group_Instructor(self):
        not_rnd = True
        while not_rnd:
            rnd_name = self.id_generator(10)
            sql = "SELECT COUNT(*) as my_count FROM `tabStudent Group Instructor` WHERE name ='%s'" % rnd_name
            not_rnd = DbCon().get_result(sql)[0]['my_count']

        return rnd_name


    def remove_widget(self, wdg):
        global instructor_widgets, instructors_new_list
        print(wdg)
        instructor_name = wdg.ids.spinner_instructor_name.text
        print (' -  Remove Instructor from `new` list', instructor_name)
        if instructors_new_list != 'select instructor':
            instructors_new_list.remove(instructor_name)
        self.ids.layout_insructors_content.remove_widget(wdg)
        instructor_widgets.remove(wdg)





class SelectInstructorWidget(BoxLayout):
    # this widget has a button and a label
    # the label shows the instructors name
    # the button is to remove this widget

    # to do - add a button to show class population
    # on_press open new screen to show students

    def __init__(self, **kwargs):
        super(SelectInstructorWidget, self).__init__(**kwargs)


    def remove_widget(self, instructor):
        self.parent.parent.parent.parent.remove_widget(instructor)


    def instructor_selected(self, instructor_name='xcscs'):
        global instructors_new_list
        # a callback to prevent duplicate name selection
        if instructor_name in instructors_new_list:
            self.ids.spinner_instructor_name.text='select instructor'

        else:
            instructors_new_list.append(instructor_name)#self.ids.spinner_instructor_name.text)
            self.ids.id_input_instructor_name.text = instructor_name

    def filter_spinner(self, text):
        global all_instructors

        print ('filter_spinner ', text)
        # use text to update spinner list with alike entries
        filtered_instrutors = DbCon().get_filtered_instrutors(text)
        print (filtered_instrutors)
        self.ids.spinner_instructor_name.values = filtered_instrutors
        if self.ids.spinner_instructor_name.text not in filtered_instrutors:
            try:
                self.ids.spinner_instructor_name.text = filtered_instrutors[0]

            except:
                self.ids.spinner_instructor_name.text = 'select instructor'

class ClassInstuctorWidget(BoxLayout):
    # a widget that gets added to the screen ,  one for each group in the selected program
    # layout - buttons user to maintain uniform layout
    # btn_1: group_name, btn_2: group_population, btn_3:names_of_instructors

    # btn1 - no effect
    # btn2 - no effect yet - want to switch to screen showing list of students
    # btn3 - switch to edit instructors screen

    instructor_name = StringProperty()
    group_name =  StringProperty()

    def __init__(self, **kwargs):
        self.instructor_name = ''
        self.group_name = ''
        super(ClassInstuctorWidget, self).__init__(**kwargs)


    def on_press_edit(self, lbl_group_name):
        global current_group
        current_group = self.ids.lbl_group_name.text
        print('on_press_edit  current_group=', current_group)


    def set_data(self, group_name, instructors):
        global list_students_in_group
        instructors_joined = ' | '.join(instructors)
        print('set_data: instructors', instructors_joined)

        self.id = group_name
        self.ids.lbl_group_name.text = group_name

        list_students_in_group = DbCon().get_student_for_group(group_name)

        self.ids.btn_student_pop.text = str(len(list_students_in_group))
        self.ids.lbl_instructor_name.text = instructors_joined


    # On button press - Create a popup dialog with a label and a close button
    def on_press_pop(self, group_name):
        layout = GridLayout(cols=1, padding=10)

        closeButton = Button(text="Close the pop-up")

        #list_students_in_group = DbCon().get_student_for_group(group_name)

        data = [{'text': str(i), 'is_selected': False} for i in list_students_in_group]

        args_converter = lambda row_index, rec: {'text': rec['text'],
                                                 'size_hint_y': None,
                                                 'height': 25}

        list_adapter = ListAdapter(data=data,
                                   args_converter=args_converter,
                                   cls=ListItemButton,
                                   selection_mode='single',
                                   allow_empty_selection=True)

        list_view = ListView(adapter=list_adapter)

        closeButton.size_hint= (1, None)
        closeButton.height=40

        layout.add_widget(closeButton)
        layout.add_widget(list_view)




        # Instantiate the modal popup and display
        popup = Popup(title='Demo Popup', content=layout)
        popup.open()

        # Attach close button press with popup.dismiss action
        closeButton.bind(on_press=popup.dismiss)




class GroupStudentsPopupContent(GridLayout):
    pass


class StudentGroupInstructorApp(App):
    def build(self):
        global sm
        root = ScreenManager()
        root.add_widget(Main_Screen(name='main_screen'))
        root.add_widget(Group_Instructors_Screen(name='group_instructors_screen'))

        sm = root
        return root

if __name__ == "__main__":
    StudentGroupInstructorApp().run()