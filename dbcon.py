import pymysql

class DbCon:
    def __init__(self):
        print('try to connect')
        try:
            self.db = pymysql.connect(host="110.232.86.18",
                                      user='root',
                                      password='test',
                                      db='6eed585e681402fb',
                                      charset='utf8mb4',
                                      cursorclass=pymysql.cursors.DictCursor)
            self.c = self.db.cursor()
        except:
            print ('connection failed')



    def check_user_password(self, user='', password=''):
        # because ......
        # we have to make a new connection here
        db = pymysql.connect(host="110.232.86.18",
                                  user='root',
                                  password='test',
                                  db='6eed585e681402fb',
                                  charset='utf8mb4',
                                  cursorclass=pymysql.cursors.DictCursor)
        c = db.cursor()

        sql = "SELECT * FROM tabInstructor WHERE instructor_name='%s' AND _comments='%s'" % (user, password)
        c.execute(sql)
        res = c.fetchall()
        return len(res)==1

    def get_programs(self, search=""):
        return  self.get_result("SELECT * FROM tabProgram")

    def get_instructor(self, search=""):
        sql = "SELECT * FROM tabInstructor WHERE name = '%s'" % search
        return  self.get_result(sql)#self.c.fetchall()

    def get_student_groups(self, instructor):
        sql = "SELECT parent \
                 FROM `tabStudent Group Instructor` \
                WHERE instructor_name = '%s' ORDER BY parent" % instructor
        #self.c.execute(sql)
        return  self.get_result(sql)#self.c.fetchall()

    def get_students_for_group(self, group_name):
        sql = "SELECT student_name \
                 FROM `tabStudent Group Student`  \
                WHERE parent = '%s' ORDER BY student_name" % group_name

        #self.c.execute(sql)
        return  self.get_result(sql)#self.c.fetchall()

    def get_form_group(self, student):
        sql = "SELECT sg.name \
                 FROM `tabStudent Group Student` sgs \
                 JOIN `tabStudent Group` sg \
                   ON sgs.parent=sg.name \
                WHERE sgs.student= '%s' \
                  AND sg.form_batch = 'form'" % student
        #self.c.execute(sql)
        res =  self.get_result(sql)#self.c.fetchall()
        if res:
            form_name = (res[0]['name'])
            print ('form_name=', form_name)
            return form_name
        else:
            print ('error this student has no form')

    def upsert(self, state, stud, student_name, current_date, student_group):
        sql = "SELECT COUNT(*) \
                 FROM `tabStudent Attendance` \
                WHERE student='%s' AND date='%s' AND student_group ='%s'" % (
                      stud, current_date, student_group)
        self.c.execute(sql)
        cnt = self.c.fetchall()[0]['COUNT(*)']
        now = datetime.datetime.now()

        sql  = "SELECT MAX(name) FROM `tabStudent Attendance`"
        #self.c.execute(sql)
        res = self.get_result(sql)#self.c.fetchall()
        x = res[0]['MAX(name)'][-4:]
        next_number = int(x)+1
        formated_number = '{:06.0f}'.format(next_number)
        name = 'SA%s' % formated_number

        if cnt == 1:
            print ('exists # update')
            sql = "UPDATE `tabStudent Attendance` \
                      SET status='%s', modified='%s' \
                    WHERE student='%s' AND date='%s' AND student_group ='%s' " % (
                          state, now,
                          stud, current_date, student_group)

        elif cnt==0:  #
            user_email = "%s@chandrakumala.com" % instructor
            sql = "INSERT INTO `tabStudent Attendance` \
                               (name, status, \
                                creation, modified, \
                                modified_by, owner, \
                                student, student_name, \
                                date, student_group) \
                        VALUES ('%s', '%s', \
                                '%s', '%s', \
                                '%s', '%s', \
                                '%s', '%s',\
                                '%s', '%s')" % (
                                name, state, now, now,
                                user_email, user_email,
                                stud, student_name,
                                current_date, student_group)

        else:
            print ('error - identical record ' , sql)

        self.c.execute(sql)
        self.db.commit()


    def get_attendance(self, student, group_name, current_date):
        sql = "SELECT status \
                 FROM `tabStudent Attendance` \
                WHERE student_group = '%s' \
                  AND student='%s' \
                  AND date='%s'" % (group_name, student, current_date)
        self.c.execute(sql)
        res = self.c.fetchone()
        print ('get_attendance ',sql, res)
        if res:
            return res['status']

        else:
            return 'Absent'

    def get_students_and_absence_for_group(self, group_name):
        global student_and_absence_dict
        print ('get_students_and_absence_for_group  | group_name =', group_name)
        student_and_absence_dict = {}

        sql = "SELECT student, student_name \
                 FROM `tabStudent Group Student` \
                WHERE parent = '%s' ORDER BY student_name" % group_name

        #self.c.execute(sql)
        res = self.get_result(sql)#self.c.fetchall()
        return res

    def get_result(self, sql=""):
        self.c.execute(sql)
        return self.c.fetchall()


    def get_programs(self):
        sql = "SELECT name FROM `tabProgram` WHERE idx>0 ORDER BY idx"
        return self.get_list(sql, 'name')

    def get_all_instrutors(self):
        sql = "SELECT instructor_name FROM tabInstructor"
        return self.get_list(sql, 'instructor_name')


    def get_filtered_instrutors(self, text):
        sql = "SELECT instructor_name FROM tabInstructor \
                WHERE instructor_name LIKE " + "'%" + text + "%'"
        print (sql)
        # return self.get_result(sql)
        return self.get_list(sql, 'instructor_name')



    def get_instructors_for_group(self, group):
        sql = "SELECT instructor_name \
                 FROM `tabStudent Group Instructor` \
                WHERE parent='%s'" % group
        #return self.get_result(sql)
        return self.get_list(sql, 'instructor_name')


    def get_student_for_group(self, group_name):
        sql = "SELECT sgs.student_name FROM `tabStudent Group Student` sgs \
                 JOIN `tabStudent Group` sg ON sg.name = sgs.parent \
                WHERE sg.name ='%s' AND academic_year='%s' " % (group_name, '2017-18')

        return self.get_list(sql, 'student_name')



    def get_groups_in_program(self, program, filter):
        sql = "SELECT name FROM `tabStudent Group` \
                        WHERE program='%s' %s" % (program, filter)
        return self.get_list(sql, 'name')


    def get_list(self, sql, field_name):
        mylist=[]
        #self.c.execute(sql)
        res = self.get_result(sql)#self.c.fetchall()
        for row in res:
            mylist.append(row[field_name])

        return mylist


    def exec(self, sql):
        self.c.execute(sql)
        self.db.commit()

