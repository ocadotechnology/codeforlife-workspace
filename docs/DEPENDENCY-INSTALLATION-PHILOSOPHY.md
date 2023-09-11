# Dependency Installation Philosophy

This document aims to guide developers when they should or should not install a dependency into an environment.

## The PROs of installing a new dependency

We need to depend on the work of others as we can't do it all ourselves! We should depend on 3rd party packages that are:

- production-ready solutions to common problems (don't reinvent the wheel).
- solving problems that we couldn't easily solve ourselves.
- battle hardened, heavily tested packages.
- popular/credible packages from major contributors.
- actively maintained so critical issues are resolved in a timely manner.

## The CONs of installing a new dependency

However, there are dangers to becoming overly dependent on the work of others. Be wary of:

- increasing our environments' build time + size and, ultimately, our time-to-deploy.
- inefficiencies in their algorithms slowing down our app.
- security vulnerabilities that we'll be liable for if sensitive data is leaked.
- software licensing that prevents us from using code in the circumstances we need.
- dependency hell - the more dependencies, the harder it'll be to resolve and re-lock all dependencies when updating a single dependency.
- the added overhead of keeping track of each dependency's health/project status.
- obfuscating the code by constantly introducing something new.

## When to install a new dependency

There is no hard, industry-standard criteria on when to install a dependency. Rather it's up to us to define our criteria on when a package should be installed. Therefore, before you install a new dependency, assess each dependency on a case-by-case basis and ensure you meet the following criteria.

*The dependency I want to install in my pull request is:*

- [ ] necessary to support our functionality
- [ ] secure (if any sensitive data is passed to it)
- [ ] licensed for our needs
- [ ] of significant complexity that we couldn't easily implement it ourselves
- [ ] appropriately sized for the complexity of its intended use
- [ ] production-ready (high quality) code
- [ ] actively maintained
- [ ] originates from credible sources
