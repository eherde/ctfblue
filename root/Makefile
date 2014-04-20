ROOT = $(abspath .)
# local root
DROOT = document-root
# install root. mutch match the entry in lighttpd.conf
DOC_ROOT = /var/www
LETC = /etc/lighttpd
LCONF = $(LETC)/lighttpd.conf
LIGHTY = /usr/sbin/lighttpd

# silence output
QUIET = >/dev/null 2>&1

# Certificate information
CERT_COUNTRY = US
CERT_STATE = CA
CERT_LOCAL = Santa Clara
CERT_ORG = Santa Clara University
CERT_UNIT = COEN 351
CERT_NAME = ctfblue
CERT_EMAIL = .
CERT = $(LETC)/server.pem

HERE = $(wildcard $(DROOT)/*.py) $(wildcard $(DROOT)/templates/*.html)
DIST = $(addprefix $(DOC_ROOT), $(subst $(DROOT),,$(HERE)))
TARGETS += $(DIST)
TARGETS += $(LCONF)
TARGETS += $(CERT)

all: $(TARGETS)

install: all
	service lighttpd restart

$(LCONF): %: $(ROOT)%
	$(LIGHTY) -t -f $< $(QUIET)
	cp $< $@

$(DOC_ROOT)/%: $(DROOT)/%
	@mkdir --parents $(@D)
	cp $< $@

.DELETE_ON_ERROR: $(CERT)
$(CERT):
	echo -en "$(CERT_COUNTRY)\n$(CERT_STATE)\n$(CERT_LOCAL)\n$(CERT_ORG)\n$(CERT_UNIT)\n$(CERT_NAME)\n$(CERT_EMAIL)\n" | \
	openssl req -new -x509 -keyout $@ -out $@ -days 365 -nodes $(QUIET)
	chmod 0400 $@

clean:
	$(RM) $(TARGETS)

.PHONY: all install clean
