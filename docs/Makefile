# .PHONY: help server clean inv

RM            = rm -rf
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
AUTOBUILD     = sphinx-autobuild
SOURCEDIR     = .
BUILDDIR      = _build


# Put it first so that "make" without argument is like "make help".
help:
	echo $(0)
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS)


html:
	$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS)


server:
	@$(AUTOBUILD) "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) \
	  --watch ../oauth2 --watch ../config_loader


clean:
	@$(RM) $(BUILDDIR) *.inv *.inv.txt
