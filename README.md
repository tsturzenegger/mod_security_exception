This script is intended to build a whitelist for mod_security. This script takes all blocked request and builds an exception rule list.
You can overwrite the input file and specify a secure IP address. This is intended for systems already in production and might had faced real attacks.

Optional switches:

-f:     Overwrite default input file (default /var/log/httpd/modsec_audit.log)
-s:     Only use events generated by this IP address
-t:     Sets threshold until creation of wildcard exclusion for rule (default 3)
-o:	Sets threshold until creation of wildcard exclusion for directory (default 5)

Example: rule.py-f ./modsec_audit.log -s 192.168.20.2
