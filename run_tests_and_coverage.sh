#!/bin/bash
coverage run --omit="lib/*","setup.py","kiskadee/tests/*",".eggs/*" ./setup.py test
coverage html
