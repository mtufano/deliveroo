import logging
import os
import validators
import json
from bs4 import BeautifulSoup
from pandas import DataFrame
from requests import get, HTTPError

# Basic logging configuration
logging.basicConfig(format="%(asctime)s - [%(levelname)s]	%(message)s", datefmt='%d-%b-%y %H:%M:%S')

class DeliverooCrawler:
    SUCCESS_STATUS_CODE = 200

    def __init__(self, url: str, f_name: str, end_dir: str = '', menu_dir: str = 'menus'):
        self.__details_json = None
        self.__bs4_data = None
        self.__restaurant = {}
        self.__restaurant_location = {}
        self.__restaurant_menu_details = []

        self.base_dir = os.path.join(f_name, end_dir)
        self.end_dir_location = os.path.join(f_name, end_dir, "location")
        self.menu_dir = os.path.join(f_name, end_dir, menu_dir)
        self.cal_dir = os.path.join(f_name, end_dir)

        self.__create_directories([self.base_dir, self.end_dir_location, self.menu_dir])

        if not self.__url_validator(url):
            logging.error(f"'{url}' is not a valid URL")
            self.__flag = False
            return

        self.__flag = True
        self.url = url
        self.__fetch_details()

    @staticmethod
    def __url_validator(link: str) -> bool:
        return validators.url(link) and link.startswith('https://deliveroo.ae/')

    @staticmethod
    def __create_directories(directories):
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
                logging.info(f"Directory '{directory}' created successfully.")

    def __fetch_details(self):
        try:
            response = get(self.url, allow_redirects=True, headers=self.__get_headers())
            if response.status_code != self.SUCCESS_STATUS_CODE:
                raise HTTPError(response.status_code, response.reason)

            self.__bs4_data = BeautifulSoup(response.content, 'lxml')
            self.__make_json()

        except HTTPError as e:
            logging.error(f"HTTP error occurred: {e}")
            self.__flag = False
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            self.__flag = False

    @staticmethod
    def __get_headers():
        return {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36'
        }

    def __make_json(self):
        try:
            data = self.__bs4_data.select_one('#__NEXT_DATA__').text
            self.__details_json = json.loads(data)
            self.__fetch_restaurant_details()
        except Exception as e:
            logging.error(f"Error in parsing JSON: {e}")
            self.__flag = False

    def __fetch_restaurant_details(self):
        try:
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
        except:
            pass
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
        #self.create_directory(self.end_dir_location)
        filename = os.path.join(self.end_dir_location, self.__converted_filepath + '.csv')

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
        #makedirs(self.menu_dir, exist_ok=True)
        filename = os.path.join(self.menu_dir, self.__converted_filepath + '.csv')
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
        #makedirs(self.cal_dir, exist_ok=True)
        filename = os.path.join(self.cal_dir, self.__converted_filepath + '.csv')
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