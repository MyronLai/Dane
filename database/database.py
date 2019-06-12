import mysql.connector
import re
import json
import os


def load_db(file):
    jsonFile = open(file, 'r')
    config = json.load(jsonFile)
    jsonFile.close()
    database = mysql.connector.connect(
        host=config['database']['host'],
        user=config['database']['user'],
        passwd=config['database']['passwd'],
        database=config['database']['database']
    )
    return database

