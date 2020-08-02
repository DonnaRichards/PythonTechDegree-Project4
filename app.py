from collections import OrderedDict
import csv
import sys
import os
import re
from datetime import datetime

from peewee import *

db = SqliteDatabase('inventory.db')

class Product(Model):
    # content
    product_id = AutoField()
    product_name = CharField()
    product_quantity = IntegerField()
    product_price = IntegerField()
    date_updated = DateTimeField()
    
    class Meta:
        database = db


def initialize():
    ''' Create DB and table if they don't exist '''
    db.connect()
    db.create_tables([Product], safe=True)
    load_data_from_csv()


def load_data_from_csv():
    ''' Load data from csv file inventory.csv to database '''
    try:
        with open('./inventory.csv') as csvfile:
            product_list = csv.DictReader(csvfile, delimiter=',')
            for product in product_list:
                product['product_price'] = format_price_str_to_int(product['product_price'])
                product['date_updated'] = format_date_str_to_datetime(product['date_updated'])
                add_record_to_db(product)
    except FileNotFoundError:
        print('inventory.csv file not found, no current data loaded to database')


def format_price_str_to_int(pricestr):
    ''' Update price field in string format to int format nnnnn '''
    # check string only contains digits plus max one $ and one .
    if '.' in pricestr:
        return int(re.sub('[\$\.]', '', pricestr))
    else:
        # if the string did not contain . , assuming just a dollar value,
        # multiply by 100 to convert to cents.
        return int(re.sub('[\$]', '', pricestr)) * 100


def format_price_int_to_str(price):
    ''' Update price field in int format nnnnn to string $nnn.nn'''
    pricestr = str(price)
    if len(pricestr) == 1:
        return '$0.0' + pricestr
    elif  len(pricestr) == 2:
        return '$0.' + pricestr
    else:
        return '$' + pricestr[:len(pricestr)-2] + '.' + pricestr[-2:]


def format_date_str_to_datetime(datestr=None):
    ''' convert date from string in format m/d/yyyy to datetime
        default if no parameter passed current date/time '''
    if datestr:
        return datetime.strptime(datestr, '%m/%d/%Y')
    else:
        return datetime.now()


def format_date_datetime_to_str(dt=datetime.now()):
    ''' convert date from datetime to string in format m/d/yyyy
        default if no parameter passed current date/time '''
    return datetime.strftime(dt, '%m/%d/%Y')


def add_record():
    ''' Add a new product to the database '''
    record = get_product_details_from_user()
    add_record_to_db(record)


def add_record_to_db(record):
    ''' function that actually adds the product record to database. If ID already exists, update '''
    try:
        Product.create(product_name=record['product_name'],
                       product_quantity=record['product_quantity'],
                       product_price=record['product_price'],
                       date_updated=record['date_updated'])
    except IntegrityError:
        product_record = Product.get(product_name=record['product_name'])
        product_record.product_quantity = record['product_quantity'],
        product_record.product_price = record['product_price'],
        if record['date_updated'] > product_record.date_updated:
            product_record.date_updated = record['date_updated']
        product_record.save()


def view_product_by_id():
    ''' View a single product's inventory '''
    valid = False
    while not valid:
        try:
            id = int(input("Enter product id: "))
            valid = True
        except:
            print("Product id needs to be a number, please retry")
    try:
        product = Product.get(Product.product_id == id)
        display_product(product)
    except:
        print('Sorry, product with this ID not found')


def get_product_details_from_user():
    ''' Get product details from user for a new product being added to db '''
    record = {}
    record['product_name'] = input("Please enter product name: ")
    record['product_quantity'] = get_quantity_from_user()
    record['product_price'] = get_price_from_user()
    record['date_updated'] = datetime.now()
    return record


def get_quantity_from_user():
    ''' Get quantity from user input and validate numeric data entered  '''
    valid = False
    while not valid:
        try:
            qty = int(input("Please enter quantity of product in stock: "))
            valid = True
        except:
            print("Quantity needs to be a number, please retry")
    return qty


def get_price_from_user():
    ''' Get price from user input and validate (numeric maybe with $ and/or .)  '''
    valid = False
    while not valid:
        pricestr = input("Please enter product price: ")
        if re.search('\$?\.?\d+', pricestr):
            price = format_price_str_to_int(pricestr)
            valid = True
        else:
            print("Invalid price, please retry")
    return price


def display_product(product):
    ''' Display details for one product on terminal '''
    print(f'Product {product.product_id}:  {product.product_name}')
    print(f'Price: {format_price_int_to_str(product.product_price)}')
    print(f'Quantity in stock: {product.product_quantity}')
    print(f'Date Last Updated: {format_date_datetime_to_str(product.date_updated)}')
    input('Press any key to continue ')


def backup_db_to_csv():
    ''' Make a backup of the entire inventory  '''
    products = Product.select()
    f = open('backup.csv', 'w')
    for product in products:
        product_row = f'{product.product_id},{product.product_name},{format_price_int_to_str(product.product_price)},'
        product_row = product_row + f'{product.product_quantity},{format_date_datetime_to_str(product.date_updated)}\n'
        f.write(product_row)
    f.close()


menu = OrderedDict([
        ('a', add_record),
        ('v', view_product_by_id),
        ('b', backup_db_to_csv),
       ])


if __name__ == '__main__':
    initialize()
    #menu loop
    choice = None
    while choice != 'q':
        # clear()
        print("Enter q to quit.")
        for key, value in menu.items():
            print(f'{key}) {value.__doc__}')
        choice = input('Action: ').lower().strip()
        if choice in menu:
            # clear()
            menu[choice]()

