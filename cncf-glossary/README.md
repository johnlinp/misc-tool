# Tools for CNCF Glossary

## check-outdated-files.sh

When we're modifying files on our localization branch, we want to make sure that the files we're modifying are up-to-date with their English counterparts.
This tool is to check if all the files on your localization branch are up-to-date.

### Usage

1. First, you have to `git checkout` to your localization branch, e.g. `dev-tw`.
1. Then please `cd` to the root directory of the `glossary` project.
1. Run the script with an argument of your language code, e.g. `zh-tw`:
```
$ /PATH/TO/check-outdated-files.sh zh-tw
```

#### Optional: Advanced Usage

If you're updateing files based on a specific commit on `main` branch, please supply the hash of that commit as an additional parameter:
```
$ /PATH/TO/check-outdated-files.sh zh-tw 2337701
```
