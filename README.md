# shopingo-backend
- SDM Group 6 final project

## Collaborative development tutorial (Git)
- Firstly, download the project.
```shell
git clone git@github.com:hsiasia/shopingo-backend.git
```

- Every time before starting development of a new feature **(important)**. 
```shell
# make sure you already have the latest version of the project in local env
git checkout master
git pull
```

- Conflicts address **(TODO)**. 
```shell
```

- Start development of a new feature. 
```shell
# branch definition: "ticket number-ticket description"
git checkout -b "01-Google_OAuth_login"
# after finishing development in local env
git add . # git add file
# commit definition "type of modification: short modification description"
# type of modification: feat = new feature, bug = bug fix, chore = chore change(e.g. deleting useless print function...)
git commit -m "feat: Adding_Google_OAuth_loging"
git push
```

- Now, you can deploy a PR on github webpage and have a discussion w/ your classmates