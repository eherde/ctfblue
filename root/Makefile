ROOT = $(abspath .)
# local root
DROOT = document-root
# install root. must match the entry in lighttpd.conf
DOC_ROOT = /var/www
LETC = /etc/lighttpd
LCONF = $(LETC)/lighttpd.conf
LIGHTY = /usr/sbin/lighttpd
USER = www-data

# silence output
QUIET = >/dev/null 2>&1

GITVER = $(shell git rev-parse --short HEAD)
VERSION = $(shell eval $$(cat version) && echo $$VERSION)

# Certificate information
CERT_COUNTRY = US
CERT_STATE = CA
CERT_LOCAL = Santa Clara
CERT_ORG = Santa Clara University
CERT_UNIT = COEN 351
CERT_NAME = ctfblue
CERT_EMAIL = .
CERT = $(LETC)/server.pem

# code targets
HERE += $(wildcard $(DROOT)/*.py)
HERE += $(wildcard $(DROOT)/lib/*.py)
HERE += $(wildcard $(DROOT)/ctf-data/*.yaml)
HERE += $(wildcard $(DROOT)/templates/*.html)
DIST = $(addprefix $(DOC_ROOT), $(subst $(DROOT),,$(HERE)))
TARGETS += $(DIST)
TARGETS += $(LCONF)
TARGETS += $(CERT)

# documentation targets
DOXYFILE=$(DROOT)/Doxyfile

all: $(TARGETS)

install: all
	chown -R $(USER):$(USER) $(DOC_ROOT)
	service lighttpd restart

$(DOXYFILE): $(DOXYFILE).template
	sed --expression 's/GITVER/$(GITVER)/' --expression 's/VERSION/$(VERSION)/' $< > $@

pdf: $(DOXYFILE)
	cd $(DROOT) && doxygen
	$(MAKE) -C $(DROOT)/latex

$(LCONF): %: $(ROOT)%
	$(LIGHTY) -t -f $< $(QUIET)
	cp $< $@

$(DOC_ROOT)/%.py: $(DROOT)/%.py
	@mkdir --parents $(@D)
	@# compile-check each file
	@python -c "__import__('compiler').parse(open('$<').read())"
	@# run unit tests
	@if [ "$(shell basename $<)" != "service.py" ]; then python $<; fi
	@cp $< $@

$(DOC_ROOT)/templates/%.html: $(DROOT)/templates/%.html
	@mkdir --parents $(@D)
	cp $< $@

$(DOC_ROOT)/ctf-data/%.yaml: $(DROOT)/ctf-data/%.yaml
	@mkdir --parents $(@D)
	cp $< $@

.DELETE_ON_ERROR: $(CERT)
$(CERT):
	@echo -en "$(CERT_COUNTRY)\n$(CERT_STATE)\n$(CERT_LOCAL)\n$(CERT_ORG)\n$(CERT_UNIT)\n$(CERT_NAME)\n$(CERT_EMAIL)\n" | \
	openssl req -new -x509 -keyout $@ -out $@ -days 365 -nodes $(QUIET)
	@chmod 0400 $@

clean:
	$(RM) $(TARGETS)
	$(RM) -r $(DROOT)/html $(DROOT)/latex
	@find . -name "*.pyc" -delete

.PHONY: all install clean pdf
