from prefix_code import Decoder


def decode(bs, logger=lambda x: None):
    """Decode deflate encoded data

    Input:
        - bitstream object
        - logger function for simple debugging

    Output:
        yield decoded content byte by byte
    """
    window = []

    while True:
        is_final = bs.get_le(1)
        block_type = bs.get_le(2)

        logger('BLOCK type=%s, final=%s' % (block_type, bool(is_final)))

        if block_type == 0:
            res = _decode_plain(bs, window)
        elif block_type == 1:
            res = _decode_fixed(bs, window)
        elif block_type == 2:
            res = _decode_dynamic(bs, window, logger)
        else:
            raise Exception('unknown block type: %d' % block_type)

        for s in res:
            yield s
        
        if is_final: 
            break

        if window > 2**16:
            window = window[-2**15:]  # max window size is 2**15


def _decode_plain(bs, window):
    """Decode deflate plain-data block"""
    bs.finish_byte() # align stream to byte boundary
    length = bs.get_byte() + bs.get_byte() * 256  # block lenght
    nl = bs.get_byte() + bs.get_byte() * 256      # negative lenght, just skip it

    for b in bs.get_bytes(length):
        window.append(b)
        yield b


def _decode_fixed(bs, window):
    """Decode deflate fixed-coded block"""
    # standard code lenghts for literals and match-lenghts
    lenghts  = [(i, 8) for i in range(144)]
    lenghts += [(i, 9) for i in range(144, 256)]
    lenghts += [(i, 7) for i in range(256, 280)]
    lenghts += [(i, 8) for i in range(280, 288)]

    literal_decoder = Decoder(lenghts)
    offset_decoder = Decoder([(i, 5) for i in range(32)]) # standard code lenghts for offsets

    for b in _decode_deflate_data(bs, literal_decoder, offset_decoder, window):
        yield b


def _decode_dynamic(bs, window, logger):
    """Decode deflate dynamic-coded block"""
    # read header
    hlit = bs.get_le(5)
    hdist = bs.get_le(5)
    hclen = bs.get_le(4)

    logger('HLIT = %d, HDIST = %d, HCLEN = %d' % (hlit, hdist, hclen))

    # read code lenghts for lenght-encode-commands
    len_commands_seq = [16, 17, 18, 0, 8, 7, 9, 6, 10, 5, 11, 4, 12, 3, 13, 2, 14, 1, 15]
    len_commands_lens = []

    for cmd in len_commands_seq[:hclen + 4]:
        len_commands_lens.append((cmd, bs.get_le(3))) # our Decoder allow zero lenghts

    # make lenght-encode-commands decoder
    len_commands_lens.sort() # in canonical huffman code commands located in natural order, not as in len_commands_seq!
    lens_decoder = Decoder(len_commands_lens)

    # read literals, lengths, offsets code lenghts
    lens = []

    while len(lens) < hlit + hdist + 258:
        symbol = lens_decoder.get(bs)
        if symbol < 16: # just code lenght
            lens.append(symbol)
        elif symbol == 16: # command "repeate previous symbol code lenght 3-6 times"
            count = bs.get_le(2) + 3
            lens.extend([lens[-1]] * count)
        elif symbol == 17: # command "repeate zero lenght 3-10 times"
            count = bs.get_le(3) + 3
            lens.extend([0] * count)
        elif symbol == 18: # command "repeate zero lenght 11-138 times"
            count = bs.get_le(7) + 11
            lens.extend([0] * count)

    logger('Literal lenghts: %s' % lens[:257])
    logger('Match-lenghts lenghts: %s' % lens[257:257+hlit])
    logger('Match-offset lenghts: %s' % lens[257+hlit:])

    # make decoders for literals-lenghts and offsets
    literal_decoder = Decoder(enumerate(lens[:257+hlit]))
    offset_decoder = Decoder(enumerate(lens[257+hlit:]))

    for b in _decode_deflate_data(bs, literal_decoder, offset_decoder, window):
        yield b


def _decode_deflate_data(bs, literal_decoder, offset_decoder, window):
    """Decode deflate block data"""

    # rules to convert encoded lenghts to actual lenghts
    length_rules = [
        # lower-interval-bound, upper-interval-bound, start-value, additional-bits-count
        (257, 264, 3,   0),
        (265, 268, 11,  1),
        (269, 272, 19,  2),
        (273, 276, 35,  3),
        (277, 280, 67,  4),
        (281, 284, 131, 5),
        (285, 285, 258, 0),
    ]

    while True:
        symbol = literal_decoder.get(bs)

        if symbol == 256: break         # end of block
        if symbol < 256:                # literal
            window.append(chr(symbol))
            yield chr(symbol)
            continue

        # it's a match: pair (length, offset)

        # get actual length
        for lower_bound, upper_bound, start, bits in length_rules:
            if symbol <= upper_bound:
                length = start + (1 << bits) * (symbol - lower_bound) + bs.get_le(bits)
                break
        else:
            raise Exception('unknown length')    

        # get encoded offset
        offset = offset_decoder.get(bs)

        # get actual offset
        if offset < 4:
            offset += 1
        elif offset < 30:
            bits = offset / 2 - 1         # additional offset bits
            start = (1 << (bits + 1)) + 1 # start of encoded offset interval
            offset = start + (1 << bits) * (offset % 2) + bs.get_le(bits) # actual offset
        else:
            raise Exception('unknown offset')
 
        if offset > len(window):
            raise Exception('too big offset, offset = %s' % offset)

        # unwrap match
        for i in range(length):
            yield window[-offset]
            window.append(window[-offset])

