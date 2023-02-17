import datetime
import json

from Course import Course

class Semester:
    def __init__(self, year, semester, courses_first_day:str=None, courses_last_day:str=None):
        self.datetime_retrieved = datetime.datetime.utcnow().strftime("%Y-%m-%d")
        self.year = year 
        self.semester = semester
        self.courses_first_day = courses_first_day # first day of classes
        self.courses_last_day = courses_last_day    # last day of classes - does not include final exam period
        
        self.courses:list[Course] = [] 
        
    def addCourse(self, course:Course):
        self.courses.append(course)
    
    def courseCount(self):
        return len(self.courses)
    
    def uniqueCoursecount(self):
        uniques = []
        for c in self.courses:
            if f"{c.subject} {c.course}" not in uniques:
                uniques.append(f"{c.subject} {c.course}")
        return len(uniques)


    def __str__(self):
        s =  f"Semester data for {self.year}{self.semester}:\n"
        s += f"{self.courseCount()} sections & "
        s += f"{self.uniqueCoursecount()} unique sections.\n"
        return s
    
    def toJSON(self):
        js = {
            "datetime_retrieved" : self.datetime_retrieved,
            "year" : self.year,
            "semester" : self.semester,
            "courses_first_day" : self.courses_first_day,
            "courses_last_day" : self.courses_last_day,

            "courses" : self.courses
        }
        
        return json.dumps(js, default=vars, indent=4)
    
    def saveToFile(self, location="json/", filename = None):
        if filename == None:
            filename = f"{self.year}{self.semester}.json"
            
        with open(location + filename, "w+") as fi:
            fi.write(self.toJSON())
    