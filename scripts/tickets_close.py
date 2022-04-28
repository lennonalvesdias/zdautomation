import sys
sys.path.append('C:\\Users\\Lennon\\Projects\\xp\\zendesk\\zdautomation')
from datetime import datetime
from tickets_service import TicketQueryService, TicketService
from api.zendesk import Client as ZenClient
from dotenv import dotenv_values
import logging


env = 'PRD'
config = dotenv_values(f'{env}.env')

logging.basicConfig(
    filename=datetime.now().strftime(f'logs/tickets_update_{env}_%Y%m%d.log'),
    encoding='utf-8', level=logging.DEBUG, format='%(asctime)s %(levelname)s:%(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p')


client = ZenClient(config['ZD_INSTANCE'], config['ZD_EMAIL'], config['ZD_TOKEN'])
ticket_service = TicketService(client, logging)
cf_canal_de_entrada = '1900005027384'


def close_ura_tickets():
    query_service = TicketQueryService()
    query_service.add_date_init('2022-04-27T00:00:00Z')
    query_service.add_custom_field(cf_canal_de_entrada, 'canal_de_entrada_ura')
    query_service.add_status('solved')
    query = query_service.build()
    tickets = ticket_service.list_by_query(query)
    logging.info(f'Found {len(tickets)} tickets')
    ticket_service.updateTicketsStatus(tickets, 'closed')


def close_old_tickets():
    query_service = TicketQueryService()
    query_service.add_date_init('2022-04-15T00:00:00Z')
    query_service.add_status('solved')
    query = query_service.build()
    tickets = ticket_service.list_by_query(query)
    logging.info(f'Found {len(tickets)} tickets')
    ticket_service.updateTicketsStatus(tickets, 'closed')


def main():
    try:
        close_ura_tickets()
        # close_old_tickets()
    except Exception as err:
        logging.error(err)


if __name__ == "__main__":
    main()
