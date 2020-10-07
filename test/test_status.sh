#!/bin/bash

# test_status.sh
#   This script functions as a small test suite for the generate_status.py script.  
#

# Find the directory we're in (used to reference other scripts)
my_dir=$(dirname $(readlink -f $0))

tests_passed=0
total_tests=0

# test all cases, expecting a nonzero exit code
export TEST_FILES_COUNT=6
printf "Testing that python3 $my_dir/../generate_status.py $my_dir/all-xml-long returns nonzero\n\nOutput:\n"
python3 $my_dir/../generate_status.py $my_dir/all-xml-long
ret=$?
echo ""
if [ $ret -eq 1 ]; then
    printf "[ \u274c ] python3 $my_dir/../generate_status.py $my_dir/failure-xml-long returned $ret but should nonzero\n"
    echo "This indicates a missing env var or other error not related to the test failing."
elif [ $ret -eq 0 ]; then
    printf "[ \u274c ] python3 $my_dir/../generate_status.py $my_dir/failure-xml-long returned $ret but should nonzero\n"
else
    printf "[ \u2714 ] python3 $my_dir/../generate_status.py $my_dir/failure-xml-long returned $ret as expected\n"
    tests_passed=$((tests_passed+1))
fi
total_tests=$((total_tests+1))

printf "\n----------\n"

# test a single failing xml file, expecting a return code of 3
export TEST_FILES_COUNT=1
printf "Testing that python3 $my_dir/../generate_status.py $my_dir/failure-xml-short returns 3\n\nOutput:\n"
python3 $my_dir/../generate_status.py $my_dir/failure-xml-short
ret=$?
echo ""
if [ $ret -eq 1 ]; then
    printf "[ \u274c ] python3 $my_dir/../generate_status.py $my_dir/failure-xml-short returned $ret but should nonzero\n"
    echo "This indicates a missing env var or other error not related to the test failing."
elif [ $ret -eq 0 ]; then
    printf "[ \u274c ] python3 $my_dir/../generate_status.py $my_dir/failure-xml-short returned $ret but should nonzero\n"
elif [ $ret -eq 3 ]; then
    printf "[ \u2714 ] python3 $my_dir/../generate_status.py $my_dir/failure-xml-short returned $ret as expected\n"
    tests_passed=$((tests_passed+1))
else
    printf "[ \u274c ] python3 $my_dir/../generate_status.py $my_dir/failure-xml-short returned $ret but should return 3\n"
fi
total_tests=$((total_tests+1))

printf "\n----------\n"

# test a single passing xml file, expecting a return code of 0
export TEST_FILES_COUNT=1
printf "Testing that python3 $my_dir/../generate_status.py $my_dir/success-xml-short returns 0\n\nOutput:\n"
python3 $my_dir/../generate_status.py $my_dir/success-xml-short
ret=$?
echo ""
if [ $ret -ne 0 ]; then
    printf "[ \u274c ] python3 $my_dir/../generate_status.py $my_dir/success-xml-short returned $ret but should zero\n"
else
    printf "[ \u2714 ] python3 $my_dir/../generate_status.py $my_dir/success-xml-short returned $ret as expected\n"
    tests_passed=$((tests_passed+1))
fi
total_tests=$((total_tests+1))

printf "\n----------\n"

# test a single skipping test xml file, expecting a return code of 0 (all non-skipped tests pass)
export TEST_FILES_COUNT=1
printf "Testing that python3 $my_dir/../generate_status.py $my_dir/skip-xml-short returns 0\n\nOutput:\n"
python3 $my_dir/../generate_status.py $my_dir/skip-xml-short
ret=$?
echo ""
if [ $ret -ne 0 ]; then
    printf "[ \u274c ] python3 $my_dir/../generate_status.py $my_dir/skip-xml-short returned $ret but should zero\n"
else
    printf "[ \u2714 ] python3 $my_dir/../generate_status.py $my_dir/skip-xml-short returned $ret as expected\n"
    tests_passed=$((tests_passed+1))
fi
total_tests=$((total_tests+1))

printf "\n----------\n"

# test a single malformed xml file, expecting a return code of 4 indicating malformed xml
export TEST_FILES_COUNT=1
printf "Testing that python3 $my_dir/../generate_status.py $my_dir/malformed-xml-short returns 4\n\nOutput:\n"
python3 $my_dir/../generate_status.py $my_dir/malformed-xml-short
ret=$?
echo ""
if [ $ret -eq 1 ]; then
    printf "[ \u274c ] python3 $my_dir/../generate_status.py $my_dir/malformed-xml-short returned $ret but should return 4\n"
    echo "This indicates a missing env var or other error not related to the test failing."
elif [ $ret -eq 0 ]; then
    printf "[ \u274c ] python3 $my_dir/../generate_status.py $my_dir/malformed-xml-short returned $ret but should return 4\n"
elif [ $ret -eq 4 ]; then
    printf "[ \u2714 ] python3 $my_dir/../generate_status.py $my_dir/malformed-xml-short returned $ret as expected\n"
    tests_passed=$((tests_passed+1))
else
    printf "[ \u274c ] python3 $my_dir/../generate_status.py $my_dir/malformed-xml-short returned $ret but should return 4\n"
fi
total_tests=$((total_tests+1))

printf "\n----------\n"

# tests runing tests on a directory where the number of files is less than TEST_FILES_COUNT, expecting rc of 2
export TEST_FILES_COUNT=100
printf "Testing that python3 $my_dir/../generate_status.py $my_dir/failure-xml-long with incorrect TEST_FILES_COUNT returns 2\n\nOutput:\n"
python3 $my_dir/../generate_status.py $my_dir/failure-xml-long
ret=$?
echo ""
if [ $ret -eq 1 ]; then
    printf "[ \u274c ] python3 $my_dir/../generate_status.py $my_dir/failure-xml-long returned $ret but should return 2\n"
    echo "This indicates a missing env var or other error not related to the test failing."
    test_status=$ret
elif [ $ret -eq 0 ]; then
    printf "[ \u274c ] python3 $my_dir/../generate_status.py $my_dir/failure-xml-long returned $ret but should return 2\n"
    test_status=$ret
elif [ $ret -eq 2 ]; then
    printf "[ \u2714 ] python3 $my_dir/../generate_status.py $my_dir/failure-xml-short returned $ret as expected\n"
    tests_passed=$((tests_passed+1))
else
    printf "[ \u274c ] python3 $my_dir/../generate_status.py $my_dir/failure-xml-short returned $ret but should return 2\n"
fi
total_tests=$((total_tests+1))

unset TEST_FILES_COUNT

printf "\n$tests_passed/$total_tests passed\n"

if [ $tests_passed -ne $total_tests ]; then
    exit 1
fi
