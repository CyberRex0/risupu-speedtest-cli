# risupu-speedtest-cli
Command Line Tool for RisuPu SpeedTest

# Requirements
- Chrome

- ChromeDriver (same version with Chrome)

- Selenium

- requests

- Python3.8 or higher

Install these modules on Windows:

```
py -3 -m pip install -U selenium chromedriver_binary
```

# Usage
## Normal (Auto)
`python3 risupu-speedtest-cli.py`

## Show the list of measure servers
`python3 risupu-speedtest-cli.py --list`

## Select server manually
`python3 risupu-speedtest-cli.py --server-id SERVER_ID`

## Save result image
`python3 risupu-speedtest-cli.py --save-image`

## Hide ISP Information
`python3 risupu-speedtest-cli.py --hide-isp`

# Troubleshooting
## Version mismatch
```
ERROR: An unknown error occured.
Message: session not created: This version of ChromeDriver only supports Chrome version 92
Current browser version is 91.0.4439.0 with binary path /home/user/chrome-linux/chrome
```

To fix this error, update Chrome or downgrade chromedriver_binary.

```
pip install -U "chromedriver_binary<=91.9"
```

## Chrome not found
```
ERROR: Chrome is not installed.
```

To fix this error, please install Chrome.

# About
Speedtest servers by RisuPu

✅ *Offical Software*

(C)2021 rspnet.jp, CyberRex
