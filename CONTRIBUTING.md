# How To Contribute

## Overview

Since this is an active, collaborative and fast-paced project, it is crucial that a clean and methodical workflow is adopted.

**Note**: The following workflow has not been accepted by the entire team. It will be discussed in the next meeting. An alternative, simpler, but **slightly** more error prone workflow can also be adopted.

## TL;DR

1. Each task/feature maps to a GitHub issue
2. Each team member works on a branch on a clone of this repo
3. Each team member will (typically) work within a directory, which is their responsibility/area of expertise.
4. Except for the initial commits for creating structure, no commits will be made directly to master.

## Features

For task/issue management, we will use GitHub Issues. Each member of the [team](../README.md#contributors) is responsible for creating an issue for the feature/task they are currently working on, and will self-assign it to themself.

Each commit related to a task should (ideally) have the issue identifier in the commit message. So fir instance, if you are working on issue `#9`, your commit message will look something like:

`git commit -m "Increase accuracy to 95% [#9]"`

## Commit Messages

Commit messages allow us to keep track of the changes made, and logically identify releases. Consider reading [this article](https://chris.beams.io/posts/git-commit/) for good commit message practices.

## Branches

After you clone this repo, please do not work directly on master. There are a couple of reasons why:
1. If someone merges changes into the upstream master and you make changes in your clone, it is a (tiny but very annoying) pain to merge changes without spoiling history
2. If your PR is rejected, you will have to move your commits to another branch, sync from master, and then move them back.

Instead, create a branch off of master, and work on that.

## Steps

  1. Each team member will create a fork of this repository
  2. Create a local clone on your machine:
  ```
  git clone https://github.com/<your_github_id>/clomask
  ```
  3. (ONLY ONCE) Set your upstream to be this repo
    ```
    git remote add upstream https://github.com/havanagrawal/clomask.git
    ```
    Verify if your remote repos are correctly set:
    ```
    git remote -v
    ```
    You should see origin and upstream.
  2. Create a branch off of master, of your fork
  ```
  git checkout -b myfeaturebranch
  ```
  3. Work on your feature/task in the branch
  ```
  # some changes
  git add myfile.py
  git commit -m "Increase accuracy to 99% [#10]"
  git push
  ```
  4. When done, create a PR from your branch (`<your_github_id>/clomask/feature-branch`) to the main repo master (`havanagrawal/clomask/master`).
  5. Wait for review, then get your PR merged.

  7. Now sync your master branch from upstream
  ```
  git merge upstream/master
  git push
  ```
