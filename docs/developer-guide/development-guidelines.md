---
description: Development guides and tips.
---

# Development Guidelines

## Working on an issue

When you see an issue that you'd like to work on, **please comment in the thread**. By commenting, you indicate your interest and we will be able to assign the issue to you. That way the issue is 'earmarked', and we avoid the situation where more than one person is working on the same issue.

You can start working on it on your [forked repository](https://docs.github.com/en/github/getting-started-with-github/fork-a-repo), and submit a pull request when done (see the detail below on _opening a pull request_).&#x20;

{% hint style="info" %}
The core developers will not be working on issues marked as **good first issue** and **volunteers**. They are reserved for volunteers only.
{% endhint %}

## Editor and Formatter

You can use whichever editor you like. Primarily for Python, we'd recommend Visual Code with [black formatter](https://black.readthedocs.io) plugin ([this is how to enable it on VSCode](https://dev.to/adamlombard/how-to-use-the-black-python-code-formatter-in-vscode-3lo0)). That way you don't have to worry about formatting and convention, and let **black** do the work. PyCharm community edition is free of charge as well. One of our developers uses IntelliJ, but you may need a license.

For HTML/CSS/Javascript, there's no auto-formatter that we know of (be careful about editor that auto-formats as it may break the code). Best way is to follow the existing style and convention.&#x20;

## Opening a pull request

You should usually open a pull request in the following situations:

* Submit trivial fixes (for example, a typo, a broken link or an obvious error)
* Start work on a contribution that was already asked for, or that you’ve already discussed, in an issue

A pull request doesn’t have to represent finished work. It’s usually better to open a pull request early on, so others can watch or give feedback on your progress. Just mark it as a “WIP” (Work in Progress) in the subject line or create a [draft PR](https://github.blog/2019-02-14-introducing-draft-pull-requests/). You can always add more commits later.

**We encourage people to open a PR early to indicate that you are working on an issue**.&#x20;

How to submit a pull request:

* [**Fork the repository**](https://guides.github.com/activities/forking/) and clone it locally. Connect your local to the original “upstream” repository by adding it as a remote. Pull in changes from “upstream” often so that you stay up to date so that when you submit your pull request, merge conflicts will be less likely. (See more detailed instructions [here](https://help.github.com/articles/syncing-a-fork/).)
* [**Create a branch**](https://guides.github.com/introduction/flow/) for your edits.

If this is your first pull request, check out [Make a Pull Request](http://makeapullrequest.com/). You can also check out [First Contributions](https://github.com/Roshanjossey/first-contributions) repository, on which you can practice the whole workflow - a fork, a clone, creating a branch, and making a pull request.

{% hint style="info" %}
It would be helpful for you to include the issue number in the PR description, so we can connect the issue to the PR.
{% endhint %}

###
