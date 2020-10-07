"""helpers.py
This file contains a list of helpful "helper" functions for the report generation scripts
in this folder.  

If you want to use this pool of helper functions, just import it by:
from helpers import *
and you'll have access to all of the functions.  
"""

import sys, os, glob, math, re, xml, untangle


def failed(case):
    """Return true if case passed, false if not.

    Params:
        -   case: a case XML object from a JUnit XML ingested through untangle
    """
    if case.children is not None:
        for result in case.children:
            if result._name == "failure":
                return True
    return False


def get_failure_message(case):
    """Return failure message if case failed, nothing if not.  

    Params:
        -   case: a case XML object from a JUnit XML ingested through untangle
    """
    if case.children is not None:
        for result in case.children:
            if result._name == "failure":
                return result.cdata
    return ""


def skipped(case):
    """Return true if case was skipped, false if not.

    Params:
        -   case: a case XML object from a JUnit XML ingested through untangle
    """
    if len(case.children) > 0:
        for result in case.children:
            if result._name == 'skipped':
                return True
    return False


def get_testsuite_failure(testsuites, ignorelist=[]):
    """Return true if all cases in the testsuite passed, false if not.

    Params:
        -   testsuite: a testsuite XML object from a JUnit XML ingested through untangle
    """
    for testsuite in testsuites:
        for case in testsuite.children:
            if failed(case) and not any(ignored_case['name'] == case['name'] for ignored_case in ignorelist):
                return True
    return False


def get_testsuite_results(testsuite):
    """Return the total number of cases and the number of failed cases.

    Params:
        -   testsuite: a testsuite XML object from a JUnit XML ingested through untangle
    """
    _total = 0
    _failed = 0
    _skipped = 0
    _passed = 0
    for case in testsuite:
        _total = _total + 1
        if failed(case):
            _failed = _failed + 1
        elif skipped(case):
            _skipped = _skipped + 1
        else:
            _passed = _passed + 1
    return _total, _failed, _skipped, _passed


def complete_results(foldername):
    """Return true if we received all of the expected test results, true if not.  
    Edge case: return false if we don't know what to expect (TEST_FILES_COUNT is not set)

    Params:
        - foldername    -   the folder that holds our results
    """
    _status = get_status(foldername, silent=True)
    return _status == 1 or _status == 2


def get_file_counts(foldername):
    """Return the number of files found, the number of expected files, and a list of the filenames.

    Prams:
        - foldername    -   the folder that holds the results
    """
    _files = glob.glob(os.path.join(foldername, "*.xml"))
    _filenames = []
    for f in _files:
        _filenames.append(os.path.basename(f))
    _found = len(_files)
    if os.getenv("TEST_FILES_COUNT"):
        _expected = int(os.getenv("TEST_FILES_COUNT"))
    else:
        print("TEST_FILES_COUNT not set, setting to none.")
        _expected = None
    return _found, _expected, _filenames


def get_folder_counts(foldername, ignorelist=[]):
    """Return the total number of cases and the number of failed cases in all results files within a folder.

    Params:
        -   foldername: the name of the folder that holds the test results
    """
    _total = 0
    _failed = 0
    _ignored = 0
    _skipped = 0
    _passed = 0
    _results = get_folder_details(foldername, ignorelist)
    for r in _results:
        _total = _total + 1
        if r["failed"]:
            _failed = _failed + 1
            if r["ignored"]:
                _ignored = _ignored + 1
        elif r["skipped"]:
            _skipped = _skipped + 1
        else:
            _passed = _passed + 1
    return _total, _failed, _skipped, _passed, _ignored


def get_folder_details(foldername, ignorelist=[]):
    """Returns a list of dicts representing the xml test results across all tests, in alphabetical order.  

    Params:
        -   foldername: the name of the folder that holds the test results
    """
    _details = []
    for _results_file in glob.glob(os.path.join(foldername, "*.xml")):
        test_results = None
        try:
            with open(_results_file, "r") as test_file:
                _test_results = test_file.read()
                try:
                    test_results = untangle.parse(_test_results)
                except xml.sax._exceptions.SAXParseException as ex:
                    test_results = _test_results
        except FileNotFoundError as e:
            print(f"{_results_file} not found, which is odd, we just listed a directory to get here, didn't we?")
            _details.append({"failed": True, "skipped": False, "ignored": False, "name": f"{_results_file} File", "message": f"{_results_file} not openable, permissions error?  Marking as a failure just in case!"})
        if test_results is not None and isinstance(test_results, untangle.Element):
            # Try catch is necessary to check for the existance of the testsuites child object on the NoneType root object.  
            try:
                for test_suite in test_results.testsuites.children:
                    for case in test_suite.children:
                        if case._name == "testcase": # Filter to ensure that we don't accidentally grab non-test-case items (XML can be troublesome)
                            _matching_cases = list(filter(lambda d: re.sub("\(.*?\)", "", d['name']) == re.sub("\(.*?\)", "", case['name']), _details))
                            _ignored = True if any(ignored_case['name'] == case['name'] for ignored_case in ignorelist) else False
                            if len(_matching_cases) > 0:
                                for item in _matching_cases:
                                    # if the case failed mark as not skipped but failed
                                    if failed(case):
                                        item["failed"] = True
                                        item["skipped"] = False
                                        item["message"] = get_failure_message(case)
                                    # if the case succeeded (aka didn't fail or skip) and wasn't already marked as a failure
                                    # mark as not skipped (to make sure we never overwrite a true failure flag, we won't touch that flag)
                                    elif not skipped(case) and not item["failed"]:
                                        item["skipped"] = False
                            # if the case is not already present in the results, 
                            else:
                                if failed(case):
                                    _details.append({"failed": True, "skipped": False, "ignored": _ignored, "name": f"{case['name']}", "message": f"{get_failure_message(case)}"})
                                elif skipped(case):
                                    _details.append({"failed": False, "skipped": True, "ignored": _ignored, "name": f"{case['name']}", "message": ""})
                                else:
                                    _details.append({"failed": False, "skipped": False, "ignored": _ignored, "name": f"{case['name']}", "message": ""})
            except AttributeError as ex:
                for case in test_results.testsuite.children:
                    _matching_cases = list(filter(lambda d: re.sub("\(.*?\)", "", d['name']) == re.sub("\(.*?\)", "", case['name']), _details))
                    _ignored = True if any(ignored_case['name'] == case['name'] for ignored_case in ignorelist) else False
                    if len(_matching_cases) > 0:
                        for item in _matching_cases:
                            # if the case failed mark as not skipped but failed
                            if failed(case):
                                item["failed"] = True
                                item["skipped"] = False
                                item["message"] = get_failure_message(case)
                            # if the case succeeded (aka didn't fail or skip) and wasn't already marked as a failure
                            # mark as not skipped (to make sure we never overwrite a true failure flag, we won't touch that flag)
                            elif not skipped(case) and not item["failed"]:
                                item["skipped"] = False
                    # if the case is not already present in the results, 
                    else:
                        if failed(case):
                            _details.append({"failed": True, "skipped": False, "ignored": _ignored, "name": f"{case['name']}", "message": f"{get_failure_message(case)}"})
                        elif skipped(case):
                            _details.append({"failed": False, "skipped": True, "ignored": _ignored, "name": f"{case['name']}", "message": ""})
                        else:
                            _details.append({"failed": False, "skipped": False, "ignored": _ignored, "name": f"{case['name']}", "message": ""})
        else:
            print(f"{_results_file} not found, which is odd, we just listed a directory to get here, didn't we?")
            _details.append({"failed": True, "skipped": False, "ignored": False, "name": f"{_results_file} File", "message": f"{_results_file} not in xml.  Marking as a failure!  Here's the content: {test_results}"})
    return sorted(_details, key=lambda k: k['name'])


def get_status(foldername, ignorelist=[], silent=False):
    """Return a single status code (integer) representing the the test results within a given directory

    Params:
        -   foldername: the name of the folder that holds our test results

    Returns:
        1 - if TEST_FILES_COUNT is not set
        2 - if the TEST_FILES_COUNT is larger than the number of test files actually recieved
        3 - if there was a test failure detected
        4 - if a test file was not in xml format
        5 - if a test file couldn't be found
    """
    _test_filename = foldername
    _test_results = None
    _file_count = math.inf
    _return_code = 0

    # Pre-load our expected number of results files from environment vars
    # exit with non-zero exit code if not set indicating probable failure
    if os.getenv("TEST_FILES_COUNT"):
        _file_count = int(os.getenv("TEST_FILES_COUNT"))
    else:
        print("TEST_FILES_COUNT not set, returning a failure.")
        return 1

    # Make sure that we have the expected number of files, if not exit non-zero
    if len(glob.glob(os.path.join(_test_filename, "*.xml"))) < _file_count:
        if not silent: print("The number of test files doesn't match or exceed the expected count, assuming failure.")
        return 2

    _result = 0
    for _results_file in glob.glob(os.path.join(_test_filename, "*.xml")):
        try:
            with open(_results_file, "r") as test_file:
                _test_results = test_file.read()
                try:
                    test_results = untangle.parse(_test_results)
                except xml.sax._exceptions.SAXParseException as ex:
                    test_results = _test_results
        except FileNotFoundError as ex:
            if not silent: print("Couldn't find the test file, even though I just listed the diretory... Permissions Error?")
            _result = 5
        if isinstance(test_results, untangle.Element):
            # Try catch is necessary to check for the existance of the testsuites child object on the NoneType root object.  
            try:
                if get_testsuite_failure(test_results.testsuites.children, ignorelist=ignorelist):
                    if not silent: print(f"Detected a test suite failure in {_results_file}!")
                    _result = 3 if _result != 4 and _result != 5 else _result
                else:
                    if not silent: print(f"{_results_file} contained no failures.")
            except AttributeError as ex:
                if get_testsuite_failure([test_results.testsuite], ignorelist=ignorelist):
                    if not silent: print(f"Detected a test suite failure in {_results_file}!")
                    _result = 3 if _result != 4 and _result != 5 else _result
                else:
                    if not silent: print(f"{_results_file} contained no failures.")
        else:
            if not silent: print(f"{_results_file} wasn't in XML format, something seems to have gone wrong!")
            _result = 4
    return _result
