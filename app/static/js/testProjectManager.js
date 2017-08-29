/**
 * Created by mxu on 1/6/17.
 */

/*
 * Open source under the GPLv2 License or later.
 * Copyright (c) 2016, Mac Xu <mxu@marinsoftware.com>.
 */

var TestProjectManager = function(projectName, dataTableBodyName, passRateDivName, summaryDivName, summaryTextElements) {
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

TestProjectManager.prototype.updateStats = function() {

    this.updatePassRateChart();

    this.summaryTextElements.caseCount.attr('placeholder', this.testCaseCount.toString());
    this.summaryTextElements.checkpointCount.attr('placeholder', this.checkpointCount.toString());
    this.summaryTextElements.jobCount.attr('placeholder', this.jenkinsJobs.length.toString());

    var durationAvg = this.testCaseDurationSum / this.testCaseCount;
    this.summaryTextElements.avarageCaseDuration.attr('placeholder', durationAvg.toFixed(1) + " Seconds");


};

TestProjectManager.prototype.load = function(callback) {

    this.loadTestClasses();
};

TestProjectManager.prototype.loadTestClasses = function(callback) {

    var thisManager = this;

    $.get('qacode/testfiles/' + thisManager.projectName, function(testClasses, status) {

        $.each(testClasses, function(lineIndex, testClassPath) {

            thisManager.classCount++;
            thisManager.updateStats();

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
        });
    });
};


TestProjectManager.prototype.loadTestMethods = function(rowTds, callback) {

    var thisManager = this;
    var testClassFilePath = rowTds.row.data('testClassPath');

    var noMethodAddedYet = true;
    var methodCountPerClass = 1;
    $.get('/qacode/testclass' + testClassFilePath, function(testmethodInfos, callback) {

        $.each(testmethodInfos.methods, function(methodName, methodInfos) {

            thisManager.methodCount++;
            thisManager.updateStats();

            var rowTdsToUpdate = rowTds;

            if (noMethodAddedYet) {
                noMethodAddedYet = false;

            } else {
                rowTdsToUpdate = thisManager.newRow(rowTds.row);
                rowTdsToUpdate.row.data(rowTds.row.data());
            }

            rowTdsToUpdate.row.data('methodInfo', methodInfos);

            thisManager.loadTestCases(rowTdsToUpdate, function(testCaseRowTds) {
                console.log('asdf');
            });

        })
    });

};

TestProjectManager.prototype.loadTestCases = function(rowTds, callback) {

    var thisManager = this;

    var testCaseCountPerMethod = 1;

    var testJsonFilePath = rowTds.row.data('methodInfo').testDefinitionFile;

    var noTestCaseAddedYet = true;
    $.get('/qacode/gettestdefinitions' + testJsonFilePath, function(testDefinitions, callback) {

        var testCaseCountPerMethod = 0;
        $.each(testDefinitions, function(testDescripion, testDefinition) {

            thisManager.testCaseCount++;
            thisManager.updateStats();

            var rowTdsToUpdate = rowTds;

            if (noTestCaseAddedYet) {
                noTestCaseAddedYet = false;
            } else {
                rowTdsToUpdate = thisManager.newRow(rowTds.row);

                rowTdsToUpdate.row.data(rowTds.row.data());
            }

            rowTdsToUpdate.row.data('testCase', testDescripion);

            var testCaseAButton = $('<a></a>').attr('href', '/case').attr('role', 'button')
                .attr('target', '_blank').addClass('btn btn-block')
                .text(testDescripion);
            rowTdsToUpdate.testCase.append(testCaseAButton);

            thisManager.loadCheckpoints(rowTdsToUpdate, testDefinition.checkpoints);

            thisManager.loadPublisher(rowTdsToUpdate.publisher, testDefinition.publisher);

            if ('vo' in testDefinition) {
                rowTdsToUpdate.vo.text(testDefinition.vo);
            } else {
                rowTdsToUpdate.vo.text('N/A');
            }

            if ('priority' in testDefinition) {
                rowTdsToUpdate.priority.text(testDefinition.priority);
            } else {
                rowTdsToUpdate.priority.text('N/A');
            }

            var rowData = rowTdsToUpdate.row.data();
            var testResultUrl = '/mongo/result/';
            if (rowData.testClassName && rowData.methodInfo.method && rowData.testCase) {
                testResultUrl += rowData.testClassName + "/" + rowData.methodInfo.method + "/" + rowData.testCase;
                $.get(testResultUrl, function(testResult) {
                    if (testResult) {

                        if (thisManager.jenkinsJobs.indexOf(testResult.jenkinsJob) == -1) {
                            thisManager.jenkinsJobs.push(testResult.jenkinsJob);
                        }

                        thisManager.testCaseDurationSum += testResult.duration;

                        thisManager.loadTestResults(rowTdsToUpdate.status, testResult.status, testResult.lastCompletedBuild.url);

                        rowTdsToUpdate.vm.text(testResult.VM);
                        rowTdsToUpdate.branch.text(testResult.BRANCH_NAME);
                    }
                });
            } else {
                console.log('data not complete....');
            }
        });
    });
};

TestProjectManager.prototype.loadPublisher = function(td, publisher) {

    if (!publisher) {
        td.text('N/A');
    } else {
        var imgPublisher = $('<img></img>').addClass('publisher_logo').attr('alt', publisher).attr('src', '/images/' + publisher + '.png');
        td.append(imgPublisher);
    }

};

TestProjectManager.prototype.loadCheckpoints = function(rowTds, checkpoints) {

    var thisManager = this;

    var collapseDivHeaderLine = 'Checkpoints';
    if (! checkpoints) {
        checkpoints = ['N/A'];
        collapseDivHeaderLine = 'N/A';
    }

    var panelRoot = $('<div></div>').addClass('panel panel-default');

    rowTds.checkpoints.append(panelRoot);

    var uniqueDivName = 'div_checkpoints_' + Math.random().toString().replace('.', '');

    var headingLink = $('<a></a>')
        .attr('data-toggle', 'collapse')
        .attr('href', '#' + uniqueDivName)
        .attr('role', 'button')
        .addClass('btn btn-default btn-block')
        .text(collapseDivHeaderLine);
    panelRoot.append(headingLink);

    // <span class="glyphicon glyphicon-menu-down"></span>
    if (collapseDivHeaderLine != 'N/A') {
        var glyphSpan = $('<span></span>').addClass('glyphicon glyphicon-menu-down');
        headingLink.append(glyphSpan);
    }

    var divCollapse = $('<div></div>').addClass('panel-collapse collapse').attr('id', uniqueDivName);
    panelRoot.append(divCollapse);

    var listGroup = $('<ul></ul>').addClass('list-group');
    divCollapse.append(listGroup);

    $.each(checkpoints, function(checkpointIndex, checkpoint) {

        thisManager.checkpointCount++;
        thisManager.updateStats();

        var listGroupItem = $('<li></li>').addClass('list-group-item');
        listGroup.append(listGroupItem);

        listGroupItem.text(checkpoint);
    });

};

TestProjectManager.prototype.loadTestResults = function(tdStatus, caseStatus, jenkinsBuildUrl) {

    var thisManager = this;

    var divStatus = $('<div></div>');
    tdStatus.append(divStatus);

    var aButton = $('<a></a>').attr('href', jenkinsBuildUrl).attr('role', 'button').attr('target', '_blank').addClass('btn btn-block');

    divStatus.append(aButton);

    if (caseStatus == 'FAILED' || caseStatus == 'REGRESSION') {
        aButton.addClass('btn-danger').text("Failed");
        thisManager.failedCaseCount++;

    } else if (caseStatus == 'PASSED' || caseStatus == 'FIXED'){
        aButton.addClass('btn-success').text("Passed");
        thisManager.passedCaseCount++;

    } else if (caseStatus == 'SKIPPED'){
        aButton.text("Skipped");
    } else {
        aButton.text(caseStatus);
    }

    thisManager.updateStats();
};

TestProjectManager.prototype.updatePassRateChart = function() {

    var thisManager = this;

    if (!this.passRateChart) {
        this.initializePassRateChart();

        this.summaryDiv.removeClass('div-invisible').addClass('div-visible');
    }

    this.passRateChart.load({
        columns: [
            ['Passed', thisManager.passedCaseCount],
            ['Failed', thisManager.failedCaseCount]
        ],
        keys: {
            value: ['']
        }
    });

};

TestProjectManager.prototype.initializePassRateChart = function () {

    var thisManager = this;
    this.passRateChart = c3.generate({
        bindto: '#' + this.divPassRateName,
        data: {
            columns: [
                ['Passed', thisManager.passedCaseCount],
                ['Failed', thisManager.failedCaseCount]
            ],
            type : 'donut',
            colors: {
                Passed: "green",
                Failed: 'red'
            }
        },
        donut: {
            title: "Case Pass Rate"
        },
        legend: {
            show: true,
            position: 'right'
        }
    });
};

TestProjectManager.prototype.newRow = function(previousElement) {
    var tr = $('<tr></tr>').addClass('align-center');

    if (!previousElement) {
        this.tableBody.append(tr);
    } else {
        tr.insertAfter(previousElement);
    }


    var tds = {};
    tds['row'] = tr;

    var tdPublisher = $('<td></td>');
    tr.append(tdPublisher);
    tds['publisher'] = tdPublisher;

    var tdVo = $('<td></td>');
    tr.append(tdVo);
    tds['vo'] = tdVo;

    var tdTestCase = $('<td></td>');
    tr.append(tdTestCase);
    tds['testCase'] = tdTestCase;

    var tdCheckpoints = $('<td></td>');
    tr.append(tdCheckpoints);
    tds['checkpoints'] = tdCheckpoints;

    var tdPriority = $('<td></td>');
    tr.append(tdPriority);
    tds['priority'] = tdPriority;

    var tdStatus = $('<td></td>');
    tr.append(tdStatus);
    tds['status'] = tdStatus;

    var tdVM = $('<td></td>');
    tr.append(tdVM);
    tds['vm'] = tdVM;

    var tdBranch = $('<td></td>');
    tr.append(tdBranch);
    tds['branch'] = tdBranch;

    return tds;
};

