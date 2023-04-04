import os
import json

from Semester import Semester
from Course import Course, ScheduleEntry

class DataExplorer:
    def __init__(self):
        self.semesters:list[Semester] = []   
        
    def filterCoursesByCondition(self, value="subject", filter="CPSC", invert=False):
        for s in self.semesters:
            
            delete = []
            for c in s.courses:
                # horrible code to invert the condition
                # there has to be a better way to do this
                if not invert:
                    if c.__dict__[value] != filter:
                        delete.append(c)
                else: 
                    if c.__dict__[value] == filter:
                        delete.append(c)
                        
            for c in delete:
                s.courses.remove(c)
    
    def coursesSummary(self):
        print("Summary: ")
        for s in self.semesters:
            print(f"{s.year}{s.semester} Courses: {s.courseCount()}\tUnique Courses: {s.uniqueCoursecount()}")

    
    # pass e.g. 202310 to only get 202310
    def loadJSON(self, *semesters:str) -> list[Semester]:
        files = os.listdir("json/")
        
        data = []
        
        if len(semesters) > 0:
            for s in semesters:
                with open(f"json/{s}.json") as fi:
                    d = json.loads(fi.read())
                    data.append(d)
        else:
            for fi in files:
                # "ignore" other json files
                if len(fi) != 11:
                    continue
                
                with open(f"json/{fi}") as fi:
                    d = json.loads(fi.read())
                    data.append(d)
                    
        
        for s in data:
        
            sem = Semester(
                s["year"],
                s["semester"],
                s["courses_first_day"],
                s["courses_last_day"]
                )   
            
            self.semesters.append(sem)
            
            for c in s["courses"]:
                course = Course(
                    c["RP"],
                    c["seats"],
                    c["waitlist"],
                    c["crn"],
                    c["subject"],
                    c["course"],
                    c["section"],
                    c["credits"],
                    c["title"],
                    c["add_fees"],
                    c["rpt_limit"],
                    c["notes"]
                )
                sem.addCourse(course)
                
                for sc in c["schedule"]:
                      schedule = ScheduleEntry(
                          sc["type"],
                          sc["days"],
                          sc["time"],
                          sc["start"],
                          sc["end"],
                          sc["room"],
                          sc["instructor"]
                      )
                      course.schedule.append(schedule)
              