import json


class Config:

    __json = None

    def __init__(self):
        with open('config.json') as f:
            self.__json = json.load(f)
            self.__verify_contents()

    def __getitem__(self, arg):
        return self.__json[arg]

    def __verify_contents(self):
        return
