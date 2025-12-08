# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
BUILDDIR      = build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile pre-build

# Define pre-build target to run custom scripts
pre-build:
	@echo "Running pre-build scripts..."
	@python  "$(SOURCEDIR)/generate_sp_docs.py"
	@python  "$(SOURCEDIR)/generate_autorst.py"

# Modify the 'html' target to depend on 'pre-build'
html: pre-build
	@echo "Building HTML documentation..."
	@$(SPHINXBUILD) -b html "$(SOURCEDIR)" "$(BUILDDIR)/html" $(SPHINXOPTS) $(O)
	@echo "HTML documentation built successfully."

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option, after running pre-build scripts.
%: pre-build Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
