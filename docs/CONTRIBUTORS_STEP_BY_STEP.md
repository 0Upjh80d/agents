# Contributor's Step-by-Step Guide

1. **Start with the Latest Code**: Before you begin any work, **pull the latest changes** from the remote repository. If you're starting a new feature or fix, ensure your local `main` and `staging` branches are up-to-date with the team's repository. This reduces the chance of merge conflicts later. For example, run:

   ```bash
   git checkout staging
   git pull origin staging
   ```

> [!NOTE]
> Use `dev` instead of `staging` if our workflow includes a `dev` branch.

2. **Create a New Branch**: Create a dedicated branch for your work:

   - For a new feature, branch off `staging` (or `dev` if using that) and name it `feature/<your-feature-name>`. Choose a short, descriptive name for the feature. For example:

     ```bash
     git checkout -b feature/improved-booking-ui staging
     ```

     This creates and switches to `feature/improved-booking-ui` based on the latest `staging`.

   - For a bug fix (non-critical), branch off `staging` and name it `bugfix/<description-of-fix>` or include the issue number, e.g.:

     ```bash
     git checkout -b bugfix/fix-date-validation staging
     ```

   - For a critical production hotfix, branch off `main` (since you're fixing something currently in production) and name it `hotfix/<description-of-fix>`, e.g.:

     ```bash
     git checkout -b hotfix/fix-null-pointer main
     ```

> [!IMPORTANT]
> Use **descriptive branch names** so others can quickly understand the purpose. Our naming convention is all lowercase with words separated by hyphens or slashes as shown. Include a prefix (`feature/`, `bugfix/`, `hotfix/`) to indicate the branch type. Avoid long or vague names. Good examples: `feature/login-auth`, `bugfix/email-validation`, `hotfix/payment-crash`. Poor example: `feature/stuff` (not descriptive). For more information on the allowed naming conventions, refer to the [Git Branching Strategy](../CONTRIBUTING.md#git-branching-strategy) section.

3. **Work Commit-by-Commit**: Make changes in your branch and commit your work in logical chunks. Each commit should have a clear purpose. Follow our commit message conventions (see below) when writing commit messages. For example:

   ```bash
   git add .
   git commit -m "feat: implement OAuth2 login flow"
   ```

   Commit often to save progress, but **ensure each commit compiles and passes tests** (don't commit broken code). This makes it easier to review and to roll back if needed. If you are working on a large feature, consider breaking it into smaller commits or even multiple smaller feature branches, to make reviews easier.

4. **Keep Your Branch Updated**: If other changes get merged into `staging` while you are working, you should update your branch to avoid drifting too far behind. You can do this by merging `staging` into your branch:

   ```bash
   git pull origin staging
   git merge staging
   ```

   or by rebasing your branch onto the latest staging:

   ```bash
   git fetch origin
   git rebase origin/staging
   ```

   Use the method you're comfortable with. Merging will create a merge commit on your branch, whereas rebasing will rewrite your commits on top of the new `staging` `HEAD` (making the history linear).

> [!CAUTION]
> If rebasing, **be cautious** if your branch is public/shared (i.e. available in the remote repository), as rebasing alters commit history. The key point is to handle conflicts on your branch **before** opening a pull request, so the PR can be merged cleanly. Keeping your branch in sync with `staging` frequently (especially before pushing) reduces big conflict headaches later.

5. **Push Your Branch to GitHub**: When you are ready to share your work (or back it up), push the branch to the remote repository:

   ```bash
   git push -u origin feature/improved-booking-ui
   ```

   The `-u` flag sets the upstream, so future `git push` calls know where to push. Pushing your branch makes it visible to the team on GitHub. You can push even before the feature is complete (mark the pull request as a draft, see next step) if you want others to see progress or help you.

6. **Open a Pull Request (PR)**: On GitHub, open a PR from **your branch into the `staging` branch**. This is how we propose to merge your changes. In the PR description:

   - Provide a **clear title** (e.g., "feat: add OAuth2 login flow" or "fix: fix date validation error on booking form").

   - Give a **description** of what your change does and why. Include any relevant context or screenshots if UI changes are involved.

   - **Link any issues** the PR addresses by referencing the issue number (e.g., "Fixes #123" to auto-close issue #123 when merged).

   - If your PR is still a work in progress (not ready for full review), mark it as a **Draft PR**. This signals it's not final yet.

   - Ensure the PR is targeting the `staging` branch (the base should be `staging` in GitHub's PR settings, not `main`).

   - Add any relevant labels or assign reviewers if you know who should review.

7. **Code Review and Discussion**: Team members will review your pull request (see the [Reviewer's Step-by-Step Guide](REVIEWERS_STEP_BY_STEP.md) for more details). Be responsive to feedback:

   - If changes are requested, push additional commits to your branch to address them. Those commits will automatically show up in the same PR.

   - Keep the discussion civil and focused on the code. The goal is to improve the quality of the codebase, so try not to take feedback personally.

   - Ensure all automated checks pass (our repository may have Continuous Integration (CI) setup to run tests and linters on PRs).

8. **Testing on Staging**: After the review is approved and the PR is merged, the `staging` branch now includes your changes. Our CI/CD pipeline might automatically deploy `staging` to a test server (if configured). Verify that your feature/fix works as expected in the `staging` environment along with other merged changes. If any issues are found, address them by creating a new `bugfix` branch from `staging`.

9. **Branch Protection**: We enforce branch protections on `main` and `staging`. This means you cannot push directly to these branches; all changes must come through PRs with at least one approval. This practice safeguards our important branches from accidental changes. Do not override these protections by forcing pushes. If something absolutely needs to be done (extremely rare), coordinate with the repository admin.

> [!TIP]
>
> **Branch Naming Recap**: Use the prefixes and naming conventions as described (`feature/`, `bugfix/`, `hotfix/`). Keep names concise yet descriptive. It's often helpful to include an issue number or a keyword. Examples:
>
> - `feature/booking-confirmation-email`
> - `feature/langchain-agent-upgrade`
> - `bugfix/typo-on-welcome-page`
> - `hotfix/cert-renewal`
>
> Avoid using ambiguous names like `update-branch` or reusing branch names. Each branch name should ideally be unique and relevant to its content.

By following this workflow, we maintain an organized project history and reduce the chances of errors. Each step (branching, PR, review, merge) acts as a checkpoint to catch issues early and ensure high code quality.

## Next Steps

Usually, when you have completed and submitted your changes, your contribution moves into the review phase (see step 7). In this next stage, a reviewer will assess your submission, ensuring it meets quality standards, adheres to best practices, and aligns with project guidelines.

After this initial assessment, approved commits from `staging` will be selectively collated — typically via cherry-picking — by the reviewer, in preparation for merging into the `main` branch as part of an official release.

Before merging into `main`, these collated changes will undergo an **additional review process** to ensure stability, quality, and alignment with the overall project roadmap.

For a detailed explanation of the reviewer's responsibilities, processes, and best practices, please proceed to the [Reviewer's Step-by-Step Guide](REVIEWERS_STEP_BY_STEP.md).
