import sys
sys.path.append('C:\\Users\\Lennon\\Projects\\xp\\zendesk\\zdautomation')

import logging
from dotenv import dotenv_values
from macros_service import MacroService
from api.zendesk import Client as ZenClient
from datetime import datetime

env = 'HML'
config = dotenv_values(f'.env')

logging.basicConfig(
    filename=datetime.now().strftime(f'logs/macros_clear-%Y%m%d.log'),
    encoding='utf-8', level=logging.DEBUG, format='%(asctime)s %(levelname)s:%(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p')


client = ZenClient(config['ZD_INSTANCE'], config['ZD_EMAIL'], config['ZD_TOKEN'])
macro_service = MacroService(client)


def clear():
    macros = client.MacroPaginate({})
    logging.info(f'Found {len(macros)} macros')
    macro_service.delete_many(macros)


def main():
    try:
        clear()
    except Exception as err:
        logging.error(err)


if __name__ == "__main__":
    main()
