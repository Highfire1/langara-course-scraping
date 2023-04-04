from Parser import Parser
from DataExplorer import DataExplorer

import sys


#p = Parser(2023, 10)
#p.loadPage()
#p.parseAndSave()

# warning: this will retrieve all 20 years of available course data
# and save the source data and parsed data locally
# this only needs to be run once.
Parser.loadParseSaveAll()

sys.exit()


explorer = DataExplorer()
explorer.loadJSON() # loads json from /json directory
explorer.coursesSummary()

#explorer.filterCoursesByCondition("subject", "CPSC")

for s in explorer.semesters:
    for c in s.courses:
        print(c)