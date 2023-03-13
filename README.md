# codeforlife-workspace

This repo collects all of CFL's repos. Furthermore, this repo supports the cloning of all CFL repos using a single command. This is achieved using [Git Submodules](https://git-scm.com/book/en/v2/Git-Tools-Submodules), which is [supported by GitHub](https://github.blog/2016-02-01-working-with-submodules/).

## Setup Workspace

To setup your workspace, you'll need to recursively clone all repos in CFL's workspace:

```bash
git clone --recurse-submodules https://github.com/ocadotechnology/codeforlife-workspace.git
```

Next, open CFL's workspace in VSCode: `VSCode > File > Open Workspace from File... > path/to/codeforlife-workspace/codeforlife.code-workspace`.

## Update Workspace

### Add Submodule

To add a new submodule to CFL's workspace:

1. Clone the workspace and `cd` into it.
1. Add the submodule to the workspace:

    ```bash
    git submodule add {CFL_REPO_URL_HERE}
    ```

1. Add the new folder to CFL's [code-workspace](codeforlife.code-workspace).
1. Git commit and push the changes.

### Remove Submodule

To remove an existing submodule from CFL's workspace:

1. Clone the workspace and `cd` into it.
1. De-initialize the submodule:

    ```bash
    git submodule deinit -f {SUBMODULE_NAME_HERE}
    ```

1. Remove the submodule from git's list of submodules.

    ```bash
    rm .git/modules/{SUBMODULE_NAME_HERE} -r -fo && git rm -f {SUBMODULE_NAME_HERE} 
    ```

1. Git commit and push the changes.

### Edit Submodule

If you have renamed a submodule, it's recommended to remove and add it again.
