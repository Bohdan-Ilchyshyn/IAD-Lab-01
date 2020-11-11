import requests
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.image as mpimg

data_urls = {
        'covid19_by_area_type_hosp_dynamics': 'https://github.com/VasiaPiven/covid19_ua/raw/master/covid19_by_area_type_hosp_dynamics.csv',
        'covid19_by_settlement_actual': 'https://github.com/VasiaPiven/covid19_ua/raw/master/covid19_by_settlement_actual.csv',
        'covid19_by_settlement_dynamics': 'https://github.com/VasiaPiven/covid19_ua/raw/master/covid19_by_settlement_dynamics.csv'
}


def download_actual_data() -> None:
    for key, value in data_urls.items():
        with open('data/'+key+'.csv', 'wb') as file:
            file.write(requests.get(value).content)


def save_to_exel(df: pd.DataFrame) -> None:
    df.to_excel('res.xlsx')


def parse_data() -> [pd.DataFrame]:
    d = []
    for k, v in data_urls.items():
        d.append(pd.read_csv('data/'+k+'.csv'))
    return d


def plot_lines(*args: pd.DataFrame) -> None:
    legend_labels = []
    for i in args:
        plt.plot(i)
        legend_labels.append(i.name.replace('new', 'totaly'))
    plt.xticks(args[0].index.values[::10], rotation=75)
    plt.legend(legend_labels)
    plt.ylabel('кількість випадків')
    plt.xlabel('дата')
    plt.show()


def plot_on_map(x: pd.Series, y: pd.Series, s: pd.Series) -> None:

    cof = len(s.unique())//10

    ukr_img = mpimg.imread('ukr_outline.png')
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(ukr_img, extent=[22.083, 40.276, 44.256, 52.506], alpha=0.5)
    scatter = ax.scatter(x=x, y=y, s=s//cof)
    handles, labels = scatter.legend_elements(prop="sizes", alpha=0.5)
    ax.legend(handles, labels, loc="upper right", title=f"Count * {cof}")
    ax.title.set_text(s.name)
    plt.show()


def plot_bar(df):
    df = df.sort_values(ascending=True)
    plt.barh(df.index, df.values)
    plt.ylabel('Область')
    plt.xlabel('Кількість')
    plt.title(str(df.name).replace('new', 'totaly'))
    plt.show()


def main():
    df_1, df_2, df_3 = pd.DataFrame, pd.DataFrame, pd.DataFrame

    print('1 - download actual data and read')
    print('2 - read data')

    command = int(input())
    if command == 1:
        download_actual_data()
        print('[+] Downloaded and read')
    elif command == 2:
        df_1, df_2, df_3 = parse_data()
        print('[+] Parsed')

    while True:
        print('\n1 - plot data on map')
        print('2 - plot lines')
        print('3 - plot bar')
        print('0 - exit\n')
        command = int(input('Make a choice: '))
        if command == 1:
            columns = ['total_susp', 'total_confirm', 'total_death', 'total_recover']
            for i, v in enumerate(columns):
                print(f'{i} - {v}')
            num = int(input('input column: '))
            plot_on_map(df_2['registration_settlement_lng'],
                        df_2['registration_settlement_lat'],
                        df_2[columns[num]])
        elif command == 2:
            cities = df_3['registration_area'].unique()
            print(cities)
            city = input('Input a region (press enter to all region): ')
            if city == '':
                df = df_3.groupby('zvit_date').sum()
            else:
                df = df_3[df_3['registration_area'] == city].groupby('zvit_date').sum()
            plot_lines(df['new_death'].cumsum(), df['active_confirm'], df['new_recover'].cumsum(),
                       df['new_susp'].cumsum(), df['new_confirm'].cumsum())
        elif command == 3:
            df = df_3.groupby('registration_area').sum()
            plot_bar(df['new_confirm'])
        elif command == 4:
            df = df_3.groupby('registration_area').sum()
            t = int(input('save to excel? (1 - YES, 2 - NO) '))
            if t == 1:
                save_to_exel(df)
        if command == 0:
            break


if __name__ == '__main__':
    main()
