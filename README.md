# JWA-Protocol-Decoder
This repository provides code to read messages from the game Jurassic World Alive.

1. It's written completely in Python 3 and requires [mitmproxy](https://github.com/mitmproxy/mitmproxy).
For setting up mitmproxy I refer to their guides.

2. To run this use mitmproxy with the following command:
```
mitmproxy --mode socks5 --rawtcp -s mitm-script.py
```
The `mitm-script.py` and `parser.py` files will have to be in your current directory.

3. Setup a Socks5 proxy on your phone to redirect all traffic to your PC (I use "Socksdroid")

4. All output is written to `out/conversation[long random string].txt`

In the mitmproxy log tab (Shift + E) you'll see the command names (Don't mind the errors, they are most likely due to the script trying to read non Ludia messages).

This script simply logs all messages in human readable text, you will still have to make sense of them on your own, I provided a jupyter notebook to give you an idea on how to parse the generated file.
