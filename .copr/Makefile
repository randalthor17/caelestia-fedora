# .copr/Makefile
#
# COPR "custom" source method entry point. Run by COPR build workers as:
#   make -f .copr/Makefile srpm outdir="$outdir"
#
# This replaces the network calls install.fish made *during installation*
# (git clone of the cli/shell repos, wget of nerd-fonts/material-symbols
# release assets, pip install of materialyoucolor) with fetches that happen
# once, at *package build* time, so the resulting RPM has no install-time
# network dependency at all.

outdir ?= $(CURDIR)/outdir
specfile := SPECS/caelestia-fedora.spec

NERDFONTS_VER := v3.4.0
MYC_VER := 3.0.2

.PHONY: srpm get_sources

srpm: get_sources
	rpmbuild -bs \
		--define "_sourcedir $(CURDIR)" \
		--define "_srcrpmdir $(outdir)" \
		$(specfile)

get_sources:
	@echo "==> Fetching dotfiles, cli, and shell source tarballs"
	curl -fsSL -o caelestia-fedora-fedora.tar.gz \
		https://github.com/EnceladusII/caelestia-fedora/archive/refs/heads/fedora.tar.gz
	curl -fsSL -o caelestia-fedora-cli-main.tar.gz \
		https://github.com/EnceladusII/caelestia-fedora-cli/archive/refs/heads/main.tar.gz
	curl -fsSL -o caelestia-fedora-shell-main.tar.gz \
		https://github.com/EnceladusII/caelestia-fedora-shell/archive/refs/heads/main.tar.gz
	@echo "==> Fetching materialyoucolor sdist (no Fedora package exists upstream)"
	curl -fsSL -o materialyoucolor-$(MYC_VER).tar.gz \
		https://files.pythonhosted.org/packages/source/m/materialyoucolor/materialyoucolor-$(MYC_VER).tar.gz
	@echo "==> Vendoring fonts (replaces install.fish's wget-at-install-time)"
	mkdir -p fonts-vendor
	curl -fsSL -o /tmp/CascadiaCode.zip \
		https://github.com/ryanoasis/nerd-fonts/releases/download/$(NERDFONTS_VER)/CascadiaCode.zip
	curl -fsSL -o /tmp/JetBrainsMono.zip \
		https://github.com/ryanoasis/nerd-fonts/releases/download/$(NERDFONTS_VER)/JetBrainsMono.zip
	unzip -o -j /tmp/CascadiaCode.zip '*.ttf' -d fonts-vendor
	unzip -o -j /tmp/JetBrainsMono.zip '*.ttf' -d fonts-vendor
	curl -fsSL -o "fonts-vendor/MaterialSymbolsRounded.ttf" \
		"https://github.com/google/material-design-icons/raw/master/variablefont/MaterialSymbolsRounded%5BFILL,GRAD,opsz,wght%5D.ttf"
	curl -fsSL -o "fonts-vendor/MaterialSymbolsOutlined.ttf" \
		"https://github.com/google/material-design-icons/raw/master/variablefont/MaterialSymbolsOutlined%5BFILL,GRAD,opsz,wght%5D.ttf"
	curl -fsSL -o "fonts-vendor/MaterialSymbolsSharp.ttf" \
		"https://github.com/google/material-design-icons/raw/master/variablefont/MaterialSymbolsSharp%5BFILL,GRAD,opsz,wght%5D.ttf"

# One-time setup on the COPR project itself (not run by the build worker;
# run this yourself with copr-cli before the first build). These four COPRs
# were each individually verified against packages.fedoraproject.org and the
# Fedora Copr search before being chosen -- in particular, hyprpicker/hypridle
# come from solopasha/hyprland, NOT install.fish's original aneagle/ags-3,
# which does not actually carry those two packages at all:
#
#   copr-cli add-build-dependency <your-project> atim/starship
#   copr-cli add-build-dependency <your-project> solopasha/hyprland
#   copr-cli add-build-dependency <your-project> errornointernet/quickshell
#   copr-cli add-build-dependency <your-project> celestelove/app2unit
#
# This is the declarative equivalent of install.fish's
#   sudo dnf copr enable atim/starship
#   sudo dnf copr enable aneagle/ags-3   (WRONG -- see above)
#   sudo dnf copr enable errornointernet/quickshell
#
# NOTE: wl-screenrec and cliphist are intentionally NOT covered by a COPR
# dependency here -- there is no single canonical/maintained one for either.
# See README.md for details and options.
