import struct


class Parser:
    def __init__(self):
        self.rest_msg = b''
        self.states = {
            0: 'idle',
            1: 'awaiting',
            2: 'skipping'
        }
        self.state = self.states[0]

    def decode(self, msg):
        parsed = []
        if self.rest_msg == b'' and msg == b'':  # nothing to do and no new message
            return parsed
        if self.rest_msg == b'':
            self.rest_msg = msg
        else:
            self.rest_msg += msg
        if not is_ludia_message(self.rest_msg):  # throw away this garbage (or save?)
            self.rest_msg = self.rest_msg[
                            1:]  # Skipping one byte only. It's safer but for long non ludia messages this might be a bad idea.
            return self.decode(msg=b'')  # Call again with skipped bytes
        else:  # our current msg is probably a ludia msg!
            msg_type, pl_len, pl, msg_left = parse_message_info(self.rest_msg)
            if pl_len == len(pl):  # All good!
                self.state = self.states[0]
                self.rest_msg = msg_left
                return [parse_payload(pl)] + self.decode(msg=b'')
            elif pl_len > len(pl):  # We need to wait for more
                self.state = self.states[1]
                return parsed
            else:
                # print("How did i get here. Payload too long. Skipping again?" )
                self.rest_msg = self.rest_msg[1:]
                return self.decode(msg=b'')


# Big thanks to iGio90 for their helpful document! https://github.com/JWA-Developers/Documentation/blob/master/PROTOCOL.md
def parse_message_info(message):
    message_type = struct.unpack_from('>B', message)[0]
    payload_length = -1
    payload = b''
    message_left = b''
    if message_type == 0x80:
        payload_length = struct.unpack_from('>H', message, 1)[0]
        payload = message[3:3 + payload_length]
        message_left = message[3 + payload_length:]
    elif message_type == 0x88:
        payload_length = struct.unpack_from('>I', message, 1)[0]
        payload = message[5:5 + payload_length]
        message_left = message[5 + payload_length:]
    return message_type, payload_length, payload, message_left


def is_ludia_message(message):
    message_type = struct.unpack_from('>B', message)[0]
    return (message_type == 0x80) or (message_type == 0x88)


def parse_message(message):
    parsed = []
    offset = 0
    while offset < len(message):
        unhexed = message[offset:]
        message_type = struct.unpack_from('>B', unhexed)[0]
        if message_type == 0x80:
            payload_length = struct.unpack_from('>H', unhexed, 1)[0]
            payload = unhexed[3:3 + payload_length]
            offset += 3 + payload_length
        elif message_type == 0x88:
            payload_length = struct.unpack_from('>I', unhexed, 1)[0]
            payload = unhexed[5:5 + payload_length]
            offset += 5 + payload_length
        else:
            print(f'unknown payload. {unhexed[0:10]} skipping bytes one by one.')
            offset += 1
            continue
        try:
            print(payload_length, end=' |')
            parsed.append(parse_payload(payload)[0])
        except:
            print('something went wrong:')
    if len(parsed) == 1:
        return parsed[0]
    else:
        return parsed


def parse_payload(payload):
    parsed = []
    offset = 0
    while offset < len(payload):
        pl = payload[offset:]
        v, off, byte_types, byte_values = read_single_attr(pl)
        parsed.append([v, byte_types, byte_values])
        offset += off
    if len(parsed) == 1:
        return parsed[0]
    else:
        return parsed


def read_single_attr(p):
    v, off, bts, btv = _read_single_attr(p)
    return v, off, bts, btv


def _read_single_attr(p):
    bts = []
    btv = []
    attr_prefix = struct.unpack_from('>B', p, 0)[0]
    bts += ['>B']
    btv += [attr_prefix]
    attr_key = None
    off = struct.calcsize('>B')
    if attr_prefix == 18:  # Reading dict
        a_len = struct.unpack_from('>h', p, off)[0]
        off += struct.calcsize('>h')
        bts += ['>h']
        btv += [a_len]
        v, off_temp, btsa, btva = parse_array_or_dict(p[off:], a_len)  # TODO: here
        bts += [btsa]
        btv += [btva]
        off += off_temp
    elif attr_prefix == 17:  # reading array
        a_len = struct.unpack_from('>h', p, off)[0]
        off += struct.calcsize('>h')
        bts += ['>h']
        btv += [a_len]
        v, off_temp, btsa, btva = parse_array(p[off:], a_len)
        bts += [btsa]
        btv += [btva]
        off += off_temp
    elif attr_prefix == 1:  # byte
        v = struct.unpack_from('>B', p, off)[0]
        off += struct.calcsize('>B')
        bts += ['>B']
        btv += [v]
    elif attr_prefix == 4:  # int
        v = struct.unpack_from('>i', p, off)[0]
        off += struct.calcsize('>i')
        bts += ['>i']
        btv += [v]
    elif attr_prefix == 5:  # long
        v = struct.unpack_from('>q', p, off)[0]
        off += struct.calcsize('>q')
        bts += ['>q']
        btv += [v]
    elif attr_prefix == 8:  # string
        s_len = struct.unpack_from('>h', p, off)[0]
        off += struct.calcsize('>h')
        bts += ['>h']
        btv += [s_len]
        v = struct.unpack_from('>{}s'.format(s_len), p, off)[0].decode('iso-8859-2')
        off += struct.calcsize('>{}s'.format(s_len))
        bts += [f'>{s_len}s']
        btv += [v]
    elif attr_prefix == 0:  # standard?
        attr_key_len = struct.unpack_from('>B', p, off)[0]
        off += struct.calcsize('>B')
        bts += ['>B']
        btv += [attr_key_len]
        attr_key, attr_type = struct.unpack_from('>{}sb'.format(attr_key_len), p, off)
        attr_key = attr_key.decode('iso-8859-2')
        off += struct.calcsize('>{}sb'.format(attr_key_len))
        bts += [f'>{attr_key_len}s', '>b']
        btv += [attr_key, attr_type]

        if attr_type == 0:  # empty
            v = struct.unpack_from('>x', p, off)
            bts += ['>x']
            btv += [v]
            # print('empty')
            off += 0
        elif attr_type == 1:  # byte
            # print('byte')
            v = struct.unpack_from('>B', p, off)[0]  # maybe different
            off += struct.calcsize('>B')
            bts += ['>B']
            btv += [v]
        elif attr_type == 2:  # bool?
            # print('bool')
            v = struct.unpack_from('>?', p, off)[0]
            off += struct.calcsize('>?')
            bts += ['>?']
            btv += [v]
        elif attr_type == 3:  # short
            v = struct.unpack_from('>h', p, off)[0]
            off += struct.calcsize('>h')
            bts += ['>h']
            btv += [v]
        elif attr_type == 4:  # int
            v = struct.unpack_from('>i', p, off)[0]
            off += struct.calcsize('>i')
            bts += ['>i']
            btv += [v]
        elif attr_type == 5:  # long
            v = struct.unpack_from('>q', p, off)[0]
            off += struct.calcsize('>q')
            bts += ['>q']
            btv += [v]
        elif attr_type == 8:  # string
            s_len = struct.unpack_from('>h', p, off)[0]
            off += struct.calcsize('>h')
            bts += ['>h']
            btv += [s_len]
            v = struct.unpack_from('>{}s'.format(s_len), p, off)[0].decode('iso-8859-2')
            off += struct.calcsize('>{}s'.format(s_len))
            bts += ['>{}s'.format(s_len)]
            btv += [v]
        elif attr_type == 17:  # short + attr_array
            a_len = struct.unpack_from('>h', p, off)[0]
            off += struct.calcsize('>h')
            bts += ['>h']
            btv += [a_len]
            v, n_off, btsa, btva = parse_array(p[off:], a_len)  # TODO here
            bts += [btsa]
            btv += [btva]
            off += n_off
        elif attr_type == 18:  # short + attr_array
            a_len = struct.unpack_from('>h', p, off)[0]
            off += struct.calcsize('>h')
            bts += ['>h']
            btv += [a_len]
            v, n_off, btsa, btva = parse_array_or_dict(p[off:], a_len)
            bts += [btsa]
            btv += [btva]
            off += n_off
        else:
            print('unknown parse attr-type', attr_type)
            v = None
    else:
        print(attr_prefix, ' prefix not implemented yet')
        return None, None, None
    if attr_key is None:
        return v, off, bts, btv
    else:
        return {attr_key: v}, off, bts, btv


def parse_array(payload, n_attr):  # parses an array with specified length
    ret_values = []
    offset = 0
    btsa = []
    btva = []
    for i in range(n_attr):
        d, off, bts, btv = read_single_attr(payload[offset:])
        btsa.append(bts)
        btva.append(btv)
        ret_values.append(d)
        offset += off
    return ret_values, offset, btsa, btva


def parse_array_or_dict(payload, n_attr):  # parses a dict with specified length
    ret_values = []
    offset = 0
    is_dict = True
    btsa = []
    btva = []
    for i in range(n_attr):
        d, off, bts, btv = read_single_attr(payload[offset:])
        btsa.append(bts)
        btva.append(btv)
        if not type(d) == dict:
            is_dict = False
        ret_values.append(d)
        offset += off
    if is_dict:
        ret_dict = {}
        for d in ret_values:
            for k, v in d.items():
                ret_dict[k] = v
        return ret_dict, offset, btsa, btva
    else:
        return ret_values, offset, btsa, btva
