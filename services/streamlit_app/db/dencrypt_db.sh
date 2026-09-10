#!/bin/bash

openssl enc -d -aes-256-cbc -in database.db-cifrada  -out database.db -K $key -iv $iv