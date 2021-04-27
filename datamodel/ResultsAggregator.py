import untangle, json, xml, os, re, itertools, typing

class ResultsAggregator():

    passed = "passed"
    failed = "failed"
    skipped = "skipped"
    ignored = "ignored"
    total = "total"

    def __init__(self, files=[], ignorelist=[]):
        self.ignorelist = ignorelist
        self.ignorelisted_names = [ iv['name'] for iv in self.ignorelist ]
        # self.__results should only be modified in insert_results and should have
        # self.__results_unsorted set when it is modified without being sorted
        self.__results = []
        # "dirty" flag for sorting - set when the dataset has been modified but not sorted
        # We're doing "lazy" sorting - only sorting results when asked for raw output, for efficiency
        self.__results_unsorted = False
        self.__counts = {
            f"{ResultsAggregator.total}": 0,
            f"{ResultsAggregator.failed}": 0,
            f"{ResultsAggregator.passed}": 0,
            f"{ResultsAggregator.skipped}": 0,
            f"{ResultsAggregator.ignored}": 0
        }
        # coverage contains a live percentage coverage value for tests executed (percentage of total not-skipped)
        #   and tests passed (percentage of executed tests that passed)
        self.__coverage = {
            f"{ResultsAggregator.skipped}": 0,
            f"{ResultsAggregator.passed}": 0,
        }
        for f in files:
            self.load_file(f)


    def get_raw_results(self):
        self.__sort_results()
        return {
            "results": self.__results,
            "coverage": self.__coverage,
            **self.__counts
        }

    
    def get_status(self):
        if self.__counts[ResultsAggregator.failed] > 0:
            return ResultsAggregator.failed
        elif self.__counts[ResultsAggregator.ignored] > 0:
            return ResultsAggregator.ignored
        else:
            return ResultsAggregator.passed

    
    def get_results(self):
        self.__sort_results()
        return self.__results


    def get_coverage(self):
        return self.__coverage

    
    def get_unique_tags_from_failures(self):
        _failures = list(r['metadata'] for r in filter(lambda r: r['state'] == ResultsAggregator.failed, self.__results))
        return self.get_unique_tags(results=_failures)

    
    def get_unique_tags(self, results=None):
        results = self.__results if results is None else results
        # Unravelling the below command:
        #   We map the squad(s) lists from _failures to a single list of lists rather than dicts
        #       handling non-existance elegantly
        #   We then flatten the list of lists using itertools.chain
        #   We then toss that into a set to ensure we only get unique items
        #   Finally we translate that set into an iterable list of tags
        _metadata = list(set(itertools.chain(*map(lambda r: r.get('squad(s)', "Unlabelled"), results))))
        # Here's a more-maintainable backup if we need it later:
        #   _metadata = set()
        #   for r in _failures:
        #      if "squad(s)" in r:
        #          for s in r["squad(s)"]:
        #              _metadata.add(s)
        #   _metadata = list(_metadata)
        _metadata = [f"squad:{s}" for s in _metadata]
        _metadata = _metadata + list(set(map(lambda r: r.get('severity', "Severity 1 - Urgent"), results)))
        _metadata = _metadata + list(set(map(lambda r: r.get('priority', "Priority/P1"), results)))
        return _metadata


    def get_counts(self) -> typing.Dict[str, str]:
        return self.__counts[ResultsAggregator.total], self.__counts[ResultsAggregator.passed], self.__counts[ResultsAggregator.failed], self.__counts[ResultsAggregator.skipped], self.__counts[ResultsAggregator.ignored]


    def insert_result(self, testsuite, state, name, metadata):
        _int_state = state if not (name in self.ignorelisted_names and state == ResultsAggregator.failed) else ResultsAggregator.ignored
        _matching_results = list(filter(lambda d: d['name'] == name and d['testsuite'] == testsuite, self.__results))
        if len(_matching_results) == 0:
            self.__results.append({
                "name": name,
                "state": _int_state,
                "testsuite": testsuite,
                "metadata": metadata
            })
            self.__update_counts(_int_state)
            self.__results_unsorted = True
        elif len(_matching_results) == 1:
            if _int_state == ResultsAggregator.failed or _int_state == ResultsAggregator.ignored:
                self.__update_counts(_int_state, _matching_results[0]['state'])
                _matching_results[0]['state'] = ResultsAggregator.failed
        else:
            raise ValueError(f"More than one matching test case and test suite ")


    def __update_counts(self, newstate, oldstate=None):
        # Iterate counts for pass/fail/skipped/total as needed
        self.__counts[newstate] = self.__counts[newstate] + 1
        if oldstate is not None:
            self.__counts[oldstate] = self.__counts[oldstate] - 1
        self.__counts[ResultsAggregator.total] = self.__counts[ResultsAggregator.total] + 1
        # Update code fail/pass percentage, marking as 0% if 0 tests total ran
        if (self.__counts[ResultsAggregator.total] - self.__counts[ResultsAggregator.skipped]) > 0:
            self.__coverage[ResultsAggregator.passed] = ((self.__counts[ResultsAggregator.passed] 
                / (self.__counts[ResultsAggregator.total] - self.__counts[ResultsAggregator.skipped])) * 100)
        else:
            self.__coverage[ResultsAggregator.passed] = 0
        # Update test execution percentage (% of tests not skipped) if we ran more than 0 total tests
        if self.__counts[ResultsAggregator.total] > 0:
            self.__coverage[ResultsAggregator.skipped] = (100 - ((self.__counts[ResultsAggregator.skipped] 
                / self.__counts[ResultsAggregator.total]) * 100))
        else:
            self.__coverage[ResultsAggregator.skipped] = 0


    def __sort_results(self):
        if self.__results_unsorted:
            self.__results = sorted(self.__results, key = lambda r: r['name'])
            self.__results_unsorted = False


    def load_file(self, filename, filetype=None):
        if filetype == "json": # If caller told us the file was json, assume they're not lying
            self.__load_json(filename)
        elif filetype == "xml": # If caller told us the file was xml, assume they're not lying
            self.__load_xml(filename)
        else: # Otherwise, try to determine the filetype, fall back on exception
            _filetype = ResultsAggregator.determine_filetype(filename) # checks extension and validates against format, tossing error if invalid JSON + XML
            if _filetype == "json":
                self.__load_json(filename)
            elif _filetype == "xml":
                self.__load_xml(filename)
            else:
                raise ValueError(f"Could not determine the correct file format for {filename}.  Please verify that it is valid XML or JSON.")  

    
    def determine_filetype(filename):
        if os.path.isfile(filename):
            with open(filename, 'r+') as _f:
                _contents = _f.read()
                try:
                    _parsed_contents = untangle.parse(_contents)
                    return "xml"
                except xml.sax._exceptions.SAXParseException as ex:
                    pass
                try:
                    _parsed_contents = json.loads(_contents)
                    return "json"
                except json.JSONDecodeError as ex:
                    pass
        else:
            raise FileNotFoundError(f"{filename} not found.  Exiting.")
        raise AttributeError(f"{filename} is not in parsable XML or JSON format and cannot be loaded.")

    
    def __load_xml(self, filename):
        try:
            with open(filename, "r") as test_file:
                _test_results = test_file.read()
                try:
                    _test_results = untangle.parse(_test_results)
                except xml.sax._exceptions.SAXParseException as ex:
                    _test_results = _test_results
        except FileNotFoundError as e:
            print(f"{filename} not found.")
            self.insert_result(f"{filename}", ResultsAggregator.failed, f"Load {filename}", f"{filename} not found", {"message": f"{filename} could not be opened.  Marking as a failure."})
        if _test_results is not None and isinstance(_test_results, untangle.Element):
            # Try catch is necessary to check for the existance of the testsuites child object on the NoneType root object.  
            try:
                for _test_suite in _test_results.testsuites.children:
                    for _case in _test_suite.children:
                        if _case._name == "testcase": # Filter to ensure that we don't accidentally grab non-test-case items (XML can be troublesome)
                            self.insert_result(_test_suite['name'], ResultsAggregator.get_case_state_xml(_case), ResultsAggregator.get_case_name_xml(_case), ResultsAggregator.get_case_metadata_xml(_case, filename))
            except AttributeError as ex:
                for _case in _test_results.testsuite.children:
                    self.insert_result(_test_results.testsuite['name'], ResultsAggregator.get_case_state_xml(_case), ResultsAggregator.get_case_name_xml(_case), ResultsAggregator.get_case_metadata_xml(_case, filename))
        else: # file isn't XML
            self.insert_result(f"{filename}", ResultsAggregator.failed, f"Load {filename}", f"{filename} parse as XML", {"message": f"{filename} not in XML format or is empty.  Marking as a failure."})


    def __load_json(self, filename):
        print("Dummy JSON Load")
        # try:
        #     with open(filename, "r") as test_file:
        #         _test_results = test_file.read()
        #         try:
        #             _test_results = untangle.parse(_test_results)
        #         except xml.sax._exceptions.SAXParseException as ex:
        #             _test_results = _test_results
        # except FileNotFoundError as e:
        #     print(f"{filename} not found.")
        #     self.insert_result(f"{filename}", ResultsAggregator.failed, f"Load {filename}", f"{filename} not found", {"message": f"{filename} could not be opened.  Marking as a failure."})
        # if _test_results is not None and isinstance(_test_results, untangle.Element):
        #     # Try catch is necessary to check for the existance of the testsuites child object on the NoneType root object.  
        #     try:
        #         for _test_suite in test_results.testsuites.children:
        #             for _case in test_suite.children:
        #                 if _case._name == "testcase": # Filter to ensure that we don't accidentally grab non-test-case items (XML can be troublesome)
        #                     self.insert_result(_test_suite, ResultsAggregator.get_case_state_xml(_case), ResultsAggregator.get_case_name_xml(_case), ResultsAggregator.get_case_metadata_xml(_case, filename))
        #     except AttributeError as ex:
        #         for case in test_results.testsuite.children:
        #             self.insert_result(_test_suite, ResultsAggregator.get_case_state_xml(_case), ResultsAggregator.get_case_name_xml(_case), ResultsAggregator.get_case_metadata_xml(_case, filename))
        # else: # file isn't XML
        #     self.insert_result(f"{filename}", ResultsAggregator.failed, f"Load {filename}", f"{filename} parse as XML", {"message": f"{filename} not in XML format or is empty.  Marking as a failure."})


    def get_case_state_xml(case):
        """Return 'passed' if the testcase passed, 'failed' if it failed, 'skipped' if it was skipped.

        Required Parameters:
        case -- an XML testcase object from JUnit XML test output parsed by Untangle
        """
        _skipped = False
        if case.children is not None:
            for result in case.children:
                if result._name == "failure":
                    return ResultsAggregator.failed
                elif result._name == 'skipped':
                    _skipped = True
        if _skipped:
            return ResultsAggregator.skipped
        else:
            return ResultsAggregator.passed


    def get_case_name_xml(case):
        """Return the name of the testcase.  Broken out into a helper function for future extension.

        Required Parameters:
        case -- an XML testcase object from JUnit XML test output parsed by Untangle
        """
        return case['name']


    def get_case_message_xml(case):
        """Return the message from the testcase.  Broken out into a helper function for future extension.

        Required Parameters:
        case -- an XML testcase object from JUnit XML test output parsed by Untangle
        """
        if case.children is not None:
            for result in case.children:
                if result._name == "failure":
                    return result.cdata
        return ""


    def get_case_metadata_xml(case, filename):
        """Return the metadata from the testcase.  Broken out into a helper function for future extension.

        Required Parameters:
        case -- an XML testcase object from JUnit XML test output parsed by Untangle
        """
        _meta = {}
        _meta['message'] =  ResultsAggregator.get_case_message_xml(case)
        _meta['filename'] = os.path.basename(filename)
        _info = re.findall("\[(.*?)\]", ResultsAggregator.get_case_name_xml(case)) 
        if _info and len(_info) >= 3:
            _meta['priority'] = _info[0]
            _meta['severity'] = _info[1]
            _meta['squad(s)'] = _info[2].split(',')
        else:
            # Metadata not set - set defaults
            _meta['priority'] = "Priority/P1"
            _meta['severity'] = "Severity 1 - Urgent"
            _meta['squad(s)'] = ["Unlabelled"]

        return _meta

