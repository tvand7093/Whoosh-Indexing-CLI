
import os

class Config(dict):
    """ Provides a dictionary style object for environment variables. """

    def __readEnv(self):
        if not os.path.isfile('.env'):
            print """Environment file missing. Please copy .env.template as .env and populate the values then try again."""
            return False

        lines = []
        with open('.env') as f:
            lines = f.readlines()

        # Convert lines to a dictionary using key=value from the file.
        split = [line.split('=') for line in lines]

        for line in split: 
            self[line[0]] = line[1].strip()

        return True

    def __getattr__(self, name):
        if name in self:
            return self[name]
        else:
            raise AttributeError("No such attribute: " + name)

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        if name in self:
            del self[name]
        else:
            raise AttributeError("No such attribute: " + name)
    
    def __init__(self):

        """ Denotes if the config values were loaded correctly or not."""
        self.wasLoaded = self.__readEnv()