/**
 * Created by mxu on 1/6/17.
 */

/*
 * Open source under the GPLv2 License or later.
 * Copyright (c) 2016, Mac Xu <mxu@marinsoftware.com>.
 */

var MongoReporter = function(projectName, dataTableBodyName, passRateDivName, summaryDivName, summaryTextElements) {
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


MongoReporter.prototype.load = function(callback) {

    this.loadTestClasses();
};

MongoReporter.prototype.loadTestClasses = function(callback) {

    var thisManager = this;

    $.get('/qacode/testfiles/' + thisManager.projectName, function(testClasses, status) {

        $.each(testClasses, function(lineIndex, testClassPath) {

            // see if this is a valid test class file:
            $.get('/qacode/istestfile' + testClassPath, function(validationResult, status) {

                if (!validationResult.isValidTestClass) {
                    console.log('This is not a valida test class: ' + testClassPath);
                } else {

                    thisManager.classCount++;

                    var newRowTds = thisManager.newRow();

                    var fileNameIndex = testClassPath.lastIndexOf("/") + 1;
                    var testFileName = testClassPath.substr(fileNameIndex);
                    var testClassName = testFileName.replace('.java', '');

                    // newRowTds.testClass.text(testClassName);
                    newRowTds.row.data('testClassPath', testClassPath);
                    newRowTds.row.data('testClassName', testClassName);

                    newRowTds.testClass.text(testClassName);

                    thisManager.loadMongoData(newRowTds.diffResults, testClassPath, callback);

                }

            });

        });
    });
};


MongoReporter.prototype.compareBuilds = function(buildDataA, buildDataB) {
    if (buildDataA.buildNumber < buildDataB.buildNumber) {
        return 1;
    }

    if (buildDataA.buildNumber > buildDataB.buildNumber) {
        return -1;
    }

    return 0;
};


MongoReporter.prototype.loadMongoData = function(td, testClassPath, callback) {

    var thisManager = this;

    $.get('/mongo/resultbyclasspath' + testClassPath, function(buildsInMongo) {

        if (buildsInMongo.length == 0) {
            return;
        }

        buildsInMongo.sort(thisManager.compareBuilds);


        $.each(buildsInMongo, function(lineIndex, testClassPath) {

            // see if this is a valid test class file:
            $.get('/qacode/istestfile' + testClassPath, function(validationResult, status) {

                if (!validationResult.isValidTestClass) {
                    console.log('This is not a valida test class: ' + testClassPath);
                } else {

                    thisManager.classCount++;
                    thisManager.updateStats();

                    var newRowTds = thisManager.newRow();

                    var fileNameIndex = testClassPath.lastIndexOf("/") + 1;
                    var testFileName = testClassPath.substr(fileNameIndex);
                    var testClassName = testFileName.replace('.java', '');

                    // newRowTds.testClass.text(testClassName);
                    newRowTds.row.data('testClassPath', testClassPath);
                    newRowTds.row.data('testClassName', testClassName);

                    newRowTds.testClass.text(testClassName);

                }

            });

        });
    });
};


MongoReporter.prototype.newRow = function(previousElement) {
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

    var tdDiffResults = $('<td></td>');
    tr.append(tdDiffResults);
    tds['diffResults'] = tdDiffResults;

    var tdJenkinsJob = $('<td></td>');
    tr.append(tdJenkinsJob);
    tds['jenkinsJob'] = tdJenkinsJob;

    return tds;
};

