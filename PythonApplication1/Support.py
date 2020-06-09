import time
import datetime

def CollectionToSeparatedString(collection, separator=','):
    list_col = list(collection)
    return separator.join(str(s) for s in list_col)

def ConvertStampToTime(now):
    return datetime.datetime.fromtimestamp(now).strftime('%d.%m.%Y %H:%M:%S')

def CompareDatesFirstLess(date1, date2):
    try:
        d1 = datetime.datetime.strptime(date1, '%d.%m.%Y')
    except :
        d1 = datetime.datetime.fromtimestamp(date1)

    try:
        d2 = datetime.datetime.strptime(date2, '%d.%m.%Y')
    except :
        d2 = datetime.datetime.fromtimestamp(date2)

    return  d1<d2