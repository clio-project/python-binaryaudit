# Contributing to binaryaudit Python module

`python-binaryaudit` is an open source project licensed under the [MIT](https://opensource.org/licenses/MIT) license.

## Coding Style

We follow the [Python Style](https://www.python.org/dev/peps/pep-0008/)
convention and enforce it through the Continuous Integration (CI) process calling into `flake8`
for each submitted Pull Request (PR).

## Certificate of Origin

In order to get a clear contribution chain of trust we use the [signed-off-by language](https://01.org/community/signed-process)
used by the Linux kernel project.

## Patch format

Beside the signed-off-by footer, we expect each patch to comply with the following format:

```
<component>: Change summary

More detailed explanation of your changes: Why and how.
Wrap it to 72 characters.
See http://chris.beams.io/posts/git-commit/
for some more good pieces of advice.

Signed-off-by: <contributor@foo.com>
```

For example:

```
vm-virtio: Reset underlying device on driver request
    
If the driver triggers a reset by writing zero into the status register
then reset the underlying device if supported. A device reset also
requires resetting various aspects of the queue.
    
In order to be able to do a subsequent reactivate it is required to
reclaim certain resources (interrupt and queue EventFDs.) If a device
reset is requested by the driver but the underlying device does not
support it then generate an error as the driver would not be able to
configure it anyway.
    
Signed-off-by: Max Mustermann <max@mustermann.com>
```

## Pull requests

`python-binaryaudit` uses the “fork-and-pull” development model. Follow these steps if
you want to merge your changes to `python-binaryaudit`:

1. Fork the [python-binaryaudit](https://github.com/clio-project/python-binaryaudit) project
   into your github organization.
2. Within your fork, create a branch for your contribution.
3. [Create a pull request](https://help.github.com/articles/creating-a-pull-request-from-a-fork/)
   against the `main` branch of the `python-binaryaudit` repository.
4. Add reviewers to your pull request and then work with your reviewers to address
   any comments and obtain minimum of 2 [maintainers](MAINTAINERS.md) approvals.
   To update your pull request amend existing commits whenever applicable and
   then push the new changes to your pull request branch.
5. Once the pull request is approved, one of the maintainers will merge it.

## Issue tracking

If you have a problem, please let us know. We recommend using
[github issues](https://github.com/clio-project/python-binaryaudit/issues/new) for formally
reporting and documenting them.

## Closing issues

You can either close issues manually by adding the fixing commit SHA1 to the issue
comments or by adding the `Fixes` keyword to your commit message:

```
Header line: explain the commit in one line (use the imperative)

Body of commit message is a few lines of text, explaining things
in more detail, possibly giving some background about the issue
being fixed, etc etc.

The body of the commit message can be several paragraphs, and
please do proper word-wrap and keep columns shorter than about
74 characters or so. That way "git log" will show things
nicely even when it's indented.

Make sure you explain your solution and why you're doing what you're
doing, as opposed to describing what you're doing. Reviewers and your
future self can read the patch, but might not understand why a
particular solution was implemented.

Resolves: #123
See also: #456, #789

Signed-off-by: Max Mustermann <max@mustermann.com>
```

Then, after the corresponding PR is merged, Github will automatically close that issue when parsing the
[commit message](https://help.github.com/articles/closing-issues-via-commit-messages/).
