mdbook-build:
  rm -rf book theme/*
  mdbook build
  if [ -f .git2rss -a -x git2rss ] ; then ./git2rss > book/commits.xml ; fi

mdbook-serve:
  rm -rf book theme/*
  mdbook serve --open --hostname 127.0.0.1

mdbook-serve-all:
  rm -rf book theme/*
  mdbook serve --open --hostname 0.0.0.0

###############################################################################
#
# Change the 'push' target to reference the specific target(s) you want the
# site to be published to. Examples:
#
#   push: mdbook-rsync
#   push: mdbook-gh-pages

mdbook-push: mdbook-gh-pages

########################################
# IF you're going to publish the generated book to a web server, and you're
# able to use 'rsync' to upload the files ...
#
# - Change the 'push:' line to include the 'rsync' target
# - Edit the rsync command below as needed.
# - For Keybase Sites, the target will be a path under '/keybase/'. Seee
#   https://jms1.keybase.pub/kbsites/ for more specific examples.

mdbook-rsync: mdbook-build
  rsync -avz --delete book/ host.domain.xyz:/var/www/html/newbook/

########################################
# IF you're going to publish the generated book to GitHub Pages, using the
# same repo where you're tracking the source ...
#
# - Change the 'push:' line above to include the 'gh-pages' target
#
# NOTES:
# - These commands work for me using bash. If you're using some other shell,
#   you may need to adjust or remove this line.
# - The 'git worktree' commands require git version 2.0.7 or later.

mdbook-gh-pages: mdbook-build
  set -ex ; \
  WORK="$$( mktemp -d )" ; \
  VER="$$( git describe --always --tags --dirty )" ; \
  trap 'git worktree remove --force "$WORK" 2>/dev/null || true' EXIT ; \
  git worktree prune ; \
  if git worktree list --porcelain | grep -Eq "^branch (refs/heads/gh-pages|refs/remotes/origin/gh-pages)$$" ; then \
    echo "gh-pages already checked out in a worktree; aborting." ; \
    git worktree list ; \
    exit 1 ; \
  fi ; \
  git fetch origin gh-pages ; \
  git worktree add --force "$$WORK" origin/gh-pages ; \
  rm -rf "$$WORK"/* ; \
  rsync -av book/ "$$WORK"/ ; \
  if [ -f CNAME ] ; then cp CNAME "$$WORK"/ ; fi ; \
  pushd "$$WORK" ; \
  git add -A ; \
  if git diff --cached --quiet ; then echo "No changes to commit" ; else git commit -m "Updated gh-pages $$VER" ; fi ; \
  git push origin HEAD:gh-pages ; \
  popd
