import re


def check_message_for_tracking_number(message):

    #TODO Get an accurate list of regexes to use
    _REGEX = {
        re.compile(r"(1Z?[0-9A-Z]{3}?[0-9A-Z]{3}?[0-9A-Z]{2}?[0-9A-Z]{4}?[0-9A-Z]{3}?[0-9A-Z]|[\dT]\d\d\d?\d\d\d\d?\d\d\d)"): 'ups',
        re.compile(r'(E\D{1}\d{9}\D{2}$|9\d{15,21})'): 'usps'
    }

    for regex, type in _REGEX.items():
        m = re.search(regex, message)
        if m:
            #TODO This only gets the first tracking number found.  We should look into possibly
            #TODO checking for multiple numbers.
            return m.group(0)

    return None