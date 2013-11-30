# lzo1x_decoder

class _Input(object):
    """Input data stream wrapper"""
    def __init__(self, data): 
        self.data = iter(data)
        self.first = None
    def peek_byte(self):
        if self.first is None:
            self.first = ord(self.data.next())
        return self.first
    def get_byte(self):
        if self.first is not None:
            tmp, self.first = self.first, None
            return tmp
        return ord(self.data.next())
    def get_text(self, length):
        self.first = None
        return (self.data.next() for _ in xrange(length))
    def get_zero_encoded_length(self):
        self.first = None
        l = 0
        while True:
            c = self.data.next()
            if c != '\x00': break
            l += 255
        l += ord(c)
        return l

def lzo1x_decoder(input_data, log = lambda x: None):
    """lzo1x decoder"""

    def _start(data, result):
        v = data.peek_byte()
        if v <= 17: return _common_case
        log((0, 'SS', v-17))                                # Special Start
        result.extend(data.get_text(v - 17))
        return _matches if v <= 20 else  _after_plain_text  # pseudo-tail or plain-text logic

    def _common_case(data, result):
        v = data.peek_byte()
        if v >= 16: return _matches
        # plain text
        l = v if v > 0 else (data.get_zero_encoded_length() + 15)
        log((len(result), 'PT', l+3))
        result.extend(data.get_text(l + 3))
        return _after_plain_text

    def _after_plain_text(data, result): 
        if data.peek_byte() >= 16: return _matches
        # special after-plain match -- I can't find it in lzo output, so this code was not tested
        v = data.get_byte()
        offset = 0x0800 + 1 + (v >> 2) + (data.get_byte() << 2)
        log((len(result), 'APM', offset, 3, v & 3))
        return _copy_match_and_return(data, offset, 3, v & 3, result)

    def _matches(data, result):
        v = data.get_byte()

        if v >= 64:    # M2 match
            mt = 'M2'
            length = ((v >> 5) & 7) - 1
            tail = v & 3
            offset = 1 + ((v >> 2) & 7) + (data.get_byte() << 3)
        elif v >= 32:  # M3 match
            mt = 'M3'
            length = (v & 31) if (v & 31) > 0 else (data.get_zero_encoded_length() + 31)
            tail = data.peek_byte() & 3
            offset = 1 + (data.get_byte() >> 2) + (data.get_byte() << 6)
        elif v >= 16:  # M4 match
            mt = 'M4'
            length = (v & 7) if (v & 7) > 0 else (data.get_zero_encoded_length() + 7)
            tail = data.peek_byte() & 3
            offset = ((v & 8) << 11) + (data.get_byte() >> 2) + (data.get_byte() << 6)
            if offset == 0: return None # eof
            offset += 0x4000
        else:          # M1 match
            mt = 'M1'
            length = 0
            tail = v & 3
            offset = 1 + (v >> 2) + (data.get_byte() << 2)

        log((len(result), mt, offset, length+2, tail))
        return _copy_match_and_return(data, offset, length+2, tail, result)

    def _copy_match_and_return(data, offset, length, tail, result):
        if offset and length:
            for i in xrange(length):
                result.append(result[-offset])
        if tail: 
            result.extend(data.get_text(tail))
        return _matches if tail else _common_case

    state = _start
    data = _Input(input_data)
    result = []

    while state:
        state = state(data, result)

    return result

