from dateutil import parser


def date_parse(s):
    ''' sql udf to convert string to date'''
    try:
        t = parser.parse(s, parser.parserinfo(dayfirst=True))
        return t.strftime('%Y-%m-%d')
    except:
        return None