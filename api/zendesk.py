from urllib.parse import parse_qs
from urllib.parse import urlparse
import requests_cache
from requests.auth import HTTPBasicAuth
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import requests.packages.urllib3
from urllib.parse import urlencode
requests.packages.urllib3.disable_warnings()


class Client(object):
    def __init__(self, subdomain=None, user=None, password=None, proxy={}):
        self.session = requests_cache.CachedSession(f'cache/{subdomain}')
        self.session.auth = HTTPBasicAuth(user, password)
        self.session.headers = {}
        retries = Retry(total=3, backoff_factor=1, status_forcelist=[401])
        self.session.mount('https://', HTTPAdapter(max_retries=retries))
        self.session.proxies = proxy
        self.subdomain = subdomain

    def TranslateStatus(self, status):
        if status == 'Novo':
            return 'new'
        if status == 'Aberto':
            return 'open'
        if status == 'Pendente':
            return 'pending'
        if status == 'Em espera':
            return 'hold'
        if status == 'Resolvido':
            return 'solved'
        if status == 'Fechado':
            return 'closed'

    def TicketShow(self, id):
        url = f'https://{self.subdomain}.zendesk.com/api/v2/tickets/{id}.json'
        response = self.session.get(url, verify=False)
        # response = requests.get(url, headers=headers, proxies=proxyDict, verify=False)
        return response.json()

    def TicketPaginate(self, params):
        tickets = []
        response = self.SearchExport(params)
        while len(response['results']) > 0:
            tickets += response['results']
            params['page[after]'] = response['meta']['after_cursor']
            response = self.SearchExport(params)
        return tickets

    def TicketListComment(self, id):
        url = f'https://{self.subdomain}.zendesk.com/api/v2/tickets/{id}/comments.json'
        response = self.session.get(url, verify=False)
        return response.json()

    def TicketUpdate(self, id, data):
        url = f'https://{self.subdomain}.zendesk.com/api/v2/tickets/{id}.json'
        response = self.session.put(url, json=data, verify=False)
        return response.json()

    def TicketUpdateStatus(self, id, status):
        data = {'ticket': {'status': status}}
        self.TicketUpdate(id, data)

    def TicketUpdateMany(self, ids, data):
        url = f'https://{self.subdomain}.zendesk.com/api/v2/tickets/update_many.json?ids={ids}'
        response = self.session.put(url, json=data, verify=False)
        return response.json()

    def TicketUpdateManyStatus(self, ids, status):
        data = {'ticket': {'status': status}}
        return self.TicketUpdateMany(ids, data)

    def Search(self, params={}):
        url = f'https://{self.subdomain}.zendesk.com/api/v2/search.json?{urlencode(params)}'
        response = self.session.get(url, verify=False)
        return response.json()

    def SearchExport(self, params={}):
        url = f'https://{self.subdomain}.zendesk.com/api/v2/search/export.json?{urlencode(params)}'
        response = self.session.get(url, verify=False)
        return response.json()

    def MacroList(self, params={}):
        url = f'https://{self.subdomain}.zendesk.com/api/v2/macros.json?{urlencode(params)}'
        response = self.session.get(url, verify=False)
        return response.json()

    def MacroPaginate(self, params={}):
        response = self.MacroList(params)
        macros = response['macros']
        while response['next_page']:
            parsed_url = urlparse(response['next_page'])
            next_page = parse_qs(parsed_url.query)['page'][0]
            params['page'] = next_page
            response = self.MacroList(params)
            macros += response['macros']
        return macros

    def MacroShow(self, id):
        url = f'https://{self.subdomain}.zendesk.com/api/v2/macros/{id}.json'
        response = self.session.get(url, verify=False)
        return response.json()

    def MacroCreate(self, data):
        url = f'https://{self.subdomain}.zendesk.com/api/v2/macros.json'
        response = self.session.post(url, json=data, verify=False)
        return response.json()

    def MacroUpdate(self, id, data):
        url = f'https://{self.subdomain}.zendesk.com/api/v2/macros/{id}.json'
        response = self.session.put(url, json=data, verify=False)
        return response.json()

    def MacroDeleteMany(self, ids):
        url = f'https://{self.subdomain}.zendesk.com/api/v2/macros/destroy_many.json?ids={ids}'
        self.session.delete(url, verify=False)

    def TicketFormsList(self, params={'active': True}):
        url = f'https://{self.subdomain}.zendesk.com/api/v2/ticket_forms.json?{urlencode(params)}'
        response = self.session.get(url, verify=False)
        return response.json()

    def TicketFieldsList(self, params={}):
        url = f'https://{self.subdomain}.zendesk.com/api/v2/ticket_fields.json?{urlencode(params)}'
        response = self.session.get(url, verify=False)
        return response.json()

    def TicketFieldsOptionsList(self, id, params={}):
        url = f'https://{self.subdomain}.zendesk.com/api/v2/ticket_fields/{id}/options.json?{urlencode(params)}'
        response = self.session.get(url, verify=False)
        return response.json()

    def GroupsList(self, params={}):
        url = f'https://{self.subdomain}.zendesk.com/api/v2/groups.json?{urlencode(params)}'
        response = self.session.get(url, verify=False)
        return response.json()

    def GetFormId(self, name):
        response = self.TicketFormsList()
        form = [item for item in response['ticket_forms'] if item.get('name').lower() == name.lower()]
        return form[0]['id']

    def GetFieldId(self, title):
        response = self.TicketFieldsList()
        field = [item for item in response['ticket_fields'] if item.get('title').lower() == title.lower()]
        return field[0]['id']

    def GetFieldOptionValue(self, field_id, option_name):
        response = self.TicketFieldsOptionsList(field_id)
        field = [item for item in response['custom_field_options'] if item.get('name').lower() == option_name.lower()]
        return field[0]['value']

    def GetGroupIds(self, group_names):
        ids = []
        for group_name in group_names.split(','):
            id = self.GetGroupId(group_name)
            ids.append(id)
        return ids

    def GetGroupId(self, group_name):
        response = self.GroupsList()
        group = [item for item in response['groups'] if item.get('name').lower() == group_name.strip().lower()]
        return group[0]['id']
