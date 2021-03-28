#!/usr/bin/env python

import argparse
import csv
import os
import re
import sys

from datetime import datetime
from shutil import copy2

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

DEFAULT_CSV_FORMAT_DATE = '%d.%m.%Y'
DEFAULT_CSV_FORMAT_TIME = '%H:%M'
DEFAULT_CSV_DELIMITER = ';'
DEFAULT_CSV_QUOTE_CHAR = '"'

PROCON_FORMAT_TIME = '%H:%M'

CERT_DB = 'nss/cert9.db'


def login(username, password):
    elem = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@placeholder="AD-Kennung"]')))
    elem.clear()
    elem.send_keys(username)

    elem = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@placeholder="Passwort"]')))
    elem.clear()
    elem.send_keys(password)

    select = Select(driver.find_element_by_id('company'))
    select.select_by_index(1)

    elem = wait.until(EC.presence_of_element_located((By.ID, 'btnLogin')))
    elem.click()


def generate_id(key, date):
    return f'{key}_{date.day - 1}'


def enter_value_in_cell(date, key, value):
    elem = wait.until(EC.presence_of_element_located((By.ID, generate_id(key, date))))
    if not elem.text:
        elem.click()
        elem = wait.until(EC.presence_of_element_located((By.ID, 'editCell')))
        if isinstance(value, str):
            elem.send_keys(value)
        else:
            elem.send_keys(value.strftime(PROCON_FORMAT_TIME))

        return elem
    else:
        return None


def enter_day(date, start, end, pause):
    if enter_value_in_cell(date, 'lnStart', start):
        enter_value_in_cell(date, 'lnEnde', end)
        enter_value_in_cell(date, 'lnPause', pause)

        elem = wait.until(EC.presence_of_element_located((By.ID, generate_id(costcenter_line, date))))
        elem.click()

        elem = wait.until(EC.presence_of_element_located((By.ID, generate_id('lnDiff', date))))
        diff_time = elem.text

        enter_value_in_cell(date, costcenter_line, diff_time)

        steal_focus()


def steal_focus():
    elem = wait.until(EC.presence_of_element_located((By.XPATH, '//td[@title="Beginn"]')))
    elem.click()


def argument_options(key, default=None):
    default_value = os.environ.get(key, default)

    map = {'default': default_value} if default_value else {'required': True}

    return map


parser = argparse.ArgumentParser(description='Import timesheet to procon')
parser.add_argument('filename', help='Filename of timesheet')
parser.add_argument('--url',               **argument_options('PROCON_URL'))
parser.add_argument('--costcenter',        **argument_options('PROCON_COST_CENTER'))
parser.add_argument('--column-name-date',  **argument_options('PROCON_COLUMN_NAME_DATE'))
parser.add_argument('--column-name-start', **argument_options('PROCON_COLUMN_NAME_START'))
parser.add_argument('--column-name-end',   **argument_options('PROCON_COLUMN_NAME_END'))
parser.add_argument('--column-name-pause', **argument_options('PROCON_COLUMN_NAME_PAUSE'))
parser.add_argument('--csv-format-date',   **argument_options('PROCON_CSV_FORMAT_DATE', DEFAULT_CSV_FORMAT_DATE))
parser.add_argument('--csv-format-time',   **argument_options('PROCON_CSV_FORMAT_TIME', DEFAULT_CSV_FORMAT_TIME))
parser.add_argument('--csv-delimiter',     **argument_options('PROCON_CSV_DELIMITER', DEFAULT_CSV_DELIMITER))
parser.add_argument('--csv-quote-char',    **argument_options('PROCON_CSV_QUOTE_CHAR', DEFAULT_CSV_QUOTE_CHAR))

args = parser.parse_args()

if not os.environ.get('PROCON_USERNAME') or not os.environ.get('PROCON_PASSWORD'):
    exit("Set environment variables PROCON_USERNAME and PROCON_PASSWORD.")

now = datetime.now()

profile = webdriver.FirefoxProfile()

if os.path.exists(CERT_DB):
    copy2(CERT_DB, profile.profile_dir)

driver = webdriver.Firefox(profile)
wait = WebDriverWait(driver, 10)
driver.get(args.url)

wait.until(EC.title_is('WebProCon'))

login(os.environ['PROCON_USERNAME'], os.environ['PROCON_PASSWORD'])

try:
    wait.until(EC.presence_of_element_located((By.ID, 'top')))
except TimeoutException:
    driver.close()
    exit("Login failed.")

try:
    xpath = f"//*[contains(text(), '{args.costcenter}')]"
    elem = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
    costcenter_line = elem.get_attribute('id').replace('row', 'PL_')
except TimeoutException:
    driver.close()
    exit(f"Costcenter {args.costcenter} not available. Exiting.")

steal_focus()

with open(args.filename, newline='') as csvfile:
    csvreader = csv.DictReader(csvfile, delimiter=args.csv_delimiter, quotechar=args.csv_quote_char)

    for row in csvreader:
        if not re.search(r'^\d+', row[args.column_name_date]):
            break

        date  = datetime.strptime(row[args.column_name_date],  args.csv_format_date)
        start = datetime.strptime(row[args.column_name_start], args.csv_format_time)
        end   = datetime.strptime(row[args.column_name_end],   args.csv_format_time)
        pause = datetime.strptime(row[args.column_name_pause], args.csv_format_time)

        if date.month != now.month or date.year != now.year:
            print(f"row {row} is not in current month. Ignoring.", file=sys.stderr)
            continue

        enter_day(date, start, end, pause)

driver.close()
