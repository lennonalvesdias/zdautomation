import sys
import logging
from api.zendesk import Client
from models.macro import Macro
from utils import has_value
import json


class MacroService(object):
    def __init__(self, client: Client):
        self.client = client
        self.titles = []
        self.creates = 0
        self.updates = 0

    def filter_macro_by_title(self, macros, title):
        macro = [item for item in macros if item.get('title').lower() == title.strip().lower()]
        return macro[0] if len(macro) > 0 else None

    def macro_exist(self, macros, macro):
        filter = self.filter_macro_by_title(macros, macro.title)
        if filter:
            f_macro = Macro(**filter)
            return f_macro
        else:
            return macro

    def get_customfield_action(self, field_title, field_value, option_name):
        field_id = self.client.GetFieldId(field_title.strip())
        value = field_value if field_value else self.client.GetFieldOptionValue(field_id, option_name.strip())
        return f'custom_fields_{field_id}', value

    def get_comment(self, row):
        if has_value(row, 'comment_html'):
            return row.comment_html
        elif has_value(row, 'comment'):
            comment_html = "<p>" + row.comment.replace("\n", "<br>") + "</p>"
            return comment_html
        else:
            return None

    def add_comment(self, macro, row):
        try:
            comment = self.get_comment(row)
            if comment:
                macro.AddAction('comment_value_html', comment)
                macro.AddAction('comment_mode_is_public', 'true' if row.comment_public else 'false')
        except Exception as err:
            raise Exception(f'Error in add_comment: {err}')

    def add_status(self, macro, row):
        try:
            if has_value(row, 'status'):
                macro.AddAction('status', self.client.TranslateStatus(row.status))
        except Exception as err:
            raise Exception(f'Error in add_status: {err}')

    def add_forms(self, macro, row):
        try:
            if has_value(row, 'forms'):
                macro.AddAction('ticket_form_id', self.client.GetFormId(row.forms))
        except Exception as err:
            raise Exception(f'Error in add_forms: {err}')

    def add_subject(self, macro, row):
        try:
            if has_value(row, 'subject'):
                macro.AddAction('subject', row.subject)
        except Exception as err:
            raise Exception(f'Error in add_subject: {err}')

    def add_tags(self, macro, row):
        try:
            if has_value(row, 'tags'):
                macro.AddAction('current_tags', row.tags)
        except Exception as err:
            raise Exception(f'Error in add_tags: {err}')

    def add_classification_tree(self, macro, row):
        try:
            if has_value(row, 'arvore_classificacao'):
                field, value = self.get_customfield_action('Árvore de Classificação', None, row.arvore_classificacao)
                macro.AddAction(field, value)
            if has_value(row, 'arvore_classificacao_n2'):
                field, value = self.get_customfield_action('Árvore de Classificação - N2', None, row.arvore_classificacao_n2)
                macro.AddAction(field, value)
            if has_value(row, 'arvore_classificacao_sac'):
                field, value = self.get_customfield_action('Árvore de Classificação - SAC', None, row.arvore_classificacao_sac)
                macro.AddAction(field, value)
        except Exception as err:
            raise Exception(f'Error in classification_tree: {err}')

    def add_product(self, macro, row):
        try:
            if has_value(row, 'product_name') and has_value(row, 'product_value'):
                field, value = self.get_customfield_action(f'Produto: {row.product_name}', None, row.product_value)
                macro.AddAction(field, value)
        except Exception as err:
            raise Exception(f'Error in add_product: {err}')

    def add_reason(self, macro, row):
        try:
            if has_value(row, 'product_value') and has_value(row, 'reason'):
                field, value = self.get_customfield_action(f'Motivo: {row.product_value}', None, row.reason)
                macro.AddAction(field, value)
        except Exception as err:
            raise Exception(f'Error in add_reason: {err}')

    def add_secondary_reason(self, macro, row):
        try:
            if has_value(row, 'reason') and has_value(row, 'secondary_reason'):
                field, value = self.get_customfield_action(f'Submotivo: {row.reason}', None, row.secondary_reason)
                macro.AddAction(field, value)
        except Exception as err:
            raise Exception(f'Error in add_secondary_reason: {err}')

    def add_n2_area(self, macro, row):
        try:
            if has_value(row, 'n2_area'):
                field, value = self.get_customfield_action(f'Áreas N2', None, row.n2_area)
                macro.AddAction(field, value)
            if has_value(row, 'n2_area_sac'):
                field, value = self.get_customfield_action(f'Áreas N2 SAC', None, row.n2_area_sac)
                macro.AddAction(field, value)
        except Exception as err:
            raise Exception(f'Error in add_n2_area: {err}')

    def add_n2_classification(self, macro, row):
        try:
            if has_value(row, 'n2_classification'):
                field, value = self.get_customfield_action(f'Classificação N2', None, row.n2_classification)
                macro.AddAction(field, value)
            if has_value(row, 'n2_classification_sac'):
                field, value = self.get_customfield_action(f'Classificação N2 SAC', None, row.n2_classification_sac)
                macro.AddAction(field, value)
        except Exception as err:
            raise Exception(f'Error in add_n2_classification: {err}')

    def add_n2_detail(self, macro, row):
        try:
            if has_value(row, 'n2_detail'):
                field, value = self.get_customfield_action(f'Detalhe da Classificação N2', None, row.n2_detail)
                macro.AddAction(field, value)
            if has_value(row, 'n2_detail_sac'):
                field, value = self.get_customfield_action(f'Detalhe da Classificação N2 SAC', None, row.n2_detail_sac)
                macro.AddAction(field, value)
        except Exception as err:
            raise Exception(f'Error in add_n2_detail: {err}')

    def add_topic(self, macro, row):
        try:
            if has_value(row, 'topic'):
                field, value = self.get_customfield_action(f'Tema', None, row.topic)
                macro.AddAction(field, value)
        except Exception as err:
            raise Exception(f'Error in add_topic: {err}')

    def add_restriction(self, macro, row):
        try:
            if has_value(row, 'restriction'):
                ids = self.client.GetGroupIds(row.restriction)
                macro.SetRestriction({'type': 'Group', 'id': ids[0], 'ids': ids})
        except Exception as err:
            raise Exception(f'Error in add_restriction: {err}')

    def process_macro(self, macro, row):
        self.add_comment(macro, row)
        self.add_status(macro, row)
        self.add_forms(macro, row)
        self.add_subject(macro, row)
        self.add_tags(macro, row)
        self.add_classification_tree(macro, row)
        self.add_product(macro, row)
        self.add_reason(macro, row)
        self.add_secondary_reason(macro, row)
        self.add_n2_area(macro, row)
        self.add_n2_classification(macro, row)
        self.add_n2_detail(macro, row)
        self.add_topic(macro, row)
        self.add_restriction(macro, row)

    def proccess_row(self, row, update: bool):
        macros = self.client.MacroPaginate({})
        macro = Macro(None, row.title, row.description, row.active, [], {}, None, None, None, None)
        if macro.title in self.titles:
            logging.warning(f'Macro {macro.title} already exists on this worksheet.')
            raise Exception(f'Macro {macro.title} already exists on this worksheet.')
        self.titles.append(macro.title)
        macro = self.macro_exist(macros, macro)
        # print(json.loads(macro.ToJson()))
        if 'id' in macro.__dict__ and macro.id:
            macro.CleanActions()
            self.process_macro(macro, row)
            payload = json.loads(macro.ToJson())
            if update:
                self.updates += 1
                logging.info(f'Updating {macro.title} in zendesk.')
                self.client.MacroUpdate(macro.id, payload)
        else:
            self.process_macro(macro, row)
            payload = json.loads(macro.ToJson())
            if update:
                self.creates += 1
                logging.info(f'Creating {macro.title} in zendesk.')
                self.client.MacroCreate(payload)
        return payload

    def delete_many(self, macros):
        macros_range = 100
        macros_ids = [str(macro['id']) for macro in macros]
        ids_by_range = [macros_ids[i:i + macros_range] for i in range(0, len(macros_ids), macros_range)]
        for ids in ids_by_range:
            ids_join = ','.join(ids)
            logging.info(f'Delete macros {ids_join}')
            self.client.MacroDeleteMany(ids_join)

    def summary(self):
        return self.creates, self.updates
