import schedule
from data_downloader import download_data
import time

schedule.every().day.at('03:00').do(download_data)
schedule.every().day.at('07:00').do(download_data)
schedule.every().day.at('11:00').do(download_data)
schedule.every().day.at('15:00').do(download_data)
schedule.every().day.at('19:00').do(download_data)
schedule.every().day.at('23:00').do(download_data)

while True:
    schedule.run_pending()
    time.sleep(1)