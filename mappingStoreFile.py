import sqlite3
from sqlite3 import Error
import logging
from mappingStoreInterface import MappingStoreInterface
import csv
import os

class MappingStoreFile(MappingStoreInterface):
    def __init__(self):
        self.store_path = None

    def init_or_open_store(self, store_path):
        self.store_path = store_path
        with open(store_path, mode='a+') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            if len(list(csv_reader)) == 0:
                # meaning it is not inited
                logging.debug("This is a brand new file")
            else:
                logging.debug("There exist some data")

    def insert_hashed_url(self, id, long_url, hash):
        with open(self.store_path, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            fieldnames = ['id', 'long_url', 'hash']
            row = {'id': id, 'long_url': long_url, 'hash': hash}
            if len(list(csv_reader)) == 0:
                csv_file.close()
                with open(self.store_path, mode='a+') as csv_file_write:
                    writer = csv.DictWriter(csv_file_write, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerow(row)
            else:
                csv_file.close()
                with open(self.store_path, mode='a+') as csv_file_write:
                    writer = csv.DictWriter(csv_file_write, fieldnames=fieldnames)

                    writer.writerow(row)

    def is_hashed_url_exist(self, hash_value):
        with open(self.store_path, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                if row['hash'] == hash_value:
                    return True
            return False

    def is_long_url_exist(self, longUrl):

        with open(self.store_path, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                if row['long_url'] == longUrl:
                    return True
            return False

    def get_long_url_from_hash(self, hash):

        with open(self.store_path, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                if row['hash'] == hash:
                    return row['long_url']
            return None

    def get_hash_from_long_url(self, longUrl):

        with open(self.store_path, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                if row['long_url'] == longUrl:
                    return row['hash']
            return None

    def clean_store(self):

        os.remove(self.store_path)
