import sys
sys.path.append('C:\\Users\\Lennon\\Projects\\xp\\zendesk\\zdautomation')
import uuid
from pathlib import Path
import logging
from dotenv import dotenv_values
from api.zendesk import Client as ZenClient
from tickets_service import TicketQueryService, TicketService
from datetime import datetime
from utils import download_file_from_url


env = 'PRD'
config = dotenv_values(f'{env}.env')

logging.basicConfig(
    filename=datetime.now().strftime(f'logs/tickets_update_{env}_%Y%m%d.log'),
    encoding='utf-8', level=logging.DEBUG, format='%(asctime)s %(levelname)s:%(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p')


client = ZenClient(config['ZD_INSTANCE'], config['ZD_EMAIL'], config['ZD_TOKEN'])
ticket_service = TicketService(client)

cf_motivo = '1900010001244'
cf_cpf = 1900007415204


def extract():
    query_service = TicketQueryService()
    query_service.add_date_init('2022-04-15T00:00:00Z')
    query_service.add_date_end('2022-04-15T00:00:00Z')
    query_service.add_custom_field(cf_motivo, 'sub_transferencia_custodia_envio_stvm')
    query = query_service.build()
    tickets = ticket_service.list_by_query(query)
    logging.info(f'Found {len(tickets)} tickets')
    for ticket in tickets:
        field = next((field for field in ticket['custom_fields'] if field["id"] == cf_cpf), None)
        cpf = field['value']
        ticket_id = ticket['id']
        attachments = ticket_service.GetTicketAttachments(ticket)
        Path(f'assets/{cpf}/{ticket_id}').mkdir(parents=True, exist_ok=True)
        for attachment in attachments:
            myuuid = uuid.uuid4()
            ext = attachment['file_name'].split('.')[-1]
            download_file_from_url(attachment['content_url'], f"assets/{cpf}/{ticket_id}/{str(myuuid)}.{ext}")


def main():
    try:
        extract()
    except Exception as err:
        logging.error(err)


if __name__ == "__main__":
    main()
