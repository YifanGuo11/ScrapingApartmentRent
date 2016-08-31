

url = 'http://www.esring.com/api/v1/properties?api_key=838&include_properties=1&per_page=500&property_group_ids=1428'

dicts_text = rent.make_page_request(url)

aaa = '//universityglenapartments.prospectportal.com/?module=property_info&amp;property[id]=256478&amp;is_responsive_snippet=1&amp;snippet_type=website&amp;is_collapsed=0&amp;'
rent.make_page_request(aaa)

rent.get_property_list()

import json

dicts = json.loads(dicts_text)

dicts['properties'][14].keys()

dicts['properties'][14].values()


url2 = 'http://www.esring.com/casa-granada-los-angeles-ca/check-availability'
source_1 = rent.make_page_request(url2)

from bs4 import BeautifulSoup

soup1 = BeautifulSoup(source_1,'html.parser')

soup_str = str(soup1.find('div',attrs={'class':'column small-12'}).find('iframe'))

import re
from collections import OrderedDict

reg_availability_url = re.compile('src="\s*(.*?)\s*"')

url3 = reg_availability_url.findall(soup_str)

rent.make_page_request(url3)

url4 = 'http://casagranada.prospectportal.com/?module=property_info&property[id]=62519&is_responsive_snippet=1&snippet_type=website&is_collapsed=0&'

source_2 = rent.make_page_request(url4)

soup2 = BeautifulSoup(source_2, 'html.parser')
allfloorplan = soup2.find_all('li',attrs={'class':re.compile('fp-row col-6|fp-row even col-6')})


for plansoup in allfloorplan:
    soup = BeautifulSoup(str(plansoup),'html.parser')
    avail_soup = soup.find(attrs={'data-class':"check-availability"})
    if avail_soup is not None:
        plan = OrderedDict()
        plan['Lease matrix URL'] = avail_soup.attrs['href']
        plan['Name'] = soup.find(title="View More Information").get_text()
        plan['BED / BATH'] = soup.find('div', attrs={'class':"fp-col bed-bath"}).find(attrs={'class':"fp-col-text"}).get_text()
        plan['Rent'] = soup.find('div', attrs={'class':"fp-col rent"}).find(attrs={'class':"fp-col-text"}).get_text()
        plan['Deposit'] = soup.find('div', attrs={'class':"fp-col deposit"}).find(attrs={'class':"fp-col-text"}).get_text()
        plan['sqft'] = soup.find('div', attrs={'class':"fp-col sq-feet"}).find(attrs={'class':"fp-col-text"}).get_text()




mtx_url = 'http:' + str(avail_soup.attrs['href']).replace('&property_floorplan','&action=view_unit_spaces&property_floorplan')
source = rent.make_page_request(mtx_url)
soup= BeautifulSoup(source, 'html.parser')

url = 'http://casagranada.prospectportal.com/?module=check_availability&property[id]=62519&action=view_apartment_amenities&property_floorplan[id]=206510&unit_space[id]=3273657'
source = rent.make_page_request(url)

ddd = [html.get_text() for html in soup.find_all(attrs={'class':'lease-term-price'})]













from rent import Rent
rent = Rent()

rent.get_property_list()
rent.get_property_data()


test = rent.property_list[14]
rent.get_floor_plan_list(test)

rent.make_page_request(test['vanity_url'])