from datetime import date

class Date:
    def __init__(self):
        self.day = None
        self.month = None
        self.year = None
    
    def SetDate(self,year,month,day):
        self.year = year
        self.month = month
        self.day = day

    def SetToday(self):
        date_elements = [int(x) for x in str.split(str(date.today()),'-')]
        self.year = date_elements[0]
        self.month = date_elements[1]
        self.day = date_elements[2]

    def mlb_str(self):
        return f"{self.year}-{self.month:02d}-{self.day:02d}"