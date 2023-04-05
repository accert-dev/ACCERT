#!/bin/bash -evx

SOURCE=`dirname $0`/../
MD_TARGET=ACCERT_README.md

#
# create complete document
#
# 0. Start with GitLab-flavored style
cat $SOURCE/scripts/gitlab_style.txt > $MD_TARGET

# 1. Add root readme
cat $SOURCE/../README.md >> $MD_TARGET

# 6. Add auto generated schema readme
$SOURCE/../bin/docprint $SOURCE/etc/accert.sch >> $MD_TARGET

# 7. Convert inter-readme-anchor links to intra
#   i.e.,  [schema](etc/README.md#schema) -> [schema](#schema)
sed -i '' 's@\](/[^\#]*\#@\](\#@g' $MD_TARGET

# 8. Convert document links to be README-relative
sed -i '' 's@\](/@\](./@g' $MD_TARGET


# Convert complete Markdown readme to HTML
pandoc $MD_TARGET -t html -o ../ACCERT_README.html
