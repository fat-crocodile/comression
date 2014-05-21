"""Read and write bitsreams"""

class InputStream(object):
    """Get iterable of symbols, treat it as bit stream, from lower byte bits to higher"""

    def __init__(self, data):
        self.data = iter(data)
        self.bit_index = 0
        self.byte_index = 0
        self.byte = None

    def get_le(self, n):
        """return n-bit integer, that lay in stream from lower bits to higher (like Little Endian)"""
        if n == 0: return 0

        source = self.data.next
        # in this function while n > 0, byte always is not None
        byte = self.byte if (self.byte is not None) else source()
        bit = self.bit_index

        res = 0
        shift = 0

        if n >= 8 - bit:  # read rest of current byte
            res += (ord(byte) >> bit)
            shift += 8-bit
            n -= 8-bit
            bit = 0
            byte = source() if n > 0 else None
            self.byte_index += 1
        
            while n >= 8: # read by bytes
                res += ord(byte) << shift
                shift += 8
                n -= 8
                byte = source() if n > 0 else None
                self.byte_index += 1

        if n > 0:         # read rest of bits
            res += (((ord(byte) >> bit) & ((1 << n) - 1)) << shift)
            bit += n

        self.bit_index = bit
        self.byte = byte
        return res

    def get_be(self, n):
        """return n-bit integer, that lay in stream from higher bits to lower (like Big Endian)"""
        if n == 0: return 0

        source = self.data.next
        byte = self.byte if self.byte is not None else source()
        bit = self.bit_index

        res = 0

        # really slow code
        # effective implementation needs to reverse bits in bytes
        # the easiest way to do it is some reverse table
        # but it make code much more difficult. 
        # and anyway rewrite it in C will be much more better
        while n > 0:
            res = res * 2 + ((ord(byte) >> bit) & 1)
            bit += 1
            n -= 1

            if bit == 8:
                bit = 0                
                byte = source() if n > 0 else None
                self.byte_index += 1

        self.bit_index = bit
        self.byte = byte
        return res
    
    def finish_byte(self):
        """Skip tail of current byte"""
        if self.byte is not None:
            self.bit_index = 0
            self.byte = None
            self.byte_index += 1

    def get_byte(self):
        """Return next byte"""
        if self.bit_index != 0:
            raise Exception('Alinment error')
        b = self.data.next()
        self.byte_index += 1
        return ord(b)

    def get_bytes(self, n):
        """Return n next bytes"""
        if self.bit_index != 0:
            raise Exception('Alinment error')

        for i in xrange(n):
            yield self.data.next()
            self.byte_index += 1

class OutputStream(object):
    """Save bitstream as stream of characters"""
    def __init__(self):
        self.buffer = []
        self.byte = 0
        self.bit_index = 0

    def put_le(self, v, n):
        """Put n-bit integer l in bit sream, least bits first (like Litte Endian)"""
        if n == 0: return
        bit = self.bit_index
        byte = self.byte
        res = []

        if n + bit >= 8:
            delta = 8 - bit
            byte |= (v & ((1 << delta) - 1)) << bit
            bit = 0
            n -= delta
            v <<= delta
            res.append(byte)
            byte = 0

            while n >= 8:
                res.append(v & ((1 << 8) - 1))
                n -= 8
                v <<= 8
        
        if n > 0:
            byte |= (v & ((1 << n) - 1)) << bit
            bit += n
        
        self.bit_index = bit
        self.byte = byte
        self.buffer.extend(chr(x) for x in res)

    def put_be(self, v, n):
        """Put n-bit integer l in bit sream, highest bits first (like Big Endian)"""
        if n == 0: return
        bit = self.bit_index
        byte = self.byte
         
        while n > 0:
            byte |= ((v >> (n-1)) & 1) << bit
            bit += 1
            if bit == 8:
                bit = 0
                self.buffer.append(chr(byte))
                byte = 0
            n -= 1

        self.bit_index = bit
        self.byte = byte

    def finish(self):
        """Finish current byte"""
        self.buffer.append(chr(self.byte))
        self.byte = 0
        self.bit = 0
    
    def get(self):
        """Return result and clear buffer for new data"""
        t = self.buffer
        self.buffer = []
        return t

