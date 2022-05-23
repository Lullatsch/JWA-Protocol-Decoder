# JWA-Protocol-Decoder
This repository provides code to read messages from the game Jurassic World Alive.

It's written completely in Python 3 and requires [mitmproxy](https://github.com/mitmproxy/mitmproxy).

To run this use mitmproxy with the following command:
```
mitmproxy --mode socks5 --rawtcp -s mitm-script.py
```
The `mitm-script.py` and `parser.py` files will have to be in your current directory.

All output is written to `out/conversation[long random string].txt`

Don't mind the Errors in the mitmproxy log tab (Shift + E), they are most likely due to the script trying to read non Ludia messages.
