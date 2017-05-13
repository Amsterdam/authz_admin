.PHONY: authorization_service test testcov testcovclean clean distclean docs_*

RM = rm -rf

# `pytest` and `python -m pytest` are equivalent, except that the latter will
# add the current working directory to sys.path. We don't want that; we want
# to test against the _installed_ package(s), not against any python sources
# that are (accidentally) in our CWD.
PYTEST = pytest

# The ?= operator below assigns only if the variable isn't defined yet. This
# allows the caller to override them::
#
#     TESTS=other_tests make test
#
PYTEST_OPTS ?= -p no:cacheprovider --capture=no --verbose
TESTS ?= tests


authorization_service:
	. tma.env; \
	authorization_service


test:
	$(PYTEST) $(PYTEST_OPTS) $(TESTS)


testcov:
	$(PYTEST) --cov-config .coveragerc --cov=oauth2 --cov-report=term $(TESTS)

testcov_clean:
	@$(RM) .cache .coverage


clean: testcov_clean
	@$(RM) build/ *.egg-info/ .eggs/ dist/
	@find . \( \
		-iname "*.pyc" \
		-or -iname "*.pyo" \
		-or -iname "*.so" \
		-or -iname "*.o" \
		-or -iname "*~" \
		-or -iname "._*" \
		-or -iname "*.swp" \
		-or -iname "Desktop.ini" \
		-or -iname "Thumbs.db" \
		-or -iname "__MACOSX__" \
		-or -iname ".DS_Store" \
		\) -delete


# @evert waar komt dit eigenlijk vandaan?
distclean: clean
	@$(RM) \
		dist/ \
		bin/ \
		develop-eggs/ \
		eggs/ \
		parts/ \
		MANIFEST \
		htmlcov/ \
		.installed.cfg


docs_%:
	$(MAKE) -C docs $*
