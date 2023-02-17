from Parser import Parser
from DataExplorer import DataExplorer

# Example usage
p = Parser()
# warning: this will retrieve all 20 years of available course data
# and save the source data and parsed data locally
# this only needs to be run once.
p.loadParseSaveAll()



explorer = DataExplorer()
explorer.loadJSON() # loads json from /json directory

explorer.filterCoursesByCondition("subject", "CPSC")

for s in explorer.semesters:
    print(f"{s.year}{s.semester} Courses: {s.courseCount()}\tUnique Courses: {s.uniqueCoursecount()}")
