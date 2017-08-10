RM            = rm -rf
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
AUTOBUILD     = sphinx-autobuild
SOURCEDIR     = .
BUILDDIR      = _build


# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS)


html:
	$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS)


server:
	@$(AUTOBUILD) "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) \
	  --watch ../oauth2 --watch ../config_loader --watch ../rest_utils


clean:
	@$(RM) $(BUILDDIR)


invclean:
	@$(RM) *.inv *.inv.txt


publish: html
	cd gh-pages; $(RM) *; touch .nojekyll
	cd _build/html; cp -a * ../../gh-pages/
