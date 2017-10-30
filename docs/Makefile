RM            = rm -rf
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
AUTOBUILD     = sphinx-autobuild --watch ../src --port 8001
SOURCEDIR     = .
BUILDDIR      = _build


# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) --help


html:
	$(SPHINXBUILD) -b html $(SPHINXOPTS) "$(SOURCEDIR)" "$(BUILDDIR)"


server:
	@$(AUTOBUILD) --watch ../src --port 8001 $(SPHINXOPTS) "$(SOURCEDIR)" "$(BUILDDIR)"


clean:
	@$(RM) $(BUILDDIR)


invclean:
	@$(RM) *.inv *.inv.txt


publish: html
	cd gh-pages && $(RM) *
	cd _build && cp -a * ../gh-pages/
