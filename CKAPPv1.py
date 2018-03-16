# app name
import kivy

from kivy.app import App
from kivy.properties import ObjectProperty, StringProperty
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen, ScreenManager

from dbcon import DbCon
import datetime

instructor = ''
student_and_absence_dict = {}
current_date = ''
student_group = ''
sm =''

class ScreenLogin(Screen):
    def press_login(self, username, password):
        global instructor

        """
        check login details
        
        if ok open app
        
        else:
            popup 'there seems to be a problem please try again'
            
            
        """
        # print (username, password)
        # if password and username:
        try:
            x = DbCon.check_user_password(username, password)
            print (x)
            instructor = username
        #         sm.current = "screen_main"
        #
        #     else:
        #         print("# popup not found")
        #
        # else:
        #     print("popup 'field missing'")
        except:
            instructor = 'david.gordon' # for testing
        sm.current = "screen_main"


class StudentWidget(BoxLayout):
    stud = StringProperty('')

    def __init__(self, **kwargs):
        super(StudentWidget, self).__init__(**kwargs)

    def set_data(self, row):
        print ('set student widget data ', row)

        student_name = row['student_name']
        group_att    = row['group_att']
        form_att     = row['form_att']

        self.ids.swgd_1_student_name.text = student_name

        if form_att=='Present':
            self.ids.swgd_1_student_name.color = (1, 1, 1, 1)
        else:
            self.ids.swgd_1_student_name.color = (1, .7, 1, 0.7)

        if group_att=='Present':
            self.ids.cb_a_group.state = 'down'

        else:
            self.ids.cb_a_group.state = 'normal'

    def setState(self, state):
        self.ids.cb_a_group.state = state

    def on_select_one(self):
        global student_and_absence_dict


        wdg = student_and_absence_dict[self.stud]['wdg']
        #wdg.setState('down')

        data = student_and_absence_dict[self.stud]
        state = data['group_att']
        if state == 'Present':
            state = 'Absent'
        else:
            state = 'Present'

        data.update({'group_att': state})
        student_and_absence_dict.update({self.stud: data})


class ScreenMain(Screen):
    layout_content = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(ScreenMain, self).__init__(**kwargs)
        self.layout_content.bind(minimum_height=self.layout_content.setter('height'))

    def on_select_all(self):
        self.change_state('Present')

    def change_state(self, state):
        global student_and_absence_dict
        for key in student_and_absence_dict:
            data = student_and_absence_dict[key]
            data.update({'group_att': state})
            student_and_absence_dict.update({key: data})
            wdg = student_and_absence_dict[key]['wdg']
            if state == 'Present':
                wdg.setState('down')
            else:
                wdg.setState('normal')

    def on_select_none(self):
        self.change_state('Absent')

    def on_submit(self):
        for stud in student_and_absence_dict:
            state = student_and_absence_dict[stud]['group_att']
            student_name = student_and_absence_dict[stud]['student_name']
            DbCon().upsert(state, stud, student_name, current_date, student_group)

    def on_enter(self):
        global instructor
        self.ids.lbl2.text = str(instructor)
        self.spinner_values = ('none',)
        self.ids.spinner_id.values = ['Select Class', ]
        self.ids.spinner_id.text = "Select Class"

        self.ids.layout_content.clear_widgets()

        try:
            student_groups_list = []
            # student_groups = DbCon().get_student_groups(GlobalShared.INSTRUCTOR)
            student_groups = DbCon().get_student_groups(instructor)

        except:
            print("S")

        try:
            for group in student_groups:
                student_groups_list.append(group['parent'])

            self.ids.spinner_id.values = tuple(student_groups_list)

        except:
            print("for group in student_groups fail")

    def list_students(self):
        global student_and_absence_dict
        self.ids.layout_content.clear_widgets()
        for STUD in student_and_absence_dict:
            row = student_and_absence_dict[STUD]
            wdg = StudentWidget()
            wdg.stud = STUD
            student_and_absence_dict[STUD]['wdg'] = wdg
            wdg.set_data(row)
            self.ids.layout_content.add_widget(wdg)

    def on_spinner_clicked(self, group_name):
        global current_date, student_group

        current_date = datetime.date.today()
        student_group = group_name
        # get student attendance
        #try:
        res = DbCon().get_students_and_absence_for_group(student_group)
        print ('get_students_and_absence_for_group ', student_group, "  ", res)

        for row in res:
            STUD = row['student']
            student_name = row['student_name']
            g_form = DbCon().get_form_group(STUD)
            f_att  = DbCon().get_attendance(STUD, g_form, current_date)

            g_att  = DbCon().get_attendance(STUD, group_name, current_date)

            student_and_absence_dict[STUD] = {'form_att': f_att, 'student_name': student_name, 'group_att': g_att}

        #except:
        #    student_and_absence_dict={}
        #    print('failed to get student attendance')

        self.list_students()


class CKAPPv1(App):
    sm = ScreenManager()
    Window.size = (600, 900)

    def build(self):
        global sm
        sm = CKAPPv1.sm
        sm.add_widget(ScreenLogin(name='screen_login'))
        sm.add_widget(ScreenMain(name='screen_main'))
        return sm


if __name__ == '__main__':
    CKAPPv1().run()

