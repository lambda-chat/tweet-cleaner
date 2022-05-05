#!/bin/bash -eu

dst="python_packages/python/lib/python3.9/site-packages"
if [ -e $dst ]; then
    echo "$dst already exists. Update them? [y/n]"
    read ans
    if [ $ans != "y" ] && [ $ans != "Y" ]; then
        exit 1
    fi
    rm -rf $dst
fi

poetry export -f requirements.txt > requirements.txt
pip install -r requirements.txt --target=$dst
rm requirements.txt

src="../src/tweet_cleaner"
cp -r $src $dst
