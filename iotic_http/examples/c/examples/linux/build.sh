#!/bin/sh
gcc -Wall -Wextra -pedantic -I ../../src -D IOTICAGENT_USE_LIBCURL -o http_entity_list http_entity_list.c ../../src/agent*.c -lcurl -lm

