import unittest
import re
import uuid
from urllib.parse import urlparse

REGEX_TYPES = {
    'string': (str, r'[^/]+'),
    'int': (int, r'\d+'),
    'number': (float, r'[0-9\\.]+'),
    'alpha': (str, r'[A-Za-z]+'),
    'path': (str, r'[^/].*?'),
    'uuid': (uuid.UUID, r'[A-Fa-f0-9]{8}-[A-Fa-f0-9]{4}-[A-Fa-f0-9]{4}-[A-Fa-f0-9]{4}-[A-Fa-f0-9]{12}')
}


# pattern = r'<.*?>' #'/event/<name:[A-Za-z]>'

class ArgsParse(object):

    properties = {"unhashable": None}

    def __init__(self, url_pattern):
        self.url_pattern = url_pattern
        self.parameter_pattern = re.compile(r'<(.+?)>')
        pattern_string = re.sub(self.parameter_pattern,
                                self.add_parameter, self.url_pattern)
        self.pattern = re.compile(r'^{}$'.format(pattern_string))
    
    def parse_parameter_string(self, parameter_string):
        """Parse a parameter string into its constituent name, type, and
        pattern
        For example::
            parse_parameter_string('<param_one:[A-z]>')` ->
                ('param_one', str, '[A-z]')
        :param parameter_string: String to parse
        :return: tuple containing
            (parameter_name, parameter_type, parameter_pattern)
        """
        # We could receive NAME or NAME:PATTERN
        name = parameter_string
        pattern = 'string'
        if ':' in parameter_string:
            name, pattern = parameter_string.split(':', 1)
            if not name:
                raise ValueError(
                    "Invalid parameter syntax: {}".format(parameter_string)
                )

        default = (str, pattern)
        # Pull from pre-configured types
        _type, pattern = REGEX_TYPES.get(pattern, default)

        return name, _type, pattern

    def add_parameter(self, match):
        name = match.group(1)
        name, _type, pattern = self.parse_parameter_string(name)

        # parameter = Parameter(
        #     name=name, cast=_type)
        # parameters.append(parameter)

        # Mark the whole route as unhashable if it has the hash key in it
        if re.search(r'(^|[^^]){1}/', pattern):
            self.properties['unhashable'] = True
        # Mark the route as unhashable if it matches the hash key
        elif re.search(r'/', pattern):
            self.properties['unhashable'] = True

        return '({})'.format(pattern) # return '(?P<name>{})'.format(pattern)
    
    def parse(self, url):
        res = self.pattern.search(url)
        if res is None:
            return None
        else:
            return self.pattern.search(url).groups()

    def is_hashable(self):
        if self.properties["unhashable"] is True:
            return False
        else:
            return True

def main2():

    #======================<Normal Url test>=================
    # Test parse 2 args
    url_pattern = '/event'
    a = ArgsParse(url_pattern)

    # check propertise
    print(a.is_hashable())


    #======================<One args test>=================
    # Test parse 1 arg
    url_pattern = '/event/<name>'
    a = ArgsParse(url_pattern)

    # basic test
    url_request = '/event/tuan'
    print(a.parse(url_request))
    # test a normal simillar url
    url_request = '/event'
    print(a.parse(url_request))
    # test a missing parse
    url_request = '/event/'
    print(a.parse(url_request))

    # check propertise
    print(a.is_hashable())

    #======================<More than one args test>=================
    # Test parse 2 args
    url_pattern = '/event/<name>/<subname>'
    a = ArgsParse(url_pattern)

    # basic test
    url_request = '/event/tuan/minh'
    print(a.parse(url_request))

    url_request = '/event'
    print(a.parse(url_request))
    # test a missing arg
    url_request = '/event/'
    print(a.parse(url_request))

    # test a missing 1 arg
    url_request = '/event/tuan'
    print(a.parse(url_request))
    # test a missing 1 arg
    url_request = '/event//minh'
    print(a.parse(url_request))

    # test a missing 1 arg
    url_request = '/eventFalse/tuan/minh'
    print(a.parse(url_request))
    # test a missing 1 arg
    url_request = '/something/tuan/minh'
    print(a.parse(url_request))

    # check propertise
    print(a.properties)
    print(a.pattern)


if __name__ == '__main__':
    main2()
