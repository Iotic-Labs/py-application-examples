# Iotic Labs HTTPS Proxy for QAPI

The QAPI Proxy provides a HTTP/RESTful interface to the Iotic-labs Queue API.  The HTTP interface
can be secure (TLS 1.2) or insecure (plain HTTP) as you wish.

### What it's for
The Proxy exists for 2 reasons
1. It's part of the Iotic-Labs web infrastructure and allows the Iotic Space web-app acts as an Iotic Thing
2. To provide an agent for devices that are too constrained to run one themselves.
This might be because they aren't able to run python or don't have sufficient processing power to run TLS 1.2.

### Limitations.
1. The proxy does not expose the full qapi functionality, but it's reasonably easy to add new functions c.f. metahelper

## Requires

- Python3 (tested with 3.4.3)

If using src release:
- py-IoticAgent https://github.com/Iotic-Labs/py-IoticAgent
- Optional/ mysqlclient https://pypi.python.org/pypi/mysqlclient
- Optional/ rdflib to enable GET PUT /entity /point ... /metahelper URLs


## Config Options

qapiproxy can load all it's config from an ini file.
Optionally storing Agent credentials a MySQL database.

- Common settings
```ini
[https]
; host and port of the RESTServer instance
host = 10.0.1.2
port = 8118
; SSL files
ssl_ca = /path/to/ca.bundle or proxy.crt if self-signed
ssl_crt = /path/to/proxy.crt
ssl_key = /path/to/proxy.key
; If ssl_key is protected by a password
ssl_pass = password

[qapimanager]
; how often (seconds) to check the config for new agents, 0 to disable
new_worker = 5
; How many unsolicited messages each Agent should store, 0 to disable
; feeddata and controlreq and unsolicited (EG reassigned, new subscriber etc)
keep_feeddata = 50
keep_controlreq = 50
keep_unsolicited = 50
; If your broker requires a self signed certificate or username prefix or vhost
; they can be specified here and will extend all agent details (DB or ini)
; vhost = example
; prefix = example
; sslca = example
```

- ini or mysql
```ini
[config]
; mode can be 'ini' or 'mysql'
mode = mysql
; if mode = mysql
dbhost = host
dbport = port
dbname = database name
dbuser = username
dbpass = password

; if mode = ini a list of 1..n agents can be stored

agents = name
; or multiple on newline
agents =
    nameOne
    nameTwo
    nameThree

; for each
[nameOne]
; agent credentials
host = host
vhost = vhost
epId = epId
password = password
; authTokens are HTTPS api keys that allow a remote thing to use this Agent
authtokens = token
; of multiple lines
authtokens =
    token
    token
    token
; if vhost, prefix or sslca not specified in qapimanager
; can be specified here for this agent only (ini only)
; vhost = xx
; prefix = xy
; sslca = xz
```


## Install

Build (If using src release)
-------
1) Create .pyz:
    cd src && ./make_pyz.sh
2) Run in current directory (as current user):
    PYTHONPATH=qapiproxy.pyz python3 -mqapiproxy qapiproxy.cfg


Service
-------
qapiproxy.init is an LSB 4.1 compatible service script. See configuration options at the top of said script for
setup. (The qapiproxyy should be run as non-root user.)

Using the service to run qapiproxy in the background:
```shell
# Create a directory for the log file
mkdir data
# Put the config in the expected location
ln -sfv cfg/example.ini qapiproxy.cfg
# Start the service
./qapiproxy.init start
# Follow the log
tail -f data/qapiproxy.log
# Stop the service
./qapiproxy.init stop
```

For system service:
- edit qapiproxy.init QAPIPROXY_RUN_DIR and QAPIPROXY_USER
- cp qapiproxy.init /etc/init.d/qapiproxy
- chmod a+x /etc/init.d/qapiproxy
- chkconfig --add qapiproxy
- chkconfig qapiproxy off  # Don't start automatically since depends on everything running already
- sudo service qapiproxy start
