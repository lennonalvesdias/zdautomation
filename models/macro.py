import json


def clean_dict(mydict):
    for key, value in list(mydict.items()):
        if value is None:
            del mydict[key]
        elif isinstance(value, dict):
            clean_dict(value)
    return mydict


class Macro(object):
    def __init__(
            self, id=None, title=None, description=None, active=False, actions=[],
            restriction={},
            created_at=None, updated_at=None, position=None, url=None):
        self.id = id
        self.title = title
        self.description = description if description else title
        self.active = active
        self.actions = actions
        self.restriction = restriction
        self.url = url
        self.created_at = created_at
        self.updated_at = updated_at
        self.position = position

    def SetTitle(self, title):
        self.title = title

    def SetDescription(self, description):
        self.description = description

    def SetActive(self, active):
        self.active = active

    def CleanActions(self):
        self.actions = []

    def AppendAction(self, action):
        self.actions.append(action)

    def AddAction(self, field, value):
        action = {'field': field, 'value': value}
        self.AppendAction(action)

    def SetRestriction(self, value):
        self.restriction = value

    def ToJson(self):
        mydict = {'macro': clean_dict(self.__dict__)}
        return json.dumps(mydict, ensure_ascii=False, allow_nan=False)
