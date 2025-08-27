#!/usr/bin/env bash
#
# setup-gh-pages
# Phillip Bonhomme <phillip.bonhomme.jr@pm.me> 2025-08-26
#
# Add a 'gh-pages' branch to the repo
#

set -e

########################################
# Make sure git is version 2.0.7 or higher

REQD="2.0.7"
GITV="$( git --version | sed 's/[^0-9\.]//g' )"
XMIN="$( echo -e "$GITV\n$REQD" | sort -V | head -1 )"

if [[ "$XMIN" != "$REQD" ]]
then
    echo "ERROR: this requires git version $REQD, you have $GITV"
    exit 1
fi

########################################
# Make sure we don't already have a 'gh-pages' branch

if [[ -n "$( git branch -a | grep gh-pages )" ]]
then
    echo "ERROR: this repo already appears to have a 'gh-pages' branch"
    exit 1
fi

########################################
# Remember what directory the primary branch is checked out in, so we can
# check and possibly copy the book/ directory.

MAIN="$( pwd )"

########################################
# Create a work directory

WORK="$( mktemp -d )"

########################################
# Add a new working directory for the repo
# - the 'git worktree' commands were added in git v2.0.7

git worktree add --detach "$WORK"

########################################
# In the new working directory, start a new 'gh-pages' branch.

pushd "$WORK"
git checkout --orphan gh-pages
git rm -rf * .gitignore

########################################
# Populate the new directory.
# - If 'mdbook' has already generated the book at least once, copy that.
# - If not, create a simple "Coming soon..." page.

if [[ -f "$MAIN/book/index.html" ]]
then
    FULL=true
    cp -rv "$MAIN/book/" ./
else
    FULL=false
    touch .nojekyll
    cat > index.html <<EOF
<html>
<head>
<title>Coming soon...</title>
</head>
<body>
<h1>Coming soon...</h1>
<p>This is a placeholder page, so you can tell that GitHub Pages is working.
This will be replaced with the actual book once you run "<tt>make push</tt>"
for the first time.</p>
</body>
</html>
EOF
fi

########################################
# Commit the new files.

git add .
git commit -m 'Started gh-pages branch'
git tag -m 'Initial commit on gh-pages branch' gh-pages-initial

########################################
# Done, remove the temp directory.

popd
git worktree remove "$WORK"

########################################
# Tell the user what's going on

if $FULL
then
    cat <<EOF

The 'gh-pages' branch now exists on this machine, containing a copy of the
book's most recently rendered content.

EOF
else
    cat <<EOF

The 'gh-pages' branch now exists on this machine, containing a simple
"Coming soon" page.

EOF
fi
