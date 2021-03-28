# procon-webbot

Webbot for entering timesheets from CSV to ProCon using [Selenium](https://www.selenium.dev/) written in Python.

## Limitations

At the moment it is possible to enter a timesheet for the current month, only. Furthermore it is not possible to divide the hours into several units. The working time is copied to a fixed unit.

Only Firefox is supported.

## Prerequisites

### Webdriver for Selenium

Download [geckodriver](https://github.com/mozilla/geckodriver/releases) and install it for your operating system.

### Python packages

```bash
pip install -r requirements.txt
```

### Certificate database

If your company is unable to provide a complete certificate chain, you may need to provide intermediate certificates yourself. All certificates from the `certs` subdirectory are put into a nss database which is used by Firefox then:

```bash
./create_cert_db.sh
```

## Usage

Username and password have to be set via environment variables, e. g.

```bash
export PROCON_USERNAME=hartarbeiterhar
export PROCON_PASSWORD=ja3kqfJRd2gW
```

All other parameter can be set via environment variables or command line arguments:

| Environment variable       | Command line argument | Description                               | Default    |
| -------------------------- | --------------------- | ----------------------------------------- | ---------- |
| `PROCON_URL`               | `--url`               | Base URL of ProCon                        | &mdash;    |
| `PROCON_COST_CENTER`       | `--costcenter`        | Name of costcenter as displayed in ProCon | &mdash;    |
| `PROCON_COLUMN_NAME_DATE`  | `--column-name-date`  | Name of date column in CSV file           | &mdash;    |
| `PROCON_COLUMN_NAME_START` | `--column-name-start` | Name of start column in CSV file          | &mdash;    |
| `PROCON_COLUMN_NAME_END`   | `--column-name-end`   | Name of end column in CSV file            | &mdash;    |
| `PROCON_COLUMN_NAME_PAUSE` | `--column-name-pause` | Name of pause column in CSV file          | &mdash;    |
| `PROCON_CSV_FORMAT_DATE`   | `--csv-format-date`   | Name of pause column in CSV file          | `%d.%m.%Y` |
| `PROCON_CSV_FORMAT_TIME`   | `--csv-format-time`   | Name of pause column in CSV file          | `%H:%M`    |
| `PROCON_CSV_DELIMITER`     | `--csv-delimiter`     | Name of pause column in CSV file          | `;`        |
| `PROCON_CSV_QUOTE_CHAR`    | `--csv-quote-char`    | Name of pause column in CSV file          | `"`        |

For example:

```bash
export PROCON_URL=https://procon.goetterbote.de/
export PROCON_COST_CENTER="123 SK0815 Migration to Cloud"
```

Imagine you have a CSV file with the following content:

```
Datum;Tag;Ein;Aus;Pause;Total;Total (dezimal)
01.03.2021;Mo;08:00;17:00;01:00;08:00;08.00
```

Then you would set in addition:

```bash
export PROCON_COLUMN_NAME_DATE="Datum"
export PROCON_COLUMN_NAME_START="Ein"
export PROCON_COLUMN_NAME_END="Aus"
export PROCON_COLUMN_NAME_PAUSE="Pause"
```

Finally you can execute the webbot:

```bash
./procon-webbot.py timesheet.csv
```
