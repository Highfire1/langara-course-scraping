from Parser import Parser

# Example usage

# load page with parser
# will first look for page locally, then fetch year from webpage
parser = Parser(2023, 10)
parser.loadPage()

# parses the webpage
semester = parser.parse()
print(semester)

# save the result to a json file
semester.saveToFile()


