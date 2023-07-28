import inspect
import json
import logging
import os.path as path
from json import loads
from os import makedirs
from pathlib import Path
import csv
import validators
from bs4 import BeautifulSoup
from pandas import DataFrame, read_csv, concat
from requests import get, HTTPError

logging.basicConfig(format="%(asctime)s - [%(levelname)s]\t%(message)s",
                    datefmt='%d-%b-%y %H:%M:%S')


class DeliverooCrawler:
    @staticmethod
    def url_validator(link: str) -> bool:
        """
        The function validates whether a given string is a valid URL of talabat.com or not
        :rtype: bool
        :param link: A string to be validated as URL or not
        :return: True if URL, else False
        """
        if validators.url(link) and (link.startswith('https://deliveroo.co.uk/')):
            return True
        else:
            return False

    def __init__(self, url: str, data_dir: str, base_dir: str = 'crawled_data',
                 f_name: str = 'crawled_data', menu_dir: str = 'menus', cal_dir: str = 'items_descr_cal') -> None:
        """
        :rtype: None
        :param url: URL for data crawl
        :param base_dir: Directory to save data
        :param menu_dir: Directory to save menus
        :param cal_dir: Directory to save calories data
        """
        self.__flag = True
        self.__details_json = None
        self.__bs4_data = None
        self.__restaurant_name = None
        self.__restaurant = {}
        self.__restaurant_location = {}
        self.__restaurant_menu_details = []

        frame = inspect.stack()[1]
        filename = frame[0].f_code.co_filename
        filepath = Path(path.dirname(filename))

        self.__filename = f_name



        if path.isabs(base_dir):
            self.__base_dir = Path(base_dir)
        else:
            self.__base_dir = filepath / base_dir

        if path.isabs(data_dir):
            self.__data_dir = Path(data_dir)
        else:
            self.__data_dir = filepath / data_dir


        if path.isabs(menu_dir):
            self.__menu_dir = Path(menu_dir)
        else:
            self.__menu_dir = self.__base_dir / menu_dir

        if path.isabs(cal_dir):
            self.__cal_dir = Path(cal_dir)
        else:
            self.__cal_dir = self.__base_dir / cal_dir

        try:
            if self.url_validator(url):
                self.url = url
            else:
                self.url = url
                raise TypeError(f"'{url}' is not a valid URL")

        except TypeError as e:
            self.url = None
            self.__flag = False
            logging.error(e)

        except Exception as e:
            self.url = None
            self.__flag = False
            logging.debug(e)

        # calling other function(s)
        if self.__flag:
            self.__fetch_details()

    def __fetch_details(self):
        # try:
        raw = get(self.url, allow_redirects=True, headers=(
            {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                              '(KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36',
            }
        ))

        status_code = raw.status_code
        reason = raw.reason

        if status_code != 200:
            raise HTTPError(status_code, reason)

        self.__bs4_data = BeautifulSoup(raw.content, 'lxml')

        # call other function(s)
        if self.__flag:
            self.__make_json()
    def __make_json(self):
        # try:
        #     try:
        data = self.__bs4_data.select('#__NEXT_DATA__')[0].text
        self.__details_json = loads(data)

        # call other function(s)
        if self.__flag:
            self.__fetch_restaurant_details()

    def __fetch_restaurant_details(self):

        self.__restaurant = self.__details_json['props']['initialState']['menuPage']['menu']['meta']['restaurant']
        self.__restaurant_name = self.__restaurant['name']
        self.__restaurant_address = self.__restaurant['location']['address']['address1']

        self.__name_address = {
            'name': self.__restaurant_name,
            'address': self.__restaurant_address,
        }

        # call other function(s)
        if self.__flag:
            self.__fetch_restaurant_location()

    def __fetch_restaurant_location(self):
        # try:
        self.__restaurant_location = self.__details_json['props']['initialState']['menuPage']['menu']['meta']['customerLocation']
        self.__lat = self.__restaurant_location['lat']
        self.__lon = self.__restaurant_location['lon']
        self.__city = self.__restaurant_location['city']
        self.__neighborhood = self.__restaurant_location['neighborhood']
        self.__postcode = self.__restaurant_location['postcode']
        self.__cityId = self.__restaurant_location['cityId']
        self.__zoneId = self.__restaurant_location['zoneId']
        self.__geohash = self.__restaurant_location['geohash']

        if self.__flag:
            self.__fetch_restaurant_menu_details()

    def __fetch_restaurant_menu_details(self):

        # try:
        self.__menu = self.__details_json['props']['initialState']['menuPage']['menu']['meta']['items']

        if len(self.__menu) < 1:
            self.__flag = False
            return
    def get_restaurant_name_address(self) -> None | DataFrame:
        if not self.__flag:
            return None
        return DataFrame(self.__restaurant)
    def get_restaurant_location(self) -> None | DataFrame:
        if not self.__flag:
            return None
        return DataFrame(self.__restaurant_location)
    def get_restaurant_menu(self) -> None | DataFrame:
        if not self.__flag:
            return None
        return DataFrame(self.__restaurant_menu_details)

    def convert_file_path(self):
        self.__lowercase_filepath = self.__restaurant_name.lower()
        self.__converted_filepath = self.__lowercase_filepath.replace(' ', '_').replace('-', '_').replace("\t", '_')
        return self.__converted_filepath

    def write_to_csv(self):


        if self.__restaurant:
            self.convert_file_path()
            self.__write_restaurant_name_address_location()


        else:
            logging.error(f'Cannot write into csv')


    def __write_restaurant_name_address_location(self):
        makedirs(self.__base_dir, exist_ok=True)
        filename = self.__base_dir / self.__data_dir / (self.__converted_filepath + '.csv')
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(
                    ['Name', 'Address', 'Latitude', 'Longitude', 'City', 'Neighborhood', 'Postcode', 'City ID',
                     'Zone ID', 'Geohash'])
                writer.writerow(
                    [self.__restaurant_name, self.__restaurant_address, self.__lat, self.__lon, self.__city, self.__neighborhood, self.__postcode, self.__cityId, self.__zoneId,
                     self.__geohash])
                self.__write_restaurant_menu()
        except:
            print(f'{filename} not written to file')
    def __write_restaurant_menu(self):
        #makedirs(self.__menu_dir, exist_ok=True)
        filename = self.__menu_dir / (self.__converted_filepath + '.csv')
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Item Name', 'Item Description', 'Item Price', 'Item Nutritional Info', 'Item Image'])

            for item in self.__menu:
                item_description = None
                if 'description' in item and item['description'] is not None:
                    item_description = item['description']

                self.__nutritional_info = None
                if 'nutritionalInfo' in item and item['nutritionalInfo'] is not None:
                    self.__nutritional_info = item['nutritionalInfo']['energyFormatted']

                    # Write calories labels to file
                    self.__write_cal_to_csv()

                row = [
                    item['name'],
                    item_description,
                    item['price']['formatted'],
                    self.__nutritional_info,
                    item['image']['url'] if 'image' in item and item['image'] is not None else None
                ]
                writer.writerow(row)

    def __write_cal_to_csv(self):
        filename = self.__cal_dir / (self.__converted_filepath + '.csv')
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Item Name', 'Item Description', 'Item Nutritional Info', 'Price', 'Img'])
            for item in self.__menu:
                if 'nutritionalInfo' in item and item['nutritionalInfo'] is not None:
                    nutritional_info = item['nutritionalInfo']['energyFormatted']

                    row = [
                        item['name'],
                        item['description'],
                        nutritional_info,
                        item['price']['formatted'],
                        item['image']['url'] if 'image' in item and item['image'] is not None else None

                    ]
                    writer.writerow(row)
                    #print(row)