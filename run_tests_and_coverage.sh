#!/bin/bash
coverage run --omit="lib/*","setup.py","kiskadee/tests/*" ./setup.py test 
coverage html
