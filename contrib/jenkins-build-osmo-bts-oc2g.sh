#!/bin/sh
set -e -x

_poky_version="$POKY_VERSION"
_poky_path="$POKY_PATH"

[ -z "$_poky_version" ] && _poky_version="2.3.2"
[ -z "$_poky_path" ] && _poky_path="/opt/poky/$_poky_version"

. "$_poky_path/environment-setup-armv5te-poky-linux-gnueabi"

# Cross-compilation: all installations need to be put in the sysmo SDK sysroot
export DESTDIR="$_poky_path/sysroots/armv5te-poky-linux-gnueabi"

base="$PWD"
name="osmo-bts-oc2g"
prefix="/usr/local/jenkins-build/inst-$name"
prefix_real="$DESTDIR$prefix"
. "$(dirname "$0")/jenkins-build-common.sh"

prev_git_url="${git_url}"
git_url="https://gitlab.com/nrw_oc2g/"
have_repo "oc2g-fw" "nrw/oc2g"
git_url="${prev_git_url}"
L1_OC2G_HEADERS="$PWD/oc2g-fw/inc"

build_repo libosmocore --disable-pcsc --disable-doxygen --disable-gnutls
build_repo libosmo-abis
build_repo osmo-bts --disable-sysmocom-bts --enable-oc2g --with-oc2g="$L1_OC2G_HEADERS"

create_bin_tgz osmo-bts-oc2g
