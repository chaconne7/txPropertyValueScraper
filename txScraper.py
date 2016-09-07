import csv
import requests
import re
from BeautifulSoup import BeautifulSoup

indexUrl = "http://comptroller.texas.gov/propertytax/administration/pvs/findings/2013f/"
response = requests.get(indexUrl)
html = response.content
#print html

soup = BeautifulSoup(html)
#print soup.prettify()

table = soup.table
#print table

list_of_rows = []

#header row in spreadsheet
list_of_cells = ["countyName", "districtName", "totalAssessedValue", "totalSecuredAssessedValue"]
list_of_rows.append(list_of_cells)

#loop through each CAD, collect data from district links on each CAD page
for row in table.findAll("tr"):
    for col in row.findAll("td"):
        for countyLink in col.findAll("a", href = True):
            url = 'http://comptroller.texas.gov/propertytax/administration/pvs/findings/2013f/{}'.format(countyLink['href'])
            countyResponse = requests.get(url)
            countyHTML = countyResponse.content
            countySoup = BeautifulSoup(countyHTML)
            cadSection = countySoup.find("div", {"id": "content"})
            cadHeaderSection = cadSection.find("div", {"id": "fullPage"})
            cadHeaderName = cadHeaderSection.h1.string
            indented = cadHeaderSection.find("div", {"class": "indented"})
            
            # loop through each school district within the CAD
            for schoolDistrictLink in cadSection.findAll("h2"):
             
                list_of_cells = []
                L1, L2, M, S = 0, 0, 0, 0;

                # append county name
                list_of_cells.append(cadHeaderName);
                urlString = schoolDistrictLink.findNext("ul").li.a['href']
                districtURL = 'http://comptroller.texas.gov/propertytax/administration/pvs/findings/2014f/{}'.format(urlString)
                districtResponse = requests.get(districtURL)
                districtHTML = districtResponse.content
                districtSoup = BeautifulSoup(districtHTML)
                
                # append district name 
                districtSection = districtSoup.find("div", {"id": "content"})
                districtHeaderName = districtSection.find("h2").findNext("h2")
                list_of_cells.append(districtHeaderName.string)
                print(districtHeaderName.string)
                # append total valuation
                valueTable = districtSection.findNext("table")
                totalValuationRow = valueTable.findAll("tr", recursive=False)[19]
                totalValuation = str(totalValuationRow.findAll("td", recursive=False)[3].text)
                totalValuation = int(re.match("([0-9,]*)(?: )", totalValuation).group(0).replace(",",""))
                # print("Total Valuation: " + str(totalValuation))
                list_of_cells.append(totalValuation);

                # append total secured valuation
                L1Row = valueTable.findAll("tr", recursive=False)[11]
                L1 = L1Row.findAll("td", recursive=False)[3].text.replace(",","")
                L1 = 0 if L1 == "" else int(L1)
                # print("L1: " + str(L1))
                L2Row = valueTable.findAll("tr", recursive=False)[12]
                L2 = L2Row.findAll("td", recursive=False)[3].text.replace(",","")
                L2 = 0 if L2 == "" else int(L2)
                # print("L2: " + str(L2))
                MRow = valueTable.findAll("tr", recursive=False)[13]
                M = MRow.findAll("td", recursive=False)[3].text.replace(",","")
                M = 0 if M == "" else int(M)
                SRow = valueTable.findAll("tr", recursive=False)[16]
                # print ("M: " + str(M))
                S = SRow.findAll("td", recursive=False)[3].text.replace(",","")
                S = 0 if S == "" else int(S)
                # print("S: " + str(S))
                totalSecuredValuation = totalValuation - L1 - L2 - M - S;
                # print("Total Secured Valuation: " + str(totalSecuredValuation))
                list_of_cells.append(totalSecuredValuation)

                # append row of district information to spreadsheet
                list_of_rows.append(list_of_cells)
                
outfile = open("./txPropertyValues2013.csv", "wb")
writer = csv.writer(outfile)
writer.writerows(list_of_rows)


