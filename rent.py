import sys

reload(sys)
sys.setdefaultencoding('utf-8')

from selenium.webdriver import Firefox
from time import sleep
import csv
import requests
from bs4 import BeautifulSoup
from collections import OrderedDict
import re
from sets import Set
import json
from random import choice, randint
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.webdriver import FirefoxProfile

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)



user_agent_header = {'User-agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36'}


class Rent():
    def __init__(self):
        self.start_url = 'http://www.esring.com/api/v1/properties?api_key=838&include_properties=1&per_page=500&property_group_ids=1428'
        self.session = requests.Session()
        #self.use_selenium = False
        try:
            self.output_data = json.loads(open('apartment_rent_output.json').read())
        except:
            self.output_data = []

    def rand_sleep(self):
        sleep(randint(2, 5))

    def make_page_request(self,url):
       for i in range(10):
            try:
                page_source = self.session.get(url, headers=user_agent_header, verify=False)
                if page_source.status_code == 200: break
            except Exception as e:
                print(1, 'Request error')
            if i == 9: print(1, 'blocked error'); exit()
       return page_source.text

    def get_property_list(self):
        json_page_source = self.make_page_request(self.start_url)
        raw_json_dicts = json.loads(json_page_source)
        raw_property_list = raw_json_dicts['properties']
        self.property_list = []
        for raw_property_dict in raw_property_list:
            property_dict = OrderedDict()
            property_dict['name'] = raw_property_dict['name']
            property_dict['address'] = raw_property_dict['address']
            property_dict['city'] = raw_property_dict['city']
            property_dict['state'] = raw_property_dict['state']
            property_dict['zip'] = raw_property_dict['zip']
            property_dict['marketing_phone'] = raw_property_dict['marketing_phone']
            property_dict['vanity_url'] = 'http://www.esring.com/' + raw_property_dict['slug'] + '/check-availability'
            self.property_list.append(property_dict)

        return self.property_list

    def get_property_data(self):
        self.property_list_full = []
        for index, property in enumerate(self.property_list):
            self.property_list_full.append(self.get_floor_plan_list(property))
            #print('Finished Property' + index)
            output_json = open('rent_output.json','w')
            output_json.write(json.dumps(self.property_list_full, indent=4))



    def get_floor_plan_list(self,property_data):
        property_url_source = self.make_page_request(property_data['vanity_url'])
        property_avail_soup = BeautifulSoup(property_url_source,'html.parser')
        property_data_full = property_data
        property_data_full['property_url'] = property_avail_soup.find('div',attrs={'class':'column small-12'}).find('iframe').attrs['src']
        property_data_full['floor_plan_list'] = self.parse_floor_plan_list(property_data['property_url'])
        return property_data_full


    def parse_floor_plan_list(self,property_url):
        floor_plan_source = self.make_page_request(property_url)
        soup = BeautifulSoup(floor_plan_source,'html.parser')
        all_floor_plan = soup.find_all('li',attrs={'class':re.compile('fp-row col-6|fp-row even col-6')})
        floor_plan_list = []
        for plansoup in all_floor_plan:
            soup = BeautifulSoup(str(plansoup),'html.parser')
            avail_soup = soup.find(attrs={'data-class':"check-availability"})
            if avail_soup is not None:
                plan = OrderedDict()
                plan['Available units URL'] = 'http:' + str(avail_soup.attrs['href']).replace('&property_floorplan','&action=view_unit_spaces&property_floorplan')
                plan['Name'] = soup.find(title="View More Information").get_text()
                plan['BED / BATH'] = soup.find('div', attrs={'class':"fp-col bed-bath"}).find(attrs={'class':"fp-col-text"}).get_text()
                plan['Rent'] = soup.find('div', attrs={'class':"fp-col rent"}).find(attrs={'class':"fp-col-text"}).get_text()
                plan['Deposit'] = soup.find('div', attrs={'class':"fp-col deposit"}).find(attrs={'class':"fp-col-text"}).get_text()
                plan['sqft'] = soup.find('div', attrs={'class':"fp-col sq-feet"}).find(attrs={'class':"fp-col-text"}).get_text()
                plan['unit lease'] = self.parse_lease_matrix(plan['Available units URL'])
                floor_plan_list.append(plan)
        return floor_plan_list

    def parse_lease_matrix(self,available_units_url):
        unit_id_source = self.make_page_request(available_units_url)
        unit_id_soup = BeautifulSoup(unit_id_source, 'html.parser')
        unit_id_list = unit_id_soup.find_all(attrs={'class':"unit-button"})

        unit_list = []
        for index, unit_id_tags in enumerate(unit_id_list):
            unit = OrderedDict()
            unit['unit_id'] = unit_id_tags.attrs['rel'][0]
            unit['Unit lease matrix url']= available_units_url + '&action=view_apartment_amenities&unit_space[id]=' + unit['unit_id']
            lease_matrix_source = self.make_page_request(unit['Unit lease matrix url'])
            soup = BeautifulSoup(lease_matrix_source, 'html.parser')
            unit['Lease Rent'] = [html.get_text() for html in soup.find_all(attrs={'class':'lease-term-price'})]
            unit['Lease Term'] = [html.get_text() for html in soup.find_all(attrs={'class':'lease-term-length'})]
            #print('Unit' + index)
            unit_list.append(unit)

        return unit_list



