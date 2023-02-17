import requests
from bs4 import BeautifulSoup
import unicodedata

from Semester import Semester
from Course import Course, ScheduleEntry

# for fall
# start date is always the day after labour day
# end date is 
# dec 3, dec 2

class Parser:
    def __init__(self, year, semester, courses_first_day=None, courses_last_day=None) -> None:
        
        if year < 2000:
            raise Exception("Course data is not available prior to 2000.")
        
        self.page = ""
        self.year = year 
        self.semester = semester
        self.courses_first_day = courses_first_day # first day of classes
        self.courses_last_day = courses_last_day    # last day of classes - does not include final exam period
        
        if courses_first_day == None or courses_last_day == None:
            get = get_start_end_dates(year, semester=semester)
            self.courses_first_day = get[0]
            self.courses_last_day = get[1]
            
        
    def loadPageFromFile(self, file_location=None) -> None:
        if file_location == None:
            file_location = f"pages/{self.year}{self.semester}.html"
        
        with open(file_location, "r") as p:
            page = p.read()
            
        self.page = page
    
    def loadPageFromWeb(self, save=True) -> None:
        # todo: make this not hardcoded
        subjects = ["ABST", "ANTH", "APPL", "APSC", "DASH", "AHIS", "ASIA", "ASTR", "BINF", "BIOL", "BCAP", "BUSM", "CNST", "CHEM", "CHIN", "CLST", "COOP", "CMNS", "CPSC", "CSIS", "CJUS", "CRIM", "DANA", "DSGN", "ECED", "ECON", "EDAS", "ENGL", "ENVS", "FLMA", "FMGT", "FINA", "FSRV", "FREN", "GEOG", "GEOL", "GERO", "HSCI", "HIST", "INTB", "EXCH", "JAPN", "JOUR", "KINS", "LATN", "LAMS", "LIBR", "MARK", "MATH", "NURS", "NUTR", "PCCN", "PHIL", "PHED", "PHYS", "POLI", "PHOT", "PSYC", "PUBL", "RECR", "SCIE", "SSRV", "SOCI", "SPAN", "STAT", "THEA", "WMDD", "WMST", "EXPE", "WILX"]

        subjects_data = ""
        for s in subjects:
            subjects_data += f"&sel_subj={s}"

        url = "https://swing.langara.bc.ca/prod/hzgkfcls.P_GetCrse"
        headers = {'Content-type': 'application/x-www-form-urlencoded'}

        data = f"term_in={self.year}{self.semester}&sel_subj=dummy&sel_day=dummy&sel_schd=dummy&sel_insm=dummy&sel_camp=dummy&sel_levl=dummy&sel_sess=dummy&sel_instr=dummy&sel_ptrm=dummy&sel_attr=dummy&sel_dept=dummy{subjects_data}&sel_crse=&sel_title=%25&sel_dept=%25&begin_hh=0&begin_mi=0&begin_ap=a&end_hh=0&end_mi=0&end_ap=a&sel_incl_restr=Y&sel_incl_preq=Y&SUB_BTN=Get+Courses"
        i = requests.post(url, headers=headers, data=data)
        self.page = i.text  
        
        if save:
            self.savePage()
        
    def loadPage(self, save=True) -> None:
        try:
            self.loadPageFromFile()
            print(f"Loaded {self.year}{self.semester} from pages/.")
        except:
            print(f"Downloading {self.year}{self.semester} from langara.ca because no local copy was found.")
            self.loadPageFromWeb(save)
            print(f"Download complete.")
    
    def loadParseSaveAll() -> None:
        for year in range(2000, 2023):
            for semester in range(10, 31, 10):
                p = Parser(year, semester)
                p.loadPage()
                
                s = p.parse()
                s.saveToFile()
                print(s)
        
    def savePage(self, location="pages/", filename=None) -> None:
        if filename == None:
            filename = f"{self.year}{self.semester}.html"
            
        if self.page == "":
            raise Exception("Cannot save empty page.")
        
        with open(location + filename, "w+") as fi:
            fi.write(self.page)
        
    
    def parse(self) -> Semester:
        semester = Semester(self.year, self.semester, self.courses_first_day, self.courses_last_day)
                
        # use BeautifulSoup to change html to Python friendly format
        soup = BeautifulSoup(self.page, 'lxml')

        # "the Course Search For Spring 2023" is the only h2 on the page
        # confirm that term is as expected
        title = soup.find("h2").text.split()

        year = int(title[-1])
        match title[-2]:
            case "Spring":
                term = 10
            case "Summer":
                term = 20
            case "Fall":
                term = 30
                
        if year != self.year or term != self.semester:
            raise Exception(f"Year/semester different than specified: {year}{term}. Expected {self.year}{self.semester}.")

        # get the table with all the courses
        table1 = soup.find("table", class_="dataentrytable")


        # write each entry on the table into a list
        # do not save anything we do not need (headers, lines and courrse headings)
        rawdata:list[str] = []
        for i in table1.find_all("td"):
            
            # remove the grey separator lines
            if "deseparator" in i["class"]: 
                continue
            
            # if a comment is >2 lines, theres whitespace added underneath, this removes them
            if "colspan" in i.attrs and i.attrs["colspan"] == "22":
                continue
            
            # fix unicode encoding
            txt = unicodedata.normalize("NFKD", i.text)
            
            # remove the yellow headers
            if txt == "Instructor(s)":
                rawdata = rawdata[0:-18]
                continue
            
            # remove the header for each course (e.g. CPSC 1150)
            if (len(txt) == 9 and txt[0:4].isalpha() and txt[5:9].isnumeric()):
                continue
            # remove non standard header (e.g. BINF 4225 ***NEW COURSE***)
            if txt[-3:] == "***":
                continue
            
            rawdata.append(txt)

        i = 0
        sectionNotes = None

        while i < len(rawdata)-1:
            
            # some class-wide notes that apply to all sections of a course are put in front of the course (see 10439 in 201110)
            # this is a bad way to deal with them
            # this fails for some cases (ie 20105 in 200710)
            if len(rawdata[i]) > 2:
                # 0 stores the subj and course id (ie CPSC 1150)
                # 1 stores the note and edits it properly
                sectionNotes = [
                    rawdata[i][0:9],
                    rawdata[i][10:].strip()
                ]
                print("NEW SECTIONNOTES:", sectionNotes)
                i += 1
                
            # terrible way to fix off by one error (see 30566 in 201530)
            if rawdata[i].isdigit():
                i -= 1

            current_course = Course(
                RP        = rawdata[i],
                seats     = rawdata[i+1],
                waitlist  = rawdata[i+2], # skip the select column
                crn       = rawdata[i+4],
                subject   = rawdata[i+5],
                course    = rawdata[i+6],
                section   = rawdata[i+7],
                credits   = rawdata[i+8],
                title     = rawdata[i+9],
                add_fees  = rawdata[i+10],
                rpt_limit = rawdata[i+11],
            )
            
            if sectionNotes != None:
                if sectionNotes[0] == f"{current_course.subject} {current_course.course}":
                    current_course.notes = sectionNotes[1]
                else:
                    print("STOPPED ON ", sectionNotes[0], f"{current_course.subject} {current_course.course}")
                    sectionNotes = None
                            
            semester.addCourse(current_course)
            i += 12
            
            while True:
                
                # sanity check
                if rawdata[i] not in [" ", "CO-OP(on site work experience)", "Lecture", "Lab", "Seminar", "Practicum","WWW", "On Site Work", "Exchange-International", "Tutorial", "Exam", "Field School", "Flexible Assessment", "GIS Guided Independent Study"]:
                    raise Exception(f"Parsing error: unexpected course type found: {rawdata[i]}. {current_course} in course {current_course.toJSON()}")
                                        
                c = ScheduleEntry(
                    type       = rawdata[i],
                    days       = rawdata[i+1],
                    time       = rawdata[i+2], 
                    start      = rawdata[i+3], 
                    end        = rawdata[i+4], 
                    room       = rawdata[i+5], 
                    instructor = rawdata[i+6], 
                )
                
                current_course.schedule.append(c)
                i += 7
                
                # if last item in courselist has no note return
                if i > len(rawdata)-1:
                    break
                                
                # look for next item
                j = 0
                while rawdata[i].strip() == "":
                    i += 1
                    j += 1

                # if j less than 5 its another section
                if j <= 5:
                    i -= j 
                    break
                
                # if j is 9, its a note e.g. "This section has 2 hours as a WWW component"
                if j == 9:
                    current_course.notes = rawdata[i].replace("\n", "") # dont save newlines
                    i += 5
                    break
                
                # otherwise, its the same section but a second time
                if j == 12:
                    continue
                
                else:
                    break
   
        return semester



# fall (30) starts in september (09) and ends in november (11) or december (12)
# spring (10) starts in jan (01) and ends in april (04)
# summer (20) starts in may (05) and ends in july(07) or august (08)
def get_start_end_dates(year:int, semester:int) -> tuple[str, str]:
    year = str(year)
    semester = str(semester)
    
    if year+semester not in start_end_dates.keys():
        print(f"Semester start and end dates are not available for given semester ({year}{semester}). Providing best estimate.")
        if semester == "30":
            get = (5, 30)
        if semester == "10":
            get = (4, 6)
        if semester == "20":
            get = (8, 4)
    else:   
        get = start_end_dates[year + semester]
        
    if semester == "30":
        start = "09"
        end = "12" if get[1] < 15 else "11"
    if semester == "10":
        start = "01"
        end = "04"
    if semester == "20":
        start = "05"
        end = "08" if get[1] < 15 else "07"
        
    start = f"{year}-{start}-{get[0]}"
    end = f"{year}-{end}-{get[1]}"
    
    return (start, end)
    
    
    
    

start_end_dates = {
    "201130" : (6, 2),
    "201210" : (4, 5),
    "201220" : (7, 3),
    "201230" : (4, 30),
    "201310" : (3, 9),
    "201320" : (6, 2),
    "201330" : (4, 30),
    "201410" : (3, 4),
    "201420" : (5, 2),
    "201430" : (2, 29),
    "201510" : (5, 8),
    "201520" : (4, 1),
    "201530" : (8, 2),
    "201610" : (4, 6),
    "201620" : (2, 30),
    "201630" : (6, 3),
    "201710" : (3, 5),
    "201720" : (1, 29),
    "201730" : (5, 30),
    "201810" : (2, 9),
    "201820" : (7, 4),
    "201830" : (4, 3),
    "201910" : (2, 4),
    "201920" : (6, 3),
    "201930" : (3, 2),
    "202010" : (6, 3),
    "202020" : (4, 1),
    "202030" : (8, 3),
    "202110" : (6, 8),
    "202120" : (6, 5),
    "202130" : (8, 2),
    "202210" : (6, 7),
    "202220" : (9, 5), 
    "202230" : (6, 2),
    "202310" : (4, 6), 
    "202320" : (8, 4), 
    "202330" : (5, 30),
}