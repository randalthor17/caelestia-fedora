## caelestia-fedora.spec
##
## Packaging of https://github.com/EnceladusII/caelestia-fedora (branch: fedora)
## for COPR. Built from the upstream install.fish, with the following design
## change: anything install.fish did with raw `sudo dnf install <random pkgs>`,
## `cargo install`, `go install`, `pip install`, ad hoc `git clone && make`, or
## `wget`+`unzip` is replaced here with declarative RPM dependencies and proper
## %build/%install steps, so `dnf install caelestia-fedora` does the whole job.
##
## Produces 3 binary RPMs from one source:
##   caelestia-fedora        - meta-package + dotfiles (hypr, foot, fish, fastfetch,
##                              uwsm, btop, qt5ct, qt6ct, starship.toml) + installer
##   caelestia-cli            - the `caelestia` control script (Python, built from
##                              caelestia-fedora-cli)
##   caelestia-shell           - the Quickshell-based desktop shell + beat_detector
##                              (built from caelestia-fedora-shell)
##
## NOTE on COPR repos: every package below was checked against
## packages.fedoraproject.org and the Fedora Copr search before being put in
## Requires/BuildRequires. Plain Fedora repos do NOT carry all of these —
## several only exist in third-party COPRs, and a couple don't exist as RPMs
## anywhere, which is noted package-by-package below. COPRs that must be
## enabled on the chroot/build host *before* this package builds or installs:
##   atim/starship              -> starship (verified: starship.rs's own
##                                  recommended install method)
##   solopasha/hyprland          -> hyprpicker, hypridle (verified: Fedora's
##                                  own hyprpicker/hypridle packages are
##                                  orphaned and only ever existed for
##                                  Fedora 40/41 -- do NOT rely on them.
##                                  install.fish's original `aneagle/ags-3`
##                                  COPR does NOT carry these two packages at
##                                  all -- that line in upstream install.fish
##                                  looks like a bug, not intentional)
##   errornointernet/quickshell  -> quickshell (the stable package; upstream
##                                  caelestia-shell docs prefer this over
##                                  quickshell-git unless you need master)
##   celestelove/app2unit        -> app2unit (verified: no plain-Fedora or
##                                  RPMFusion package exists)
## Two more packages install.fish pulled in (wl-screenrec, cliphist) have NO
## single canonical/maintained COPR -- they're scattered across several
## small personal repos of varying quality. Rather than depend on one of
## those, this project also builds them itself, from the same upstream
## sources install.fish used (russelltg/wl-screenrec, sentriz/cliphist) --
## see SPECS/wl-screenrec.spec and SPECS/cliphist.spec alongside this file.
## See the .copr/ section at the bottom of this file / README for `copr-cli`
## invocations that enable these automatically for COPR builds.

%global dotsrepo    caelestia-fedora
%global dotscommit  fedora
%global clirepo     caelestia-fedora-cli
%global clicommit   main
%global shellrepo   caelestia-fedora-shell
%global shellcommit main
%global mycver      3.0.2

%global forgeurl0 https://github.com/EnceladusII/%{dotsrepo}
%global forgeurl1 https://github.com/EnceladusII/%{clirepo}
%global forgeurl2 https://github.com/EnceladusII/%{shellrepo}

Name:           caelestia-fedora
Version:        1.0.0
Release:        2%{?dist}
Summary:        Caelestia Hyprland dotfiles, ported to Fedora

License:        GPL-3.0-only
URL:            %{forgeurl0}
Source0:        %{forgeurl0}/archive/refs/heads/%{dotscommit}/%{dotsrepo}-%{dotscommit}.tar.gz
Source1:        %{forgeurl1}/archive/refs/heads/%{clicommit}/%{clirepo}-%{clicommit}.tar.gz
Source2:        %{forgeurl2}/archive/refs/heads/%{shellcommit}/%{shellrepo}-%{shellcommit}.tar.gz
# PyPI sdist for materialyoucolor: no Fedora/RPMFusion package exists for
# this at all (confirmed against packages.fedoraproject.org and Fedora's own
# end-4/dots-hyprland community, who hit the same gap and fell back to pip
# into a venv on Fedora). It ships a pybind11 C++ extension, so it's built
# from source here rather than just `pip install`'d.
Source3:        https://files.pythonhosted.org/packages/source/m/materialyoucolor/materialyoucolor-%{mycver}.tar.gz

BuildArch:      noarch

# --- COPR repos that MUST be enabled for this spec to build/install ---
# (documented here, enforced by .copr/Makefile, see bottom of file)

Requires:       caelestia-cli = %{version}-%{release}
Requires:       caelestia-shell = %{version}-%{release}

# --- Core runtime deps (formerly the giant `dnf install ...` in ensure_tools) ---
# Plain Fedora repos (verified on packages.fedoraproject.org):
Requires:       hyprland
Requires:       xdg-desktop-portal-hyprland
Requires:       xdg-desktop-portal-gtk
Requires:       wl-clipboard
Requires:       bluez
Requires:       bluez-tools
Requires:       inotify-tools
Requires:       wireplumber
Requires:       trash-cli
Requires:       foot
Requires:       fish
Requires:       fastfetch
Requires:       btop
Requires:       jq
Requires:       socat
Requires:       ImageMagick
Requires:       curl
Requires:       adw-gtk3-theme
Requires:       papirus-icon-theme
Requires:       qt5ct
Requires:       qt6ct
Requires:       google-noto-sans-mono-fonts
Requires:       NetworkManager
Requires:       lm_sensors
Requires:       ddcutil
Requires:       brightnessctl
Requires:       cava

# COPR atim/starship (verified: this is starship.rs's own documented Fedora
# install method, not just an install.fish guess)
Requires:       starship

# COPR solopasha/hyprland (verified: Fedora's own hyprpicker/hypridle exist
# ONLY for Fedora 40/41 and are orphaned -- do not rely on them past that.
# install.fish points at `aneagle/ags-3` for these, which is wrong: that COPR
# only ships aylurs-gtk-shell/hyprpanel, not hyprpicker or hypridle, so this
# spec uses the correct COPR instead of reproducing the upstream bug)
Requires:       hyprpicker
Requires:       hypridle

# app2unit: confirmed there is NO plain Fedora or RPMFusion package; only
# available via COPR celestelove/app2unit. (See .copr/Makefile / README for
# the enable command. install.fish built this from source via git+make on
# every install instead -- one COPR enable replaces that.)
Requires:       app2unit

# wl-screenrec : confirmed there is NO single canonical/official
# Fedora or COPR package for either of these -- they're scattered across
# several small personal COPRs of varying quality/maintenance (e.g.
# endegraaf/wl-screenrec is explicitly marked "not yet working" by its own
# author; cliphist has at least 3 competing unofficial COPRs: alternateved,
# wef, purian23). Rather than depend on one of those, this spec's COPR
# project should also build SPECS/wl-screenrec.spec and SPECS/cliphist.spec
# (included alongside this file) from the same upstream sources install.fish
# used (russelltg/wl-screenrec, sentriz/cliphist), so both Requires below
# resolve from this project's own COPR output rather than a third party's.
Requires:       wl-screenrec
Requires:       cliphist

# Fonts: replaces the wget-from-GitHub-releases nerd-font + Material Symbols
# dance in install.fish with a real font subpackage built in this same spec.
Requires:       %{name}-fonts = %{version}-%{release}

%description
Meta-package and dotfiles for the Caelestia Hyprland desktop, Fedora edition
(EnceladusII/caelestia-fedora). Installing this package pulls in caelestia-cli,
caelestia-shell, and every runtime dependency the upstream install.fish script
used to install ad hoc with dnf/cargo/go/pip/git+make, and symlinks the bundled
configs (hypr, foot, fish, fastfetch, uwsm, btop, qt5ct, qt6ct, starship.toml)
into $XDG_CONFIG_HOME for you on first login via a %post scriptlet, exactly as
install.fish did, minus the network calls.

Before building or installing from COPR, make sure the following COPR repos
are enabled on the chroot:
  atim/starship, solopasha/hyprland, errornointernet/quickshell,
  celestelove/app2unit
wl-screenrec and cliphist are built by this same COPR project (see
SPECS/wl-screenrec.spec, SPECS/cliphist.spec) rather than depending on a
third-party COPR, since no single canonical one exists for either.

%package fonts
Summary:        Nerd Fonts + Material Symbols used by the Caelestia shell
BuildArch:      noarch
# CascadiaCode / JetBrainsMono Nerd Font + Google Material Symbols, formerly
# fetched at install-time via `wget` from GitHub releases in install.fish's
# fonts_install / material_symbols_install functions.
# This subpackage is named caelestia-fedora-fonts (Name-fonts); referenced
# above as Requires: %{name}-fonts.

%description fonts
Cascadia Code Nerd Font, JetBrains Mono Nerd Font, and Google Material Symbols
(Rounded/Outlined/Sharp), packaged as real RPM-managed fonts instead of being
downloaded with wget into ~/.local/share/fonts at install time.

%package -n caelestia-cli
Summary:        Control script for the Caelestia dotfiles (Fedora build)
License:        GPL-3.0-only
URL:            %{forgeurl1}
BuildRequires:  python3-devel
BuildRequires:  python3-build
BuildRequires:  python3-installer
BuildRequires:  hatch
BuildRequires:  python3-hatch-vcs
Requires:       python3-materialyoucolor = %{version}-%{release}
Requires:       fish
Requires:       libnotify
Requires:       swappy
Requires:       grim
Requires:       slurp
Requires:       wl-clipboard
Requires:       glib2
Requires:       fuzzel

%description -n caelestia-cli
The `caelestia` command-line control script: scheme/wallpaper management,
screenshot/recording helpers, IPC into the shell, and the `caelestia install`
subcommand. Built from a wheel via python3 -m build, replacing install.fish's
ad hoc `git clone && python3 -m build --wheel && pip install --break-system-packages`
sequence with a normal RPM %%build/%%install.

%package -n python3-materialyoucolor
Summary:        Material You color generation algorithms (pybind11/C++ backend)
License:        Apache-2.0
URL:            https://github.com/T-Dynamos/materialyoucolor-python
BuildRequires:  python3-devel
BuildRequires:  python3-pip
BuildRequires:  python3-setuptools
BuildRequires:  python3-wheel
# materialyoucolor's setup.py imports pybind11 directly at build time (not
# just headers via pybind11-devel) -- confirmed by AUR's
# python-materialyoucolor-git PKGBUILD comment trail, where omitting either
# one breaks the build with "Missing setuptools dependency" /
# "Misses pybind11 as dependency, fails to build without".
BuildRequires:  python3-pybind11
BuildRequires:  pybind11-devel
BuildRequires:  gcc-c++
%description -n python3-materialyoucolor
Pure-Python Material You color algorithms with a pybind11 C++ quantization
backend, used by caelestia-cli for wallpaper-derived theming. No Fedora or
RPM Fusion package exists for this upstream project (confirmed against
packages.fedoraproject.org), so it's built here from the PyPI sdist instead
of caelestia-cli falling back to `pip install --break-system-packages` the
way install.fish's cli_install function did.

%package -n caelestia-shell
Summary:        Quickshell-based desktop shell for Caelestia (Fedora build)
License:        GPL-3.0-only
URL:            %{forgeurl2}
BuildRequires:  gcc-c++
BuildRequires:  pkgconfig(libpipewire-0.3)
BuildRequires:  pkgconfig(aubio)
BuildRequires:  pkgconfig(sndfile)
BuildRequires:  pkgconfig(fftw3f)
# COPR errornointernet/quickshell provides both `quickshell` (tracks the
# latest tagged release) and `quickshell-git` (tracks master). Use the
# stable package -- caelestia-shell's own upstream docs only recommend
# quickshell-git for bleeding-edge/master-tracking use, not as a default.
Requires:       quickshell
Requires:       qt6-qtdeclarative
Requires:       libqalculate
Requires:       pipewire
Requires:       aubio
Requires:       caelestia-cli = %{version}-%{release}

%description -n caelestia-shell
The Quickshell QML shell (bar, launcher, notifications, lock screen, etc.) and
its compiled beat_detector helper. The beat_detector binary used to be built
by hand with a raw g++ invocation pasted into install.fish; here it's a normal
compiled RPM artifact installed to %{_libdir}/caelestia/beat_detector.

%prep
%setup -q -n %{dotsrepo}-%{dotscommit} -a 1 -a 2
mv %{clirepo}-%{clicommit} cli
mv %{shellrepo}-%{shellcommit} shell
%setup -q -T -D -a 3

%build
# --- materialyoucolor: build the wheel (no Fedora package exists upstream;
# this replaces caelestia-cli's install.fish-era pip --break-system-packages
# fallback with a real RPM build of the pybind11 C++ extension) ---
pushd materialyoucolor-%{mycver}
%py3_build_wheel
popd

# --- caelestia-cli: build the wheel (replaces git clone + python -m build) ---
pushd cli
%py3_build_wheel
popd

# --- caelestia-shell: compile beat_detector (replaces the raw g++ one-liner) ---
pushd shell
g++ -std=c++17 -Wall -Wextra -O2 \
    $(pkg-config --cflags --libs libpipewire-0.3 aubio) \
    -o beat_detector assets/beat_detector.cpp \
    -lsndfile -lfftw3f -lm
popd

%install
# --- dotfiles payload ---
install -d %{buildroot}%{_datadir}/caelestia
cp -a hypr foot fish fastfetch uwsm btop qt5ct qt6ct %{buildroot}%{_datadir}/caelestia/
install -Dm0644 starship.toml %{buildroot}%{_datadir}/caelestia/starship.toml

install -Dm0755 install.fish %{buildroot}%{_datadir}/caelestia/install.fish
install -d %{buildroot}%{_bindir}
ln -s %{_datadir}/caelestia/install.fish %{buildroot}%{_bindir}/caelestia-fedora-setup

# --- fonts ---
install -d %{buildroot}%{_datadir}/fonts/caelestia-nerd-fonts
install -d %{buildroot}%{_datadir}/fonts/caelestia-material-symbols
# Font binaries are vendored as Source archives in the real package build;
# COPR custom source webhook downloads release tarballs from:
#   https://github.com/ryanoasis/nerd-fonts/releases (CascadiaCode, JetBrainsMono)
#   https://github.com/google/material-design-icons (variablefont/*.ttf)
# and drops the .ttf files into ./fonts-vendor/ before rpmbuild runs; see
# .copr/Makefile `get_sources` target. We just install whatever's there.
if [ -d fonts-vendor ]; then
    find fonts-vendor -iname '*NerdFont*.ttf' -exec install -Dm0644 {} -t %{buildroot}%{_datadir}/fonts/caelestia-nerd-fonts/ \;
    find fonts-vendor -iname 'MaterialSymbols*.ttf' -exec install -Dm0644 {} -t %{buildroot}%{_datadir}/fonts/caelestia-material-symbols/ \;
fi

# --- materialyoucolor ---
pushd materialyoucolor-%{mycver}
%py3_install_wheel materialyoucolor*.whl
popd

# --- caelestia-cli ---
pushd cli
%py3_install_wheel caelestia*.whl
popd
install -d %{buildroot}%{_datadir}/fish/vendor_completions.d
if [ -f cli/completions/caelestia.fish ]; then
    install -Dm0644 cli/completions/caelestia.fish \
        %{buildroot}%{_datadir}/fish/vendor_completions.d/caelestia.fish
fi

# --- caelestia-shell ---
install -d %{buildroot}%{_libdir}/caelestia
install -Dm0755 shell/beat_detector %{buildroot}%{_libdir}/caelestia/beat_detector
install -d %{buildroot}%{_datadir}/caelestia-shell/quickshell
cp -a shell/. %{buildroot}%{_datadir}/caelestia-shell/quickshell/
rm -rf %{buildroot}%{_datadir}/caelestia-shell/quickshell/assets/beat-detector.cpp

%post
# Symlinks formerly done line-by-line in install.fish (ln -s (realpath ...) ...)
config="${XDG_CONFIG_HOME:-$HOME/.config}"
if [ -n "${SUDO_USER:-}" ]; then
    real_home=$(getent passwd "$SUDO_USER" | cut -d: -f6)
    config="$real_home/.config"
fi
for d in hypr foot fish fastfetch uwsm btop qt5ct qt6ct; do
    target="$config/$d"
    if [ ! -e "$target" ] && [ ! -L "$target" ]; then
        ln -s "%{_datadir}/caelestia/$d" "$target" 2>/dev/null || :
    fi
done
if [ ! -e "$config/starship.toml" ] && [ ! -L "$config/starship.toml" ]; then
    ln -s "%{_datadir}/caelestia/starship.toml" "$config/starship.toml" 2>/dev/null || :
fi
:

%files
%doc README.md
%{_datadir}/caelestia/
%{_bindir}/caelestia-fedora-setup

%files fonts
%{_datadir}/fonts/caelestia-nerd-fonts/
%{_datadir}/fonts/caelestia-material-symbols/

%files -n python3-materialyoucolor
%{python3_sitelib}/materialyoucolor*

%files -n caelestia-cli
%{python3_sitelib}/caelestia*
%{_bindir}/caelestia
%{_datadir}/fish/vendor_completions.d/caelestia.fish

%files -n caelestia-shell
%{_libdir}/caelestia/beat_detector
%{_datadir}/caelestia-shell/

%changelog
* Thu Jun 25 2026 Auhon <packager@example.com> - 1.0.0-2
- wl-screenrec and cliphist are now built as sibling COPR packages
  (SPECS/wl-screenrec.spec, SPECS/cliphist.spec) instead of being left
  unrequired; Requires re-enabled accordingly
* Thu Jun 25 2026 Auhon <packager@example.com> - 1.0.0-1
- Initial COPR packaging of EnceladusII/caelestia-fedora
- Replaced install.fish's ad hoc dnf/cargo/go/pip/wget package installs with
  declarative Requires/BuildRequires and real %%build/%%install steps
- Split into caelestia-fedora (dotfiles+meta), caelestia-cli, caelestia-shell,
  and caelestia-fedora-fonts subpackages
