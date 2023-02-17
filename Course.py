import json

class Course:
    def __init__(self, RP:str, seats:str, waitlist:str, crn:str, subject:str, course:str, section:str, credits:str, title:str, add_fees:str, rpt_limit:str, notes=None):
        
        self.RP = RP               # whether the course has restrictions ie blank, R, or P
        self.seats = seats         # num. of seats available in course
        self.waitlist = waitlist   # num. of people on waitlist
        self.crn = crn             # 5 digit id of course
        self.subject = subject     # 4 letter subject code
        self.course = course       # 4 digit course id
        self.section = section     # Section id (0 = inperson, M = mixed, W = online)
        self.credits = credits     # amount of credits course is worth
        self.title = title         # title of course (ie "Intro. to Web Programming")
        self.add_fees = add_fees   # additional fees of course
        self.rpt_limit = rpt_limit # num. on repeat limit of course
        
        self.notes = notes         # notes on the course (ie "CPSC 1050 section M01 will also meet for 2 hours per week as a WWW component.")
                                   # times when the course is scheduled
        self.schedule:list[ScheduleEntry] = []
    
    def __str__(self):
        return f"Course: {self.subject} {self.course} CRN: {self.crn}"
    
    def toJSON(self):
        return str(self.__dict__)
    
    
class ScheduleEntry:
    def __init__(self, type:str, days:str, time:str, start:str, end:str, room:str, instructor:str):
        self.type = type                # type of entry (ie Lecture, Lab, Exam, etc)
        self.days = days                # days this entry runs (ie M-W----)
        self.time = time                # time this entry runs (ie 1030-1230)
        self.start = convertDate(start) # date course starts (ie " " or "11-Apr-23")
        self.end = convertDate(end)     # date course ends (ie " " or "11-Apr-23")
        self.room = room                # room entry is in (ie A254)
        self.instructor = instructor    # instructor for entry (ie "Tom Jones")
        
    def __str__(self):
        return json.dumps(self.__dict__)
    
    def toJSON(self):
        return json.dumps(self.__dict__)

# converts date from "11-Apr-23" to "2023-04-11"
def convertDate(date:str):
    if len(date) != 9:
        return date
    
    date = date.split("-")
    months = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
    return f"20{date[2]}-{months.index(date[1].lower())}-{date[0]}"
    