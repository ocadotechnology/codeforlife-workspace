# codeforlife-workspace

This repo collects all of CFL's repos. Furthermore, this repo supports the cloning of all CFL repos using a single command. This is achieved using [Git Submodules](https://git-scm.com/book/en/v2/Git-Tools-Submodules), which is [supported by GitHub](https://github.blog/2016-02-01-working-with-submodules/).

## LICENCE
In accordance with the [Terms of Use](https://www.codeforlife.education/terms#terms)
of the Code for Life website, all copyright, trademarks, and other 
intellectual property rights in and relating to Code for Life (including all 
content of the Code for Life website, the Rapid Router application, the 
Kurono application, related software (including any drawn and/or animated 
avatars, whether or not such avatars have any modifications) and any other 
games, applications or any other content that we make available from time to 
time) are owned by Ocado Innovation Limited.

The source code of the Code for Life portal, the Rapid Router application 
and the Kurono/aimmo application are [licensed under the GNU Affero General 
Public License](https://github.com/ocadotechnology/codeforlife-workspace/blob/main/LICENSE.md).
All other assets including images, logos, sounds etc., are not covered by 
this licence and no-one may copy, modify, distribute, show in public or 
create any derivative work from these assets.

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

### Update Submodules

To sync your local submodules with the submodules in CFL's remote workspace:

```bash
git submodule update --remote
```

(***NOTE**: this will clone new submodules added by someone else*)

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
