#!/usr/bin/env bash
# The sources the editions are built from, at the commits the data in this repo was built from, into $1 (default
# src/ beside the offline-data checkout). Used by the daily alignment session (ALIGNMENT-ROUTINE.md), which starts in
# an empty container. Sources already there are left as they are. About 2.5 GB, a few minutes.
# To move to newer sources, change the commits here and rebuild everything (README, Run / sync).
set -euo pipefail
REPO=$(cd "$(dirname "$0")/../../.." && pwd)
SRC=${1:-$(dirname "$REPO")/src}
mkdir -p "$SRC" && cd "$SRC"

fetch() {  # fetch DIR URL SHA PATH...: that commit only, only those paths
  local dir=$1 url=$2 sha=$3; shift 3
  if [ -d "$dir/.git" ]; then echo "have $dir $(git -C "$dir" log -1 --format=%h)"; return; fi
  mkdir -p "$dir" && git -C "$dir" init -q && git -C "$dir" remote add origin "$url"
  git -C "$dir" sparse-checkout set "$@"
  for i in 1 2 3 4 5; do
    git -C "$dir" fetch -q --depth 1 --filter=blob:none origin "$sha" && break
    [ "$i" = 5 ] && exit 1; sleep $((2 ** i))
  done
  git -C "$dir" checkout -q FETCH_HEAD
  echo "fetched $dir $(git -C "$dir" log -1 --format=%h)"
}

fetch tipitaka.lk https://github.com/pathnirvana/tipitaka.lk 58eed98e6dc2df2bc01801f075c885a17679faa8 public/static/text
fetch tipitaka-xml https://github.com/VipassanaTech/tipitaka-xml 00a2b2b05cd64e6bec0eb0674f5cbefaa119dbd3 romn
fetch bilara-data https://github.com/suttacentral/bilara-data 6a395ceb6f28549111d7d96859f7f6f6610afc01 \
  root/pli/ms reference/pli/ms variant/pli/ms
fetch raw/t2500 https://github.com/tipitaka2500/tipitaka2500.github.io 5cc3e9aabdadea79557f7d7d9e47e553231d982e tipitaka

if [ ! -s palinew.sqlite ]; then  # E-Tipitaka, Siam Rath (Git LFS); sha256 62e0b31282b87c2a…
  curl -sSfL -o palinew.sqlite https://media.githubusercontent.com/media/ssutee/e-tipitaka-pc/master/resources/palinew.sqlite
fi
sha256sum palinew.sqlite | grep -q '^62e0b31282b87c2a' || echo "WARNING: palinew.sqlite is not the one the data was built from"

if [ ! -d gretil/x/2_pali ]; then  # GRETIL 2_pali (PTS), kept in this repo's gretil-pali branch
  mkdir -p gretil/x
  git -C "$REPO" fetch -q origin gretil-pali
  git -C "$REPO" show origin/gretil-pali:gretil/2_pali.zip > gretil/2_pali.zip
  (cd gretil/x && unzip -q ../2_pali.zip)
fi

if [ ! -s raw/mbu-pm/030109.csv ]; then  # the Thai Pātimokkha (Mahāmakuṭa), uisp on Hugging Face
  mkdir -p raw/mbu-pm
  for p in $(seq 1 113); do
    f=$(printf '03%04d.csv' "$p")
    curl -sSfL --retry 4 -o "raw/mbu-pm/$f" \
      "https://huggingface.co/datasets/uisp/dhamma-book-for-general-public/resolve/main/03/$f"
  done
fi
echo "sources in $SRC:"; du -sh "$SRC"/* 2>/dev/null
