#!/bin/bash

export SUBMISSION_CONFIG=config.yml
python -m aiohttp.web triple_store_submitter:init_func
