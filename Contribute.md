# How to Contribute

Thank you for considering contributing to this project!
This guide outlines how we work, how to propose changes, and the expectations for contributions.

> **TL;DR**
>
> * **Never push directly to `develop`.**
> * **Every change happens on a dedicated branch:** `feature_...`, `bug_...`, etc.
> * Open a Pull Request (PR) → pass tests → review → merge.

---

## 1. Ground Rules

By contributing, you agree to:

* Respect review decisions and collaborate constructively.
* Not commit:

  * Secrets, passwords, tokens, or private keys.
  * Proprietary or personal data.
  * Large binary/data files unless explicitly approved (and preferably via Git LFS or external storage).

---

## 2. Branching & Protection Rules (Important)

### No Direct Pushes to `develop`

* `develop` is a **protected integration branch**.
* **Do not push directly to `develop`** under any circumstances.
* All changes must:

  1. Be developed on a dedicated branch.
  2. Go through a Pull Request.
  3. Pass tests.
  4. Be approved by at least one maintainer (or per project policy).

### Branch Naming Convention

Create one branch per logical change. The prefixes must be in accordance to the labels of the issue which is adressed by your contribution. E.g:

* New features:
  `feature_<short-description>`
  e.g. `feature_user_auth`, `feature_new_dashboard`

* Bug fixes:
  `bug_<short-description>`
  e.g. `bug_fix_login_redirect`, `bug_resolve_null_pointer`

....

**Recommendations**

* Include ticket/issue IDs:
  `feature_1234_user_auth`, `bug_5678_fix_validation`
* Use lowercase and `_` as separator for consistency.

---

## 3. Contribution Workflow

1. **Find or create an issue**

   * For new ideas, open an issue before starting heavy work to align with maintainers.

2. **Fork & Clone (if external contributor)**

   ```bash
   git clone <repo-url>
   cd <repo>
   ```

3. **Create a branch**

   ```bash
   git checkout -b feature_short-description
   # or
   git checkout -b bug_short-description
   ```

4. **Set up your environment**

   * Install prerequisites (see `README.md` / `docs/`).
   * Run initial setup scripts if provided.
   * Ensure tests run locally.

5. **Implement your changes**

   * Keep changes focused and self-contained.
   * Add or update tests.
   * Update documentation / examples where relevant.

6. **Run checks locally**

   All tests within the test folder must run through.
   All tests must pass before you open a PR.
   If you think something is missing, please add additional tests (via creating a branch ... 😉)

8. **Commit with a clear message**

   Use clear, conventional-style messages, for example:

   * `feat: add user auth flow`
   * `fix: handle null user id`
   * `docs: update installation guide`
   * `chore: update CI pipeline`

   Keep commits small, meaningful, and logically grouped.

9. **Push your branch**

   ```bash
   git push origin feature_short-description
   ```

10. **Open a Pull Request**

   In your PR:

   * Use a descriptive title.
   * Link related issues: `Closes #123`.
   * Briefly describe **what** and **why**, not just **how**.
   * List breaking changes (if any).
   * Confirm:

     * [x] Tests pass locally
     * [x] No direct commits to `develop`
     * [x] No secrets or sensitive data included

---

## 4. Code Review Guidelines

Maintainers and reviewers will check for:

* Correctness and alignment with project architecture.
* Tests
* Style:

  * Follows the project’s formatting & linting rules.
  * Uses existing patterns & abstractions; no unnecessary duplication.
* Security & privacy considerations.
* Documentation updates where needed.

**As an author:**

* Be responsive to review comments.
* Prefer amending your branch (via additional commits or a clean rebase) instead of opening new PRs for the same change.
* Avoid force-pushing over commits that reviewers have already commented on unless necessary and clearly communicated.

---

## 5. Reporting Bugs & Requesting Features

When opening issues:

* Use the provided templates if available.
* For bugs, include:

  * Steps to reproduce
  * Expected vs actual behavior
  * Environment (OS, runtime, versions)
  * Logs or stack traces (with secrets redacted)
* For features, include:

  * Problem statement
  * Proposed solution or API
  * Alternatives considered
  * Potential impact

Quality issues and feature requests are contributions too ❤️

---

## 6. License & Ownership

By submitting a contribution:

* You confirm you have the right to license the work.
* Your contribution will be licensed under the repository’s declared license (see `LICENSE`).

---

## 7. Need Help?

If anything is unclear:

* Check `README.md` and `docs/`.
* Browse existing issues and discussions.
* If still stuck, open a discussion or a clarification issue with a concise description.
* Contact the maintainers of the repo

We’re happy you’re here. Now go make a branch (not on `develop` 😉) and build something great.
