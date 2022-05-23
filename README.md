# JWA-Protocol-Decoder
This repository provides code to read messages from the game Jurassic World Alive. It's written completely in Python 3 and requires [mitmproxy](https://github.com/mitmproxy/mitmproxy).

1. Set up Python and mitmproxy:
- For installing mitmproxy pls visit their guide [Mitmproxy installation](https://docs.mitmproxy.org/stable/overview-installation/).
- Install the [Mitmproxy certificate](https://docs.mitmproxy.org/stable/concepts-certificates/)
To get mitmproxy running with JWA you will need to install the mitmproxy certificate as a **system** certificate! (requires root on android).
If no root is available you would need to to rebuild the apk with a modified `network_security_config.xml`. Every time the app updates you would need to rebuild. :(

2. To run this use mitmproxy with the following command:
```
mitmproxy --mode socks5 --rawtcp -s mitm-script.py
```
The `mitm-script.py` and `parser.py` files will have to be in your current directory.

3. Setup a Socks5 proxy on your phone to redirect all traffic to your PC (I use "Socksdroid")

4. Open the game and do whatever you want!

5. All output is written to `out/conversation[long random string].txt`

In the mitmproxy log tab (Shift + E) you'll see the command names (Don't mind the errors, they are most likely due to the script trying to read non Ludia messages).

This script simply logs all messages in human readable text, you will still have to make sense of them on your own, I provided a jupyter notebook to give you an idea on how to parse the generated file.

## FAQ:
### Can this get used to cheat in the game?
No. This just reads the traffic. No modifications are done to the data

### Is this illegal?
It shouldn't be (but I'm no lawyer). The game communicates in clear text (no deciphering needed). You can use mitmproxy on your own device only.

### Can I post my recordings?
**PLEASE DO NOT POST YOUR CONVERSATION.txt ANYWHERE**. It might contain sensible data such as your private account id, login token, device- or geolocation-info.

### What do I do with this?
Uhm I don't know. I make dino usage plots of Top-N players in tournaments see: ![Example](Tournament_Champ%20RE%20All%20Skill%20BLT%20AEP-Top150.jpg)
