"""
Contains classes and methods relevant to getting and storing weeks during an NFL season.
PLEASE NOTE that using any season not between and including 2013 and 2024 will results in a ValueError.
"""

from datetime import date
from enum import Enum,auto
from math import floor

_2024_season_ended = False

_preseason_start_dates = {
    2000 : 3,
    2001 : 9,
    2002 : 8,
    2003 : 7,
    2004 : 12,
    2005 : 11,
    2006 : 10,
    2007 : 9,
    2008 : 31,
    2009 : 6,
    2010 : 5,
    2011 : 4,
    2012 : 2,
    2013 : 1,
    2014 : 31,
    2015 : 6,
    2016 : 4,
    2017 : 3,
    2018 : 2,
    2019 : 1,
    2020 : 6,
    2021 : 5,
    2022 : 4,
    2023 : 3,
    2024 : 1
}

_regular_season_start_dates = {
    2000 : 2,
    2001 : 8,
    2002 : 6,
    2003 : 3,
    2004 : 8,
    2005 : 7,
    2006 : 6,
    2007 : 5,
    2008 : 3,
    2009 : 9,
    2010 : 8,
    2011 : 7,
    2012 : 6,
    2013 : 5,
    2014 : 3,
    2015 : 9,
    2016 : 7,
    2017 : 6,
    2018 : 5,
    2019 : 4,
    2020 : 9,
    2021 : 8,
    2022 : 7,
    2023 : 6,
    2024 : 4
}

_postseason_start_dates = {
    2000 : 28,
    2001 : 10,
    2002 : 2,
    2003 : 1,
    2004 : 6,
    2005 : 5,
    2006 : 4,
    2007 : 3,
    2008 : 1,
    2009 : 7,
    2010 : 6,
    2011 : 5,
    2012 : 3,
    2013 : 2,
    2014 : 1,
    2015 : 7,
    2016 : 5,
    2017 : 4,
    2018 : 3,
    2019 : 2,
    2020 : 7,
    2021 : 13,
    2022 : 12,
    2023 : 11,
    2024 : 9
}

class WeekType(Enum):
    PRESEASON = 1
    REGULAR = 2
    POSTSEASON = 3

def GetPreseasonStart(year,year_override = False):
    if not isinstance(year,int):
        raise TypeError('Year must be an integer value')
    
    if year < 2013 and not year_override:
        raise ValueError('Year cannot be earlier than 2013')
    
    if year > 2024 and not year_override:
        raise ValueError('Year cannot be later than 2024')

    month = 8
    if year in [2008,2014]:
        month = 7

    day = _preseason_start_dates[year]
    return date(year,month,day)

def GetRegularSeasonStart(year,year_override = False):
    if not isinstance(year,int):
        raise TypeError('Year must be an integer value')
    
    if year < 2013 and not year_override:
        raise ValueError('Year cannot be earlier than 2013')
    
    if year > 2024 and not year_override:
        raise ValueError('Year cannot be later than 2024')
    
    day = _regular_season_start_dates[year]
    return date(year,9,day)

def GetPostseasonStart(year,year_override = False):
    if not isinstance(year,int):
        raise TypeError('Year must be an integer value')
    
    if year < 2013 and not year_override:
        raise ValueError('Year cannot be earlier than 2013')
    
    if year > 2024 and not year_override:
        raise ValueError('Year cannot be later than 2024')
    
    month = 1
    d_year = year
    if year == 2000:
        month = 12
    else:
        d_year += 1

    day = _postseason_start_dates[year]
    return date(d_year,month,day)

def GetRegularSeasonLength(year,year_override = False):
    if year < 2013 and not year_override:
        raise ValueError('Year cannot be earlier than 2013')
    elif 2000 <= year and year < 2021:
        return 17
    elif 2021 <= year and (year < 2025 or year_override):
        return 18
    elif year_override:
        raise ValueError(f'Season length for {year} is not defined')
    else:
        raise ValueError('Year cannot be later than 2024')

def FindNearestWeek(day,year_override = False):
    if not isinstance(day,date):
        raise TypeError('Expected date object')
    
    week_obj = NFLWeek()

    season = day.year
    if (season == 2025 and not _2024_season_ended) or GetPreseasonStart(day.year,year_override) > day:
        season -= 1
    week_obj.SetSeason(season,year_override)

    season_length = GetRegularSeasonLength(season,year_override)
    week = 1 + floor((day - GetRegularSeasonStart(season,year_override)).days / 7)

    if season == 2001 and date(2001,9,11) < day: # the 9/11 check
        week -= 1

    if 0 < week and week <= season_length:
        week_obj.SetWeekType(WeekType.REGULAR)
    elif week <= 0:
        week = 1 + floor((day - GetPreseasonStart(season,year_override)).days / 7)
        if week <= 0 or 4 < week:
            return None
        week_obj.SetWeekType(WeekType.PRESEASON)
    elif season_length < week:
        week = 1 + floor((day - GetPostseasonStart(season,year_override)).days / 7)
        if week <= 0 or 5 < week:
            return None
        week_obj.SetWeekType(WeekType.POSTSEASON)

    week_obj.SetWeekNum(week)

    return week_obj
        

class NFLWeek:
    def __init__(self):
        self.week_num = 1
        self.week_type = WeekType.REGULAR
        self.season = 2013

    def __repr__(self):
        season_type_list = [None,'Preseason','Regular Season','Postseason']
        season_type_index = self.week_type.value
        return f'Week {self.week_num} {season_type_list[season_type_index]} {self.season}'

    def __eq__(self,other):
        if not isinstance(other,NFLWeek):
            raise TypeError('Cannot compare NFLWeek to non-NFLWeek object')
        
        return self.week_num == other.week_num and self.week_type == other.week_type and self.season == other.season
    
    def __ne__(self, other):
        return not (self == other)

    def __int__(self):
        season_length = GetRegularSeasonLength(self.season)

        if self.week_type == WeekType.PRESEASON:
            return 0
        
        if self.week_type == WeekType.REGULAR:
            return self.week_num
        
        return season_length + self.week_num

    def SetWeekNum(self,num):
        if not isinstance(num,int):
            raise TypeError('Week can only be an integer value')
        self.week_num = num

    def SetWeekType(self,type):
        if not isinstance(type,WeekType):
            raise TypeError('Expected WeekType enumerable object')
        self.week_type = type
    
    def SetSeason(self,year,year_override = False):
        if not isinstance(year,int):
            raise TypeError('Year can only be an integer value')
        
        if year < 2013 and not year_override:
            raise ValueError('Year cannot be earlier than 2013')
        
        self.season = year