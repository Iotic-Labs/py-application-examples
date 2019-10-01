#! /bin/bash

ARGS='end rmdby space=DB'
RUN='python test_iot.py'

## EXAMPLES

$RUN example1 $ARGS
$RUN example1b $ARGS
$RUN example1c $ARGS
$RUN example1d $ARGS
$RUN example2 $ARGS
##$RUN example2b $ARGS
$RUN example3 $ARGS
$RUN example4 $ARGS
$RUN example5 $ARGS
$RUN example5b $ARGS
##$RUN example6 $ARGS
##$RUN example7 $ARGS
$RUN example8 $ARGS
$RUN example9 $ARGS

$RUN example10 $ARGS
$RUN example11 $ARGS
$RUN example12 $ARGS
$RUN example13 $ARGS
$RUN example14 $ARGS
$RUN example15 $ARGS
$RUN example15b $ARGS
$RUN example15c $ARGS
$RUN example16 $ARGS
$RUN example17 $ARGS
$RUN example18 $ARGS
$RUN example19 $ARGS

$RUN example20 $ARGS
$RUN example20b $ARGS
##$RUN example22 $ARGS
$RUN example27 $ARGS

## TESTS
$RUN test1 $ARGS
$RUN test2 $ARGS
$RUN test3 $ARGS
$RUN test4 $ARGS
$RUN test4b $ARGS
$RUN test4c $ARGS
$RUN test5 $ARGS
$RUN test6 $ARGS
$RUN test7 $ARGS
$RUN test8 $ARGS
$RUN test9 $ARGS
$RUN test10 $ARGS
$RUN test11 $ARGS
$RUN test12 $ARGS



#TODO: If anything in errors.txt, it's a fail
#TODO: if results.txt differs from expected_results, fail

# END
