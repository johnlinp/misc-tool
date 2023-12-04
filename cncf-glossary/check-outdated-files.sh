#!/usr/bin/env bash

if [ "x$#" != "x1" ] && [ "x$#" != "x2" ]
then
    echo "usage: $0 <language-code> [en-target-commit-hash]"
    echo
    echo "example:"
    echo "  $0 zh-tw"
    echo "  $0 zh-tw 2337701"
    echo
    echo "notes:"
    echo "  - please execute this script on your localization dev branch (e.g. dev-tw)"
    echo "  - please execute this script from the root directory of glossary git project"
    echo "  - the argument [en-target-commit-hash] is optional; it's the git commit hash for the commit on main branch if your change is based on this commit"
    exit 1
fi

set -e

LANGUAGE_CODE="$1"
EN_TARGET_COMMIT_HASH="$2"

if [ "x$EN_TARGET_COMMIT_HASH" != "x" ]
then
    EN_TARGET_COMMIT_AUTHOR_DATE=$(git log -n 1 --format=%ad "$EN_TARGET_COMMIT_HASH")
fi

for LOCALIZED_FILE_PATH in $(find content/"$LANGUAGE_CODE" -type f)
do
    LOCALIZED_FILE_LAST_COMMIT_AUTHOR_DATE=$(git log -n 1 --format=%ad "$LOCALIZED_FILE_PATH")
    EN_FILE_PATH=${LOCALIZED_FILE_PATH/"$LANGUAGE_CODE"/en}

    echo "checking $LOCALIZED_FILE_PATH (latest commit author date: $LOCALIZED_FILE_LAST_COMMIT_AUTHOR_DATE)"
    if [ "x$EN_TARGET_COMMIT_HASH" == "x" ]
    then
        git log --format=oneline --since="$LOCALIZED_FILE_LAST_COMMIT_AUTHOR_DATE" main "$EN_FILE_PATH"
    else
        git log --format=oneline --since="$LOCALIZED_FILE_LAST_COMMIT_AUTHOR_DATE" --until="$EN_TARGET_COMMIT_AUTHOR_DATE" main "$EN_FILE_PATH"
    fi
done
echo "check done"
