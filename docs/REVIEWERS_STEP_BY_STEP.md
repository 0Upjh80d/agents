# Reviewer's Step-by-Step Guide

1. **Start with the Latest Code**: Before you begin any work, **pull the latest changes** from the remote repository. For releases, ensure your local `main` branch is up-to-date with the team's repository. This reduces the chance of merge conflicts later. For example, run:

   ```bash
   git checkout main
   git pull origin main
   ```

2. **Code Review and Discussion**: As a reviewer, your role is crucial in maintaining the quality and integrity of our codebase. When reviewing pull requests:

   - Thoroughly evaluate the submitted code, ensuring it adheres to project guidelines, quality standards, and best practices (see [Contributing](../CONTRIBUTING.md) guide for details).

   - Provide clear, constructive, and actionable feedback to the contributor. Maintain a professional and supportive tone to foster a positive collaborative environment.

   - Clearly specify any requested changes and offer guidance or suggestions to facilitate improvements.

   - Ensure that all automated checks, including Continuous Integration (CI) tests and linters, pass successfully before approving the pull request.

3. **Merge the Pull Request**: Once the PR is approved by at least the required number of reviewers (usually 1-2) and all checks passed, it's time to merge:

   - We prefer using **"Squash and Merge"** for most pull requests. Squash merging will take all your commits and combine them into a single commit on the `staging` branch. This keeps the commit history clean and easy to follow (one commit per PR/feature). GitHub allows you to edit the commit message when squashing; make sure to write a concise summary (you can use the PR title and include the issue number).

   - After merging, **delete the feature/bugfix branch** from the remote (GitHub usually gives a button for this). This keeps our repository tidy by removing branches that are no longer needed. You will still have the branch locally, but you can delete it locally too (`git branch -d feature/improved-booking-ui`) since it's merged.

4. **Create a New Branch**: Create a dedicated branch for your release:

   - For a new release, branch off `main` and name it `release/yyyy-mm-dd`. For example:

     ```bash
     git checkout -b release/2025-01-01 main
     ```

     This creates and switches to `release/2025-01-01` based on the latest `main`.

5. **Cherry-pick Approved Commits**: Cherry-pick approved commits from `staging` to `release/yyyy-mm-dd`:

   - We prefer reviewers collate approved commits from `staging` (typically via cherry-picking) onto the release branch. These cherry-picked changes are then prepared to be merged into `main` as part of an official release. Alternatively, open a release PR from `staging` into `main`. This PR should list all the changes (automatically, the commits or PRs included since the last merge to `main`).

   - Use the `git cherry-pick` command to copy the commits from `staging` to `release/yyyy-mm-dd`:

     ```bash
     git cherry-pick <commit-hash>
     ```

     Replace `<commit-hash>` with the hash of the commit you want to cherry-pick. This will copy the commit from `staging` to `release/yyyy-mm-dd`.

     For merge commits (instead of squash), you can use `git cherry-pick <commit-hash> -m 1` instead to copy the commit message from `staging` to `release/yyyy-mm-dd`[^1].

   - Repeat this process for all approved commits from `staging` to `release/yyyy-mm-dd`.

6. **Update the Changelog**: Update the [CHANGELOG.md](../CHANGELOG.md) file with a summary of the release. This file should be updated after each release to keep track of the project's history.

7. **Version Bump**: If this release bumps the project version, the [`pyproject.toml`](../pyproject.toml) file will need to be updated:

   - For minor version bump, run:

     ```bash
     bump-my-version bump minor # v0.1.0 -> v0.2.0
     git add pyproject.toml
     git commit -m "chore(release): bump version to v0.2.0"
     git push origin release/yyyy-mm-dd
     ```

     For major or patch version bumps, replace `minor` with `major` or `patch` accordingly.

   - If no version bumps, run the following instead:

     ```bash
     git commit -m "chore(release): update stable snapshot (yyyy-mm-dd)"
     git push origin release/yyyy-mm-dd
     ```

8. **Push Your Branch to GitHub**: When you are ready to share your release (or back it up), push the branch to the remote repository:

   ```bash
   git push -u origin release/2025-01-01
   ```

   The `-u` flag sets the upstream, so future `git push` calls know where to push. Pushing your branch makes it visible to the team on GitHub. You can push even before the release is complete (mark the pull request as a draft, see next step) if you want others to see progress or help you.

9. **Open a Pull Request (PR)**: On GitHub, open a PR from **your release branch into the `main` branch**. This is how we propose to merge your release. In the PR description:

   - Provide a **clear title**:

     - If there was a version bump for the project: "chore(release): v0.2.0 `<summary>`"

     - If there was no version bump: "chore(release): `<summary>`"

   - **Link any issues** the PR addresses by referencing the issue number (e.g., "Fixes #123" to auto-close issue #123 when merged).

   - If your release is still a work in progress (not ready for full review), mark it as a **Draft PR**. This signals it's not final yet.

   - Ensure the PR is targeting the `main` branch (the base should be `main` in GitHub's PR settings, not `staging`).

10. **Release to Main**: When we decide to release to production (this could be immediately if the change is urgent, or after accumulating a few changes):

    - Ensure `staging` is stable and all intended changes for the release are merged.

    - Review and approve this PR (team lead or devops might handle this), then merge it into `main`. We might use a merge commit here or squash — the choice is up to our convention. Using a merge commit for the release can preserve the individual feature commits (squashed commits) from `staging`, which is preferred.

    - The deployment to production will be triggered after merging to `main` (if CI/CD is set up for that).

    - After release, merge `main` back into `staging` if any new commit (like a hotfix or a generated release commit) was added, to keep them in sync. Often, merging `staging` to `main` via PR won't create any divergence, but in case of a hotfix or if you did a merge commit, syncing `main` into `staging` ensures no disparity.

11. **Release Tags**: Once these changes have been approved and merged into `main`, the resulting commit should be tagged:

    - Tag the release commit on `main` with the new version (if there was a project version bump):

      ```bash
      git tag -a v0.2.0 -m "chore(release): minor update v0.2.0"
      git push origin v0.2.0
      ```

    - If the release did not bump the project version, update only the `stable` tag:

      ```bash
      git tag -fa stable -m "chore(release): update stable snapshot"
      git push origin stable --force
      ```

    - This tagging marks the official release point and helps in tracking and referencing specific versions of the project moving forward.

12. **Branch Protection**: We enforce branch protections on `main` and `staging`. This means you cannot push directly to these branches; all changes must come through PRs with at least one approval. This practice safeguards our important branches from accidental changes. Do not override these protections by forcing pushes. If something absolutely needs to be done (extremely rare), coordinate with the repository admin.

## Next Steps

As a reviewer, you're now prepared to collaborate directly with contributors, guiding their submissions toward successful integration into the project. Contributors will submit their changes through pull requests, which you will evaluate carefully to ensure quality, adherence to standards, and alignment with the project's objectives. During this process, your clear, constructive feedback is essential to refining contributions effectively.

For a detailed overview of how contributors prepare and submit their changes, and to better understand their workflow and perspective, please proceed to the [Contributor's Step-by-Step Guide](CONTRIBUTORS_STEP_BY_STEP.md).

[^1]:
    Why use `-m 1`? The `m` (mainline) option tells Git which parent should be treated as the
    base. `-m 1` means "consider the first parent (the `staging` branch) as the `base` and
    apply the changes from the second parent (`feature/xxx`)." Without `-m 1`, Git will refuse to cherry-pick a merge commit, because it doesn't know which parent to use.
