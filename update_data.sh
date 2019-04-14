#!/bin/bash
python code/python/scraper.py
git add -A
git commit -m "Data update"
git push
