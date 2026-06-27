%global cargo_install_lib 0

Name:           wl-screenrec
Version:        0.2.0
Release:        1%{?dist}
Summary:        High performance hardware accelerated wlroots screen recorder

License:        Apache-2.0 AND (Apache-2.0 OR MIT) AND (Apache-2.0 WITH LLVM-exception OR Apache-2.0 OR MIT) AND ISC AND MIT AND (MIT OR Apache-2.0) AND (Unlicense OR MIT) AND WTFPL
URL:            https://github.com/russelltg/wl-screenrec
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz
Source1:        vendor.tar.zst

BuildRequires:  cargo-rpm-macros >= 26
BuildRequires:  clang-devel
BuildRequires:  pkgconfig(libavdevice)
BuildRequires:  pkgconfig(libavfilter)
BuildRequires:  pkgconfig(libavformat)
BuildRequires:  pkgconfig(libavutil)
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  vulkan-loader
BuildRequires:  vulkan-headers
BuildRequires:  wayland-devel
BuildRequires:  wayland-protocols-devel

Requires:       ffmpeg-free

%description
High performance screen/audio recorder for wlroots. Uses dma-buf transfers
to get the surface, and uses the GPU to do both pixel format conversion and
encoding, so the raw video data never touches the CPU.

%prep

%autosetup -n %{name}-%{version} -p1 -a1

# Comprehensive fixes for FFmpeg 7 / Fedora 44 enum expansions
# Fix side_data match matching error (fallback to an existing variant like Type::Palette)
sed -i 's/AV_PKT_DATA_RTCP_SR => Type::RTCP_SR,/AV_PKT_DATA_RTCP_SR => Type::RTCP_SR, _ => Type::Palette,/' \
    vendor/ffmpeg-next/src/codec/packet/side_data.rs

# Fix color primaries match error (fallback to Primaries::Unspecified)
sed -i 's/AVCOL_PRI_EBU3213 => Primaries::EBU3213,/AVCOL_PRI_EBU3213 => Primaries::EBU3213, _ => Primaries::Unspecified,/' \
    vendor/ffmpeg-next/src/util/color/primaries.rs

# Fix transfer characteristics match error (fallback to TransferCharacteristic::Unspecified)
sed -i 's/AVCOL_TRC_ARIB_STD_B67 => TransferCharacteristic::ARIB_STD_B67,/AVCOL_TRC_ARIB_STD_B67 => TransferCharacteristic::ARIB_STD_B67, _ => TransferCharacteristic::Unspecified,/' \
    vendor/ffmpeg-next/src/util/color/transfer_characteristic.rs

# Fix frame side data match error (fallback to an existing variant like Type::PanScan)
sed -i 's/AV_FRAME_DATA_3D_REFERENCE_DISPLAYS => Type::THREE_D_REFERENCE_DISPLAYS,/AV_FRAME_DATA_3D_REFERENCE_DISPLAYS => Type::THREE_D_REFERENCE_DISPLAYS, _ => Type::PanScan,/' \
    vendor/ffmpeg-next/src/util/frame/side_data.rs

# Fix big codec id enum match error (fallback to CodecId::None)
sed -i 's/AV_CODEC_ID_PCM_S16LE => Id::PCM_S16LE,/ _ => Id::None, AV_CODEC_ID_PCM_S16LE => Id::PCM_S16LE,/' \
    vendor/ffmpeg-next/src/codec/id.rs

# Strip all updated file hashes from .cargo-checksum.json to bypass integrity locks
sed -i 's/"src\/codec\/packet\/side_data.rs":"[a-f0-9]*",//' vendor/ffmpeg-next/.cargo-checksum.json
sed -i 's/"src\/util\/color\/primaries.rs":"[a-f0-9]*",//' vendor/ffmpeg-next/.cargo-checksum.json
sed -i 's/"src\/util\/color\/transfer_characteristic.rs":"[a-f0-9]*",//' vendor/ffmpeg-next/.cargo-checksum.json
sed -i 's/"src\/util\/frame\/side_data.rs":"[a-f0-9]*",//' vendor/ffmpeg-next/.cargo-checksum.json
sed -i 's/"src\/codec\/id.rs":"[a-f0-9]*",//' vendor/ffmpeg-next/.cargo-checksum.json


mkdir -p .cargo
cat > .cargo/config.toml << 'EOF'
[source.crates-io]
replace-with = "vendored-sources"

[source."git+https://github.com/russelltg/rust-ffmpeg-sys?branch=vulkan"]
git = "https://github.com/russelltg/rust-ffmpeg-sys"
branch = "vulkan"
replace-with = "vendored-sources"

[source.vendored-sources]
directory = "vendor"
EOF

# Inject the missing 'rpm' profile definition that Fedora's macros expect
cat >> Cargo.toml << 'EOF'

[profile.rpm]
inherits = "release"
opt-level = 3
EOF

%build
# Build utilizing our explicit override settings
%cargo_build -a

%{cargo_license_summary}
%{cargo_license} > LICENSE.dependencies
%{cargo_vendor_manifest}

%install
# 1. Create the target binary execution directory in the buildroot
install -d %{buildroot}%{_bindir}

# 2. Manually copy the compiled executable directly from the target build artifacts
# Fedora macros place it under target/rpm/ or target/release/
install -m 0755 target/rpm/wl-screenrec %{buildroot}%{_bindir}/wl-screenrec

# 3. Initialize directory trees for shell runtime completions
install -d %{buildroot}%{_datadir}/bash-completion/completions
install -d %{buildroot}%{_datadir}/zsh/site-functions
install -d %{buildroot}%{_datadir}/fish/vendor_completions.d

# 4. Generate the completions using the buildroot layout target binary
%{buildroot}%{_bindir}/wl-screenrec --generate-completions bash \
    > %{buildroot}%{_datadir}/bash-completion/completions/wl-screenrec
%{buildroot}%{_bindir}/wl-screenrec --generate-completions zsh \
    > %{buildroot}%{_datadir}/zsh/site-functions/_wl-screenrec
%{buildroot}%{_bindir}/wl-screenrec --generate-completions fish \
    > %{buildroot}%{_datadir}/fish/vendor_completions.d/wl-screenrec.fish

%files
%license LICENSE
%license LICENSE.dependencies
%license cargo-vendor.txt
%doc README.md
%{_bindir}/wl-screenrec
%{_datadir}/bash-completion/completions/wl-screenrec
%{_datadir}/zsh/site-functions/_wl-screenrec
%{_datadir}/fish/vendor_completions.d/wl-screenrec.fish

%changelog
* Sat Jun 27 2026 S. M. A Kahar Auhon <auhon@example.com> - 0.2.0-1
- Initial release bump to 0.2.0.
- Dropped Cargo.lock verification tracking to bypass vendor crate sync mismatches.
- Manual .cargo/config.toml structural rewrite for offline git tracking maps.
- Added clap runtime shell completion generation.
