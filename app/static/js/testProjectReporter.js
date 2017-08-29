/**
 * Created by mxu on 1/6/17.
 */

/*
 * Open source under the GPLv2 License or later.
 * Copyright (c) 2016, Mac Xu <mxu@marinsoftware.com>.
 */

var TestProjectReporter = function(projectName, dataTableBodyName, passRateDivName, summaryDivName, summaryTextElements) {
    this.projectName = projectName;

    this.tableBodyName = dataTableBodyName;
    this.tableBody = $('#' + this.tableBodyName);

    this.tableBody.empty();

    this.summaryDivName = summaryDivName;
    this.summaryDiv = $('#' + summaryDivName);
    this.summaryTextElements = summaryTextElements;

    this.classCount = 0;
    this.methodCount = 0;
    this.testCaseCount = 0;
    this.testCaseDurationSum = 0.00;
    this.checkpointCount = 0;

    this.passedCaseCount = 0;
    this.failedCaseCount = 0;
    this.jenkinsJobs = [];

    this.divPassRateName = passRateDivName;
    this.passRateChart = null;
};

TestProjectReporter.prototype.updateStats = function() {

};

TestProjectReporter.prototype.load = function(callback) {

    this.loadTestClasses();
};

TestProjectReporter.prototype.loadTestClasses = function(callback) {

    var thisManager = this;

    $.get('qacode/testfiles/' + thisManager.projectName, function(testClasses, status) {

        $.each(testClasses, function(lineIndex, testClassPath) {

            // see if this is a valid test class file:
            $.get('qacode/istestfile' + testClassPath, function(validationResult, status) {

                if (!validationResult.isValidTestClass) {
                    console.log('This is not a valida test class: ' + testClassPath);
                } else {

                    thisManager.classCount++;
                    thisManager.updateStats();

                    console.log("new line for: " + testClassPath);
                    var newRowTds = thisManager.newRow();

                    var fileNameIndex = testClassPath.lastIndexOf("/") + 1;
                    var testFileName = testClassPath.substr(fileNameIndex);
                    var testClassName = testFileName.replace('.java', '');

                    // newRowTds.testClass.text(testClassName);
                    newRowTds.row.data('testClassPath', testClassPath);
                    newRowTds.row.data('testClassName', testClassName);

                    thisManager.loadTestMethods(newRowTds, function() {
                        console.log('aaaa');
                    })

                }

            });


        });
    });
};


TestProjectReporter.prototype.loadTestMethods = function(rowTds, callback) {

    var thisManager = this;
    var testClassFilePath = rowTds.row.data('testClassPath');

    var noMethodAddedYet = true;
    var methodCountPerClass = 1;
    $.get('/qacode/testclass' + testClassFilePath, function(testClassInfos, callback) {

        $.each(testClassInfos.methods, function(methodName, methodInfos) {

            thisManager.methodCount++;
            thisManager.updateStats();

            var rowTdsToUpdate = rowTds;

            if (noMethodAddedYet) {
                noMethodAddedYet = false;

            } else {
                console.log("new row for method: " + methodName);
                rowTdsToUpdate = thisManager.newRow(rowTds.row);
                rowTdsToUpdate.row.data(rowTds.row.data());
            }


            methodInfos['classFile'] = testClassInfos.classFile;
            methodInfos['className'] = testClassInfos.className;
            methodInfos['projectName'] = thisManager.projectName;
            rowTdsToUpdate.row.data('methodInfo', methodInfos);

            thisManager.loadTestCases(rowTdsToUpdate, function(testCaseRowTds) {
                console.log('asdf');
            });
        })
    });

};

TestProjectReporter.prototype.loadTestCases = function(rowTds, callback) {

    var thisManager = this;

    var testCaseCountPerMethod = 1;

    var methodInfos = rowTds.row.data('methodInfo');

    var noTestCaseAddedYet = true;
    var testCaseCountPerMethod = 0;

    var testCases = methodInfos.cases;
    $.each(testCases, function(testDescripion, testDefinition) {

        thisManager.testCaseCount++;
        thisManager.updateStats();

        var rowTdsToUpdate = rowTds;

        if (noTestCaseAddedYet) {
            noTestCaseAddedYet = false;
        } else {
            console.log("New row for test case: " + testDescripion);
            rowTdsToUpdate = thisManager.newRow(rowTds.row);

            rowTdsToUpdate.row.data(rowTds.row.data());
        }

        rowTdsToUpdate.row.data('testCase', testDescripion);

        rowTdsToUpdate.testClass.text(methodInfos.className.replace('com.marin.qa.', ''));
        rowTdsToUpdate.testMethod.text(methodInfos.testMethod);

        rowTdsToUpdate.testCase.text(testDescripion);

        thisManager.loadTestResults(rowTdsToUpdate);

    });
};


TestProjectReporter.prototype.loadTestResults = function(rowTdsToUpdate) {

    var thisManager = this;
    var rowData = rowTdsToUpdate.row.data();

    var testResultUrl = '/mongo/result/' + thisManager.projectName + "/";
    if (rowData.methodInfo.className && rowData.methodInfo.testMethod && rowData.testCase) {
        testResultUrl += rowData.methodInfo.className + "/" + rowData.methodInfo.testMethod + "/";

        var testCaseInUrl = rowData.testCase;
        if (testCaseInUrl.startsWith('/')) {
            testCaseInUrl = 'SLASH' + testCaseInUrl.substr(1);
        }
        testResultUrl += testCaseInUrl;
        $.get(testResultUrl, function(jenkinsResults) {
            if (jenkinsResults.length > 0) {

                thisManager.loadJenkinsJobInfo(rowTdsToUpdate, jenkinsResults[0].jobUrl);

                var buildResults = '';
                // build results
                for (var i=0; i < jenkinsResults.length; i++) {
                    var jenkinsResult = jenkinsResults[i];

                    // success or not
                    var resultStatus = jenkinsResult.status;
                    var buildNumber = jenkinsResult.buildNumber;
                    var buildUrl = jenkinsResult.buildUrl;

                    var imgName = '/images/redlight.png';
                    if (resultStatus == 'PASSED') {
                        // TODO: more status should be considered "success"?
                        imgName = '/images/greenlight.png';
                    }

                    var imgStatus = $('<img></img>').addClass('build_result').attr('alt', buildNumber).attr('src', imgName);

                    var aLink = $('<a></a>').attr('href', buildUrl).attr('title', '').attr('target', '_blank').attr('data-toggle', 'popover').attr('data-trigger', 'focus')
                        .attr('data-content', '').text('');

                    aLink.append(imgStatus);

                    rowTdsToUpdate.jenkinsResults.append(aLink);

                    // buildResults += "x";
                }

                // rowTdsToUpdate.jenkinsResults.text(buildResults);

            }
        });
    } else {
        console.log('data not complete....');
    }
};

TestProjectReporter.prototype.loadJenkinsJobInfo = function(rowTdsToUpdate, jobUrl) {

    var linkButton = $('<a></a>').attr('href', jobUrl).attr('role', 'button')
        .attr('target', '_blank').addClass('btn btn-block')
        .text('Jenkins Job');
    rowTdsToUpdate.jenkinsJob.append(linkButton);

};



TestProjectReporter.prototype.newRow = function(previousElement) {
    var tr = $('<tr></tr>').addClass('align-center');

    if (!previousElement) {
        this.tableBody.append(tr);
    } else {
        tr.insertAfter(previousElement);
    }


    var tds = {};
    tds['row'] = tr;

    var tdTestClass = $('<td></td>');
    tr.append(tdTestClass);
    tds['testClass'] = tdTestClass;

    var tdTestMethod = $('<td></td>');
    tr.append(tdTestMethod);
    tds['testMethod'] = tdTestMethod;

    var tdTestCase = $('<td></td>');
    tr.append(tdTestCase);
    tds['testCase'] = tdTestCase;

    var tdJenkinsResults = $('<td></td>');
    tr.append(tdJenkinsResults);
    tds['jenkinsResults'] = tdJenkinsResults;

    var tdJenkinsJob = $('<td></td>');
    tr.append(tdJenkinsJob);
    tds['jenkinsJob'] = tdJenkinsJob;

    return tds;
};

