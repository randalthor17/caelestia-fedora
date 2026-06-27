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
Source3:        https://files.pythonhosted.org/packages/source/m/materialyoucolor/materialyoucolor-%{mycver}.tar.gz

# BuildArch:      noarch

Requires:       caelestia-cli = %{version}-%{release}
Requires:       caelestia-shell = %{version}-%{release}

# Core runtime deps
Requires:       (hyprland or hyprland-git)
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
Requires:       starship
Requires:       hyprpicker
Requires:       hypridle
Requires:       app2unit
Requires:       wl-screenrec
Requires:       cliphist
Requires:       %{name}-fonts = %{version}-%{release}

%description
Meta-package and dotfiles for the Caelestia Hyprland desktop, Fedora edition.
Run `caelestia-fedora-setup` after installation to safely deploy configurations
directly to your home configuration profile paths.

%package fonts
Summary:        Nerd Fonts + Material Symbols used by the Caelestia shell
BuildArch:      noarch

%description fonts
Cascadia Code Nerd Font, JetBrains Mono Nerd Font, and Google Material Symbols
packaged natively as system RPM fonts.

%package -n caelestia-cli
Summary:        Control script for the Caelestia dotfiles (Fedora build)
License:        GPL-3.0-only
URL:            %{forgeurl1}
BuildRequires:  python3-devel python3-build python3-installer hatch python3-hatch-vcs pyproject-rpm-macros
Requires:       python3-materialyoucolor = %{version}-%{release}
Requires:       fish libnotify swappy grim slurp wl-clipboard glib2 fuzzel

BuildArch:      noarch

%description -n caelestia-cli
The `caelestia` command-line control tool wrapper.

%package -n python3-materialyoucolor
Summary:        Material You color generation algorithms (pybind11/C++ backend)
License:        Apache-2.0
BuildRequires:  python3-devel python3-pip python3-setuptools python3-wheel pyproject-rpm-macros
BuildRequires:  python3-pybind11 pybind11-devel gcc-c++

%description -n python3-materialyoucolor
Pure-Python Material You color matching engine optimized via C++ extensions.

%package -n caelestia-shell
Summary:        Quickshell-based desktop shell for Caelestia (Fedora build)
License:        GPL-3.0-only
URL:            %{forgeurl2}
BuildRequires:  gcc-c++ pkgconfig(libpipewire-0.3) pkgconfig(aubio) pkgconfig(sndfile) pkgconfig(fftw3f)
Requires:       quickshell qt6-qtdeclarative libqalculate pipewire aubio
Requires:       caelestia-cli = %{version}-%{release}

%description -n caelestia-shell
The desktop shell user-interface core.

%prep
# Unpack Source0 and set custom directory context
%setup -q -n %{dotsrepo}-%{dotscommit}

# You must explicitly supply "-n %%{dotsrepo}-%%{dotscommit}" to every append setup block
%setup -q -T -D -a 1 -n %{dotsrepo}-%{dotscommit}
%setup -q -T -D -a 2 -n %{dotsrepo}-%{dotscommit}
%setup -q -T -D -a 3 -n %{dotsrepo}-%{dotscommit}

# Safely rename standard GitHub branch structures to clean aliases
mv %{clirepo}-%{clicommit} cli
mv %{shellrepo}-%{shellcommit} shell

%build
# Set the pretend version environment variable so hatch-vcs can build without a .git folder
export SETUPTOOLS_SCM_PRETEND_VERSION=%{version}

# Build materialyoucolor wheel
pushd materialyoucolor-%{mycver}
%pyproject_wheel
popd

# Build caelestia-cli wheel
pushd cli
%pyproject_wheel
popd

# Compile beat_detector
pushd shell
g++ -std=c++17 -Wall -Wextra -O2 \
    $(pkg-config --cflags --libs libpipewire-0.3 aubio) \
    -o beat_detector assets/cpp/beat-detector.cpp \
    -lsndfile -lfftw3f -lm
popd

%install
# Create core asset storage directory
install -d %{buildroot}%{_datadir}/caelestia
cp -a hypr foot fish fastfetch uwsm btop qt5ct qt6ct %{buildroot}%{_datadir}/caelestia/
install -Dm0644 starship.toml %{buildroot}%{_datadir}/caelestia/starship.toml

# ─── INJECT COPIED USER-SPACE SEED SETUP TOOL ───
cat << 'EOF' > %{buildroot}%{_datadir}/caelestia/install.fish
#!/usr/bin/env fish

argparse -n 'caelestia-fedora-setup' -X 0 \
    'h/help' \
    'noconfirm' \
    -- $argv
or exit

if set -q _flag_h
    echo 'usage: caelestia-fedora-setup [-h] [--noconfirm]'
    echo
    echo 'options:'
    echo '  -h, --help     show this help message and exit'
    echo '  --noconfirm    skip overwrite confirmations'
    exit
end

function _out -a colour text
    set_color $colour
    echo $argv[3..] -- ":: $text"
    set_color normal
end

function log -a text
    _out cyan $text $argv[2..]
end

function input -a text
    _out blue $text $argv[2..]
end

function confirm-overwrite -a path
    if test -e $path -o -L $path
        if set -q _flag_noconfirm
            rm -rf $path
        else
            read -l -p "input '$path already exists. Overwrite with defaults? [Y/n] ' -n" confirm || exit 1
            if test "$confirm" = 'n' -o "$confirm" = 'N'
                log 'Skipping...'
                return 1
            else
                rm -rf $path
            end
        end
    end
    return 0
end

set -q XDG_CONFIG_HOME && set -l config $XDG_CONFIG_HOME || set -l config $HOME/.config

log 'Welcome to the Caelestia user profile manager!'
log 'Seeding default configuration files into user target environment trees...'

set -l pkg_source_dir "/usr/share/caelestia"
mkdir -p $config

# Physically copy folders over so user space modifications work safely
for d in hypr foot fish fastfetch uwsm btop qt5ct qt6ct
    if confirm-overwrite $config/$d
        log "Copying default $d configurations..."
        cp -a $pkg_source_dir/$d $config/$d
    end
end

if confirm-overwrite $config/starship.toml
    log 'Copying default starship configuration...'
    cp -a $pkg_source_dir/starship.toml $config/starship.toml
end

log 'User environment profiles initialized successfully!'
log 'Done! Enjoy Caelestia on Fedora!'
EOF

# Ensure setup script layout permissions match executable flags
chmod 0755 %{buildroot}%{_datadir}/caelestia/install.fish

# Generate global launcher symlink shortcut execution point
install -d %{buildroot}%{_bindir}
ln -s ../share/caelestia/install.fish %{buildroot}%{_bindir}/caelestia-fedora-setup

# Font arrays integration execution
install -d %{buildroot}%{_datadir}/fonts/caelestia-nerd-fonts
install -d %{buildroot}%{_datadir}/fonts/caelestia-material-symbols
if [ -d fonts-vendor ]; then
    find fonts-vendor -iname '*NerdFont*.ttf' -exec install -Dm0644 {} -t %{buildroot}%{_datadir}/fonts/caelestia-nerd-fonts/ \;
    find fonts-vendor -iname 'MaterialSymbols*.ttf' -exec install -Dm0644 {} -t %{buildroot}%{_datadir}/fonts/caelestia-material-symbols/ \;
fi

# Wheel installations execution block
pushd materialyoucolor-%{mycver}
%pyproject_install
popd

pushd cli
%pyproject_install
popd

install -d %{buildroot}%{_datadir}/fish/vendor_completions.d
if [ -f cli/completions/caelestia.fish ]; then
    install -Dm0644 cli/completions/caelestia.fish \
        %{buildroot}%{_datadir}/fish/vendor_completions.d/caelestia.fish
fi

# Shell & Core Binaries delivery execution
install -d %{buildroot}%{_libdir}/caelestia
install -Dm0755 shell/beat_detector %{buildroot}%{_libdir}/caelestia/beat_detector
install -d %{buildroot}%{_datadir}/caelestia-shell/quickshell
cp -a shell/. %{buildroot}%{_datadir}/caelestia-shell/quickshell/
rm -rf %{buildroot}%{_datadir}/caelestia-shell/quickshell/assets/cpp/beat-detector.cpp

%files
%doc README.md
%{_datadir}/caelestia/
%{_bindir}/caelestia-fedora-setup

%files fonts
%{_datadir}/fonts/caelestia-nerd-fonts/
%{_datadir}/fonts/caelestia-material-symbols/

%files -n python3-materialyoucolor
%{python3_sitearch}/materialyoucolor*

%files -n caelestia-cli
%{python3_sitelib}/caelestia*
%{_bindir}/caelestia
%{_datadir}/fish/vendor_completions.d/caelestia.fish

%files -n caelestia-shell
%{_libdir}/caelestia/beat_detector
%{_datadir}/caelestia-shell/

%changelog
* Sat Jun 27 2026 Auhon <packager@example.com> - 1.0.0-2
- Patched line break on cp target inside %install section.
- Fixed setup macro expansion behaviors on main-branch GitHub extractions.
- Completely shifted install routines to Approach A copy-based system for safe local edits.
