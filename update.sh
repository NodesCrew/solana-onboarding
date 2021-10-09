#!/bin/sh
cd /home/www/solana-onboarding/;

python3 grab.py;
python3 generate.py;
git add onboarding;
git commit -m "Update database";
git push;

