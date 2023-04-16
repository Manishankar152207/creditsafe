
from urllib import request
from django.http import HttpResponseRedirect,JsonResponse,HttpResponse
from django.shortcuts import render,redirect
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt

import requests
import json
import pyodbc
from zeep import Client,helpers
from zeep.transports import Transport
from requests import Session
from requests.auth import HTTPBasicAuth
from enum import Enum
# Create your views here.
countryNameList = ('Slovenia','Germany', 'France', 'UK', 'Ireland', 'Denmark', 'Switzerland', 'Liechtenstein', 'Netherlands', 'Belgium', 'Sweden', 'Finland', 'Norway', 'Portugal', 'Luxembourg', 'Canada', 
'Spain', 'USA', 'Puerto Rico', 'American Samoa', 'Guam', 'Marshall Islands', 'Northern Mariana Islands', 'Palau', 'U.S. Virgin Islands', 'Hungary', 'Czech Republic', 'Poland', 'Slovakia', 'Albania', 'Bosnia and Herzegovina', 'Croatia', 'Macedonia', 'Bulgaria', 'Romania', 'Serbia', 'Latvia', 'Estonia', 'Ukraine', 'Moldova', 'Russia', 'Armenia', 'Azerbaijan', 'Belarus', 'Georgia', 'Kazakhstan', 'Uzbekistan', 'Tajikistan', 'Turkmenistan', 'Kyrgyzstan', 'Comoros', 'Hong Kong', 'Austria', 'Italy', 'Brazil', 'South Korea', 'Mexico', 'New Zealand', 'UAE', 'Burkina Faso', 'Bahrain', 'Benin', 'Democratic Republic of the Congo', 'Egypt', 'Western Sahara', 'Jordan', 'Kuwait', 'Lebanon', 'Oman', 'Palestine', 'Qatar', 'Saudi Arabia', 'Sudan', 'Syria', 'Greece', 'Turkey', 'Colombia', 'Ecuador', 'Venezuela', 'Gambia', 'Australia') 

countryCodeList = ['DE', 'FR', 'GB', 'IE', 'DK', 'CH', 'LI', 'NL', 'BE', 'SE', 'FI', 'NO', 'PT', 'LU', 'CA', 'ES', 'US', 'PR', 'AS', 'GU', 'MH', 'MP', 'PW', 'VI', 'HU', 'CZ', 'PL', 'SK', 'SI', 'AL', 'BA', 'HR', 'MK', 'BG', 'RO', 'RS', 'LV', 'EE', 'UA', 'MD', 'RU', 'AM', 'AZ', 'BY', 'GE', 'KZ', 'UZ', 'TJ', 'TM', 'KG', 'KM', 'HK', 'AT', 'IT', 'BR', 'KR', 'MX', 'PLC', 'NZ', 'AE', 'BF', 'BH', 'BJ', 'CD', 'EG', 'EH', 'JO', 'KW', 'LB', 'OM', 'PS', 'QA', 'SA', 'SD', 'SY', 'GR', 'TR', 'CO', 'EC', 'VE', 'GM', 'AU']
request_data={
            "countries":{
                "CountryCode":[
                    'NL'
                ]        
            },
            "searchCriteria":{
                "Name":{
                    "_value_1":"INTRATUIN TRADE EN LOGISTICS B.V",
                    "MatchType":"MatchBeginning"
                }
            }
        }

class QueryMatchType(Enum): 
    MatchBeginning = 1
    
    MatchBlock = 2

    MatchAnyParts = 3

    MatchWords = 4

    MatchBlockOrWords = 5

    ExactValue  = 6

    ClosestKeywords = 7

def db_connection():
        conn = pyodbc.connect('DRIVER={SQL Server};SERVER=192.168.3.53;PORT=1433;DATABASE=MatrixAsiagateDB;UID=sa;PWD=admin@123456')
        cursor = conn.cursor()
        return cursor

def db_connection_ucs():
        conn = pyodbc.connect('DRIVER={SQL Server};SERVER=192.168.3.53;PORT=1433;DATABASE=TCMNewDB;UID=sa;PWD=admin@123456')
        cursor = conn.cursor()
        return cursor

def get_country_name(cursor, countryC):
        sql=f"select CountryName from CountryShortNames where CountryShortName='{countryC}';"
        try:
            cursor.execute(sql)        
        except:
            return ''
        else:
            res = cursor.fetchall()
            if res:
                return res[0][0]
            else:
                return ''

def get_country_shortname(cursor, country):
        sql=f"select CountryShortName from CountryShortNames where CountryName='{country}';"
        try:
            cursor.execute(sql)        
        except:
            return ''
        else:
            res = cursor.fetchall()
            if res:
                return res[0][0]
            else:
                return ''

def vat_or_registraion(countrycode):
    if countrycode in ['CZ','SK']:
        return {"MatchType":QueryMatchType.MatchBlockOrWords.name}
    elif countrycode in ['PL','NO','CH','ES','IT','FI','SE']:
        return {"MatchType":QueryMatchType.ClosestKeywords.name}
    else:
        return {"MatchType":QueryMatchType.MatchBeginning.name}

def SearchCriteria(countrycode, cname = None):
    if countrycode in ['CZ','SK']:
        return {"_value_1":cname,"MatchType":QueryMatchType.MatchBlockOrWords.name}
    elif countrycode in ['PL','NO','CH','ES','IT','FI','SE']:
        return {"_value_1":cname,"MatchType":QueryMatchType.ClosestKeywords.name}
    else:
        return {"_value_1":cname,"MatchType":QueryMatchType.MatchBeginning.name}

def api_authenticate_and_fetch_company_list(request_data):
    # print(request_data)
    wsdl = "https://webservices.creditsafe.com/GlobalData/1.3/MainServiceBasic.svc/meta?wsdl"
    session = Session()
    session.auth = HTTPBasicAuth("Ucs!nd1A", "Cr3d!t753")
    client = Client(wsdl,transport=Transport(session=session))
    companies = client.service.FindCompanies(**request_data).Companies
    return companies

def payload(companyname,countrycode,companytype):
    request_data = None
    if companytype != "company":
        if companytype == "registration":
            request_data={
                "countries":{
                    "CountryCode":[
                        countrycode
                    ]        
                },
                "searchCriteria":{
                    "Name":vat_or_registraion(countrycode),
                    "RegistrationNumber":companyname
                }
            }
        elif companytype == 'vat':
            request_data={
                "countries":{
                    "CountryCode":[
                        countrycode
                    ]        
                },
                "searchCriteria":{
                    "Name":vat_or_registraion(countrycode),
                    "VatNumber":companyname
                }
            }
    else:
        request_data={
            "countries":{
                "CountryCode":[
                    countrycode
                ]        
            },
            "searchCriteria":{
                "Name":SearchCriteria(countrycode, companyname)
            }
        }
    return request_data
            
def index(request):
    cursor = db_connection()
    countrylist = []
    for cc in countryCodeList:
        cn = get_country_name(cursor, cc)
        if cn:
            countrylist.append({"key":cc, "value":cn})
    return render(request, 'index.html', context={"data":countrylist})

def del_DateOfLatestAccounts(data):
    if data['DateOfLatestAccounts'] == None:
        data['DateOfLatestAccounts'] = ""
        return data
    else:
        date2month = {"01":"Jan","02":"Feb","03":"Mar","04":"Apr","05":"May","06":"Jun","07":"Jul","08":"Aug","09":"Sep","10":"Oct","11":"Nov","12":"Dec"}
        date = str(helpers.serialize_object(data['DateOfLatestAccounts'])).split(" ")[0].split('-')[::-1]
        date[1] = date2month[date[1]]
        date = '-'.join(date)
        data['DateOfLatestAccounts'] = date
        return data

@csrf_exempt 
def fetch_company_list(request):
    companiesList = []
    TotalCompanies = 0
    if request.method == "POST":        
        companyname = request.POST['companyname']
        countrycode = request.POST['countrycode']
        companytype = request.POST['companytype'] if request.POST['companytype'] else "company"
        request_data = payload(companyname,countrycode,companytype)
        companies = api_authenticate_and_fetch_company_list(request_data)  
        if companies != None:            
            companiesList = companies.Company
            companiesList = [ del_DateOfLatestAccounts(helpers.serialize_object(item)) for item in companiesList]
            TotalCompanies = len(companiesList)
        return HttpResponse(json.dumps({"total":TotalCompanies,"companiesList":companiesList,"success":True}),content_type="application/json")
    else:
        return HttpResponse(json.dumps({"success":False}))

@csrf_exempt
def fetch_company_list_db(request):
    message = ""
    if request.method == 'POST':
        regno = request.POST.get('regno', None)
        if regno == None:
            message = "Invalid Registration number"
            return HttpResponse(json.dumps({"message":message,"success":True}),content_type="application/json")
        else:
            data = fetch_from_orgMaster(regno,'Netherlands') #61194654
            if data:
                return HttpResponse(json.dumps({"company":data,"success":True}),content_type="application/json")
            else:
                return HttpResponse(json.dumps({"success":False}),content_type="application/json")


def fetch_from_orgMaster(regno, Country):
    cursor = db_connection_ucs()
    sql = f'''SELECT o.ForFinYear, o.CompanyName,  o.FileNo,  o.CompanyStatus, o.LegalStatus, o.InroporationNo, o.DateOfIncorporation, o.TaxID, o.NoOfEmployees, o.Address, o.City, o.PinCode,o.Country,o.OrgID,o.VerifiedOn,l.purchase_date,l.log_id FROM OrgMaster o left join ucs_cs_logs l ON o.FileNo = l.report_id and l.log_id=(select top 1 log_id from ucs_cs_logs where report_id=o.FileNo order by log_id desc) WHERE REPLACE(REPLACE(REPLACE(o.InroporationNo,'-',''),'/',''),'','') like {regno} and o.Country='{Country}' ORDER BY l.log_id DESC'''
    # print(sql)
    # sql = f"select top 1 * from OrgMaster where InroporationNo={regno}"
    try:
        cursor.execute(sql)        
    except:
        return ''
    else:
        res=cursor.fetchall()
        if res:
            name = res[0][1]
            status = res[0][3]
            registrationnumber = res[0][5]
            vatnumber = 0
            address = res[0][9]
            reportid = res[0][2]
            financialyear = str(res[0][0])
            lastpurchaseddate = str(res[0][15])
            verifiedon = str(res[0][14])
            return {"name":name,"status":status,"regno":registrationnumber,"vatnumber":vatnumber,"address":address,"reportid":reportid,"fy":financialyear,"lpd":lastpurchaseddate,"verifiedon":verifiedon}
        else:
            return ''

@csrf_exempt
def fetch_order_list_db(request):
    if request.method == 'POST':
        return HttpResponse (json.dumps({"orders":fetch_from_OrderInvestigation(),"success":True}),content_type="application/json")
    else:
        return HttpResponse (json.dumps({"success":False}),content_type="application/json")


def fetch_from_OrderInvestigation():
    orderList = []
    cursor = db_connection()
    sql = f"select * from OrderInvestigation where OrderType IN ('UpdateReportRequest','FreshInvestigation') and OrderStatus='0' and Country IN {countryNameList};"
    # print(sql)
    try:
        cursor.execute(sql)        
    except:
        return []
    else:
        res=cursor.fetchall()
        if res:
            for item in res:
                orderList.append({"OrderId":int(item[0]),'Name':item[4],"OrderType":item[2],"regno":item[5],"Address":item[6],"ispdf":item[18],"deldate":item[17] if item[17] else "" ,"country":item[19],"countrycode":get_country_shortname(cursor,item[19])})
            return orderList
        else:
            return []