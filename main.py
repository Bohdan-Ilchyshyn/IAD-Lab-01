import time
import json
import pandas as pd
import requests
from datetime import date, timedelta, datetime
from dateutil.rrule import rrule, MONTHLY
from colorama import Fore
import plotter

API_KEY = '6532d6454b8aa370768e63d6ba5a832e'


# F -> C
def temperature_converter(temperature: str) -> float:
    return fahrenheit_to_celsius(float(temperature))


# mph -> mph
def speed_converter(speed: str) -> float:
    return mph_to_mps(float(speed.split(' ')[0]))


# 23.01 -> 23-01-2019
def date_converter(date_: str) -> date:
    return datetime.strptime(date_ + '.2019', '%d.%b.%Y')


# 10% -> 0.1
def humidity_converter(h: str) -> float:
    return round(float(h.strip('%')) / 100.0, 2)


def time_converter(time_: str) -> time:
    return datetime.strptime(time_, "%I:%M %p").time()


def pressure_converter(pressure: str) -> float:
    return round(float(pressure.replace(',', '.')) / 0.0040146, 2)


def mph_to_mps(speed: float) -> float:
    return round((speed * 1.609344) / 3.6, 2)


def fahrenheit_to_celsius(temperature: float) -> float:
    return round((temperature - 32) / 1.8, 2)


def parse_data_from_file() -> pd.DataFrame:
    data = pd.read_csv(filepath_or_buffer='../DATABASE.csv',
                       # index_col='day/month',
                       usecols=['day/month', 'Time', 'Temperature', 'Dew Point', 'Humidity', 'Wind',
                                'Wind Speed', 'Wind Gust', 'Pressure', 'Condition'
                                ],
                       converters={
                           'day/month': date_converter,
                           'Time': time_converter,
                           'Temperature': temperature_converter,
                           'Dew Point': temperature_converter,
                           'Humidity': humidity_converter,
                           'Wind Speed': speed_converter,
                           'Wind Gust': speed_converter,
                           'Pressure': pressure_converter
                       },
                       encoding='utf8',
                       sep=';')
    data.rename(columns={'day/month': 'Date', 'Wind': 'Wind Direction'}, inplace=True)
    data.set_index('Date')

    return data


def get_data(station: str, f: date, t: date):
    url = f'https://api.weather.com/v1/location/{station}/observations/historical.json' \
          f'?apiKey={API_KEY}' \
          f'&units=e' \
          f'&startDate={f.strftime("%Y%m%d")}' \
          f'&endDate={t.strftime("%Y%m%d")}'

    response = requests.get(url)
    data = json.loads(response.text)['observations']

    return data


def parse_data_from_site(station: str, from_date: date, to_date: date):
    data = []
    prev = from_date
    # Сайт позволяє запросити максимум 31 день за 1 запрос
    for single_date in rrule(MONTHLY, dtstart=from_date, until=to_date):
        if prev == single_date.date():
            continue

        data.extend(get_data(station, prev, single_date.date() - timedelta(1)))
        time.sleep(1)
        prev = single_date.date()

    if prev <= to_date:
        data.extend(get_data(station, prev, to_date))

    return data


def json_to_dataframe(data) -> pd.DataFrame:
    return pd.DataFrame.from_records(data)


def process_data(data: pd.DataFrame) -> pd.DataFrame:
    dataframe = pd.DataFrame()

    dataframe['Date'] = pd.to_datetime(data['valid_time_gmt'], unit='s').dt.date
    dataframe['Time'] = pd.to_datetime(data['valid_time_gmt'], unit='s').dt.time
    dataframe['Temperature'] = data['temp'].apply(fahrenheit_to_celsius)
    dataframe['Dew Point'] = data['dewPt'].apply(lambda z: fahrenheit_to_celsius(z))
    dataframe['Humidity'] = data['rh'].apply(lambda z: z / 100.0)
    dataframe['Wind Direction'] = data['wdir']
    dataframe['Wind Direction Cardinal'] = data['wdir_cardinal']
    dataframe['Wind Speed'] = data['wspd'].apply(lambda z: mph_to_mps(z))
    # dataframe['Wind Gust']
    dataframe['Pressure'] = data['pressure']
    dataframe['Condition'] = data['wx_phrase']
    dataframe['UV Index'] = data['uv_index']

    return dataframe


def main():
    data = None

    print(Fore.BLUE + 'Read data from\n1 - from site\n2 - from file')
    choice = int(input(Fore.YELLOW + 'Make a choice: '))
    if choice == 1:
        print(Fore.BLUE + 'input date in format: Year-Month-Day')
        from_date = input(Fore.YELLOW + 'from: ')
        to_date = input(Fore.YELLOW + 'to: ')
        data = process_data(json_to_dataframe(parse_data_from_site(
            'UKKK:9:UA',
            datetime.strptime(from_date, '%Y-%m-%d').date(),
            datetime.strptime(to_date, '%Y-%m-%d').date()
        )))
    elif choice == 2:
        data = parse_data_from_file()

    diag = plotter.Diagram(data)

    for col in data.columns.values:
        print(Fore.BLUE + col)

    column1 = input(Fore.YELLOW + 'Column 1: ')
    column2 = input(Fore.YELLOW + 'Column 2: ')

    if column2 == '':
        diag.plot_diagrams(column1)
    else:
        diag.plot_diagrams(column1, column2)


if __name__ == '__main__':
    main()
