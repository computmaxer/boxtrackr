import re


def check_message_for_tracking_number(message):

    #TODO Get an accurate list of regexes to use
    _REGEX = {
        re.compile(r"(1Z?[0-9A-Z]{3}?[0-9A-Z]{3}?[0-9A-Z]{2}?[0-9A-Z]{4}?[0-9A-Z]{3}?[0-9A-Z]|[\dT]\d\d\d?\d\d\d\d?\d\d\d)"): 'ups',
        re.compile(r'(E\D{1}\d{9}\D{2}$|9\d{15,21})'): 'usps',
        re.compile(r'(/\b(1Z ?[0-9A-Z]{3} ?[0-9A-Z]{3} ?[0-9A-Z]{2} ?[0-9A-Z]{4} ?[0-9A-Z]{3} ?[0-9A-Z]|[\dT]\d\d\d ?\d\d\d\d ?\d\d\d)\b/i)'): 'ups',
        re.compile(r'(/\b((96\d\d\d\d\d ?\d\d\d\d|96\d\d) ?\d\d\d\d ?d\d\d\d( ?\d\d\d)?)\b/i)'): 'fedex',
        re.compile(r'(/\b(91\d\d ?\d\d\d\d ?\d\d\d\d ?\d\d\d\d ?\d\d\d\d ?\d\d|91\d\d ?\d\d\d\d ?\d\d\d\d ?\d\d\d\d ?\d\d\d\d)\b/i)'): 'usps'
    }

    for regex, type in _REGEX.items():
        matches = re.findall(regex, message)
        if matches:
            return matches

    return None