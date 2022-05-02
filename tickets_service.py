from api.zendesk import Client
import itertools
import time


class TicketQueryService(object):
    def __init__(self):
        self.query = ''

    def add_date_init(self, date):
        self.query += f'created<{date} '

    def add_date_end(self, date):
        self.query += f'created>{date} '

    def add_custom_field(self, field_id, value):
        self.query += f'custom_field_{field_id}:{value} '

    def add_status(self, status):
        self.query += f'status<{status} '

    def add_assignee(self, assignee):
        self.query += 'assignee:none'

    def build(self):
        return self.query


class TicketService(object):
    def __init__(self, client: Client, logging):
        self.client = client
        self.logging = logging

    def list_by_query(self, query):
        params = {
            'query': query,
            'filter[type]': 'ticket'
        }
        return self.client.TicketPaginate(params)

    def UpdateTicketsStatus(self, tickets, status_update, n=100):
        tickets_ids = [str(ticket['id']) for ticket in tickets]
        ids_by_range = [tickets_ids[i:i + n] for i in range(0, len(tickets_ids), n)]
        for ids in ids_by_range:
            ids_join = ','.join(ids)
            updated = self.client.TicketUpdateManyStatus(ids_join, status_update)
            self.logging.debug(updated)
            time.sleep(2)

    def GetTicketAttachments(self, ticket):
        ticket_id = ticket['id']
        comments = self.client.TicketListComment(ticket_id)
        attachments = [comment['attachments'] for comment in comments['comments']]
        attachments = list(itertools.chain.from_iterable(attachments))
        return attachments
