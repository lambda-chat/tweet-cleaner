#!/bin/bash -eu

dst="python_packages/python/lib/python3.9/site-packages"
if [ -e $dst ]; then
    echo "$dst already exists. Update them? [y(yes)|n(no)|q(quit)]"
    read ans
    if [ $ans = "y" ] || [ $ans = "Y" ]; then
        rm -rf $dst
        poetry export -f requirements.txt > requirements.txt
        pip install -r requirements.txt --target=$dst
        rm requirements.txt
        src="../src/tweet_cleaner"
        cp -r $src $dst
    elif [ $ans != "n" ] && [ $ans != "N" ]; then
        exit 1
    fi
fi

cdk deploy
