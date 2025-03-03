# Useful Commands

## Docker relevant

```bash

# List all containers (including stopped)
docker ps -a

# List all images
docker images

# List all volumes
docker volume ls

# Remove container
docker rm -f my_container
# Remove all containers
docker container prune

# Remove image
docker rmi my_image:latest
# Remove all  unused images
docker image prune -a

# Remove volume
docker volume rm my_volume
# Remove all volumes
docker volume prune

# Remove all unused containers, volumes, networks and images
docker system prune -a --volumes
```

## Docker compose

```bash

docker-compose -f docker-compose.prod.yml up --build


# Remove containers, networks
docker-compose -f docker-compose.dev.yml down

# Remove containers, networks, volumes, and only local images
docker-compose -f docker-compose.dev.yml down -v --rmi local

# Remove containers, networks, volumes, and images
docker-compose -f docker-compose.dev.yml down -v --rmi all

# Remove everything and remove orphaned containers
docker-compose -f docker-compose.dev.yml down -v --rmi all --remove-orphans


```


## Frontend relevant

```bash
npm install

npm run dev

npm run build
npm run preview

```

## Git

```bash

git log --oneline
git log --oneline -n 3

git add .
git add file_1 file_2
git commit -m "commit staged changes"
git commit -am "directly stage and commit all change"



# --- update commit message ---

## --- update ONLY the last commit ---
git commit --amend -m "New message for last commit"

## --- update 2nd last commit ---
git rebase -i HEAD~2  # this will open vim, press esc+i to go into insert mode
# In the editor that opens, you'll see something like:
pick abc1234 Old commit message 1
pick def5678 Old commit message 2
# Change 'pick' to 'reword' or 'r' for commits you want to change:
reword abc1234 Old commit message 1
pick def5678 Old commit message 2
# Then you can modify message "Old commit message 1". use :wq to save and quit


# --- rollback current working branch ---

## --- clean untracked files ---
# Print out the list of files and directories which will be removed (dry run)
git clean -n -d
# Delete the files from the repository
git clean -f
# Remove directories, run:
git clean -fd
# Remove ignored files, run:
git clean -fX
# Remove ignored and non-ignored files, run 
git clean -fx

## --- Remove all uncommitted changes ---
# always do `git status` before run git reset
git reset --hard


# --- update content for the commit ---

## --- amend ONLY the last commit
# First, update the files as what you want
git add .
git commit --amend -m "the existed commit content and message will be updated"

## --- amend second last commit with rebase approach
# In the editor that opens, mark the 2nd last commit to edit with 'edit'
git rebase -i HEAD~2
# In the editor that opens, you'll see something like:
pick abc1234 Old commit message 1
pick def5678 Old commit message 2
# First, update the files as what you want
edit abc1234 Old commit message 1
pick def5678 Old commit message 2
# Then for the selected commit, make your change in the codes, and then:
git add .
git commit --amend
git rebase --continue
# if there will be conflict between 2nd last and the last commits:
# Option 1: Resolve the conflict
# a. Open the conflicted files
# b. Look for conflict markers (<<<<<<, =======, >>>>>>>)
# c. Edit the files to resolve conflicts
# d. Then:
git add .
git rebase --continue

# Option 2: Skip this commit
git rebase --skip

# Option 3: Abort the rebase and go back to original state
git rebase --abort


## --- amend second last commit with clean branch approach
# Scenario: we accidentally commit the constant.txt file with password inside in the 2nd last commit
# We want to keep the changes in the last commit but we want to fully remove record in 2nd last commit from git history:

# get and note down the commit hashes and commit message for the last two commits:
git log -n 3
# commit hash_code_1 (HEAD -> master)
# commit hash_code_2
# commit hash_code_3

# Create new clean branch which is back to 3rd last commit status (move 2 steps back from HEAD)
git checkout -b clean-branch HEAD~2

# Cherry-pick 2nd last commits and remove password from constant.txt
git cherry-pick --no-commit hash_code_2
git reset constant.txt
git add .
git commit -m "Your original commit message for 2nd last change"

# cherry pick the last commit without touching anything 
git cherry-pick --no-commit commit_hash_1
git add .
git commit -m "Your original commit message for the last change"

# Switch to your main branch and force update it
git checkout main
git reset --hard clean-branch

```
