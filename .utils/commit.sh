#! /bin/bash 


# !!! ⚠️ !!! => you have to authorize the script to be executed : chmow +x .utils/commit.sh (in linux)
isort .
black .

git add .
git commit -m "update"
git push