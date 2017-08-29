/**
 * Created by mxu on 1/6/17.
 */

/*
 * Open source under the GPLv2 License or later.
 * Copyright (c) 2016, Mac Xu <mxu@marinsoftware.com>.
 */

var TestManager = function(tableName) {
    this.tableName = tableName;
    this.table = $('#' + this.tableName);

    this.divPassedCaseStat = $('#divCaseCountPassed');
    this.divFailedCaseStat = $('#divCaseCountFailed');

    this.data = {};
    this.data['builds'] = {};
    this.data['failed_cases_count'] = 0;
    this.data['succeeded_cases_count'] = 0;
};

TestManager.prototype.clearUIDatas = function() {
    this.data['failed_cases_count'] = 0;
    this.data['succeeded_cases_count'] = 0;
    this.refreshTestCastStatOnUI();

    $('#' + this.tableName + ' tbody > tr').remove();
};


TestManager.prototype.loadDatasByJenkinsUrls = function(jenkinsJobUrls) {

    this.clearUIDatas();

    var thisManager = this;

    jenkinsJobUrls.forEach(function(jenkinsUrl) {
        if (!jenkinsUrl.includes('/job/')) {
            // this is the URL of a view
            $.get('jenkins/view/builds/' + jenkinsUrl, function(jobDatas, status) {

                console.log("view: " + jenkinsUrl);
                $.each(jobDatas, function( index, jobData ) {
                    console.log("job: " + jobData.url);
                    thisManager.loadJobDatas(jobData.url);
                });
            });
        } else {
            // this is the URL of a job
            console.log("job: " + jenkinsUrl);
            thisManager.loadJobDatas(jenkinsUrl);
        }
    });
};

TestManager.prototype.loadDatas = function() {

    var thisManager = this;
    $.get('trackedjobs', function(jenkinsUrls, status) {
        thisManager.loadDatasByJenkinsUrls(jenkinsUrls);

        $('[data-toggle="popover"]').popover();
    });
};

TestManager.prototype.loadJobDatas = function(jobUrl) {
    var thisManager = this;

    $.get('jenkins/job/' + jobUrl, function(jobData, status) {

        var jobInfo = {};
        jobInfo['color'] = jobData.color;
        jobInfo['lastBuildNumber'] = jobData.nextBuildNumber - 1;
        jobInfo['url'] = jobData.url;
        jobInfo['name'] = jobData.name;
        jobInfo['branchName'] = jobData.BRANCH_NAME;
        jobInfo['branchVersion'] = jobData.BRANCH_VERSION;
        jobInfo['vm'] = jobData.VM;
        jobInfo['projectPath'] = jobData.POM_PATH.replace('/pom.xml', '');

        $.get('jenkins/build/cases/' + jobData.lastBuild.url, function(jenkinsCaseInfos, status) {

            $.each(jenkinsCaseInfos, function( jenkinsTestClassName, jenkinsTestClassInfos ) {

                // get the test class info from qa code base, once.
                $.get('qacode/testclass/' + jenkinsTestClassName + "/" + jobInfo['projectPath'], function(qaTestClassInfos) {

                    $.each(jenkinsTestClassInfos, function( jenkinsTestMethodName, jenkinsTestMethodDatas ) {

                        if (jenkinsTestMethodName in qaTestClassInfos.methods &&
                            'testDefinitionFile' in qaTestClassInfos.methods[jenkinsTestMethodName]) {
                            var testDefinitionFile = qaTestClassInfos.methods[jenkinsTestMethodName]['testDefinitionFile'];

                            $.get('/qacode/gettestdefinitions' + testDefinitionFile, function(testDefinitions) {

                                $.each(jenkinsTestMethodDatas, function( jenkinsTestCaseDescription, jenkinsTestCaseData ) {

                                    var newTableRow = thisManager.newTableRow();

                                    thisManager.loadJenkinsCaseData(newTableRow, jenkinsTestCaseData, jobInfo);
                                    thisManager.loadTestDefinitionData(newTableRow, testDefinitions[jenkinsTestCaseDescription]);

                                    thisManager.testCaseStats(jenkinsTestCaseData);

                                })
                            });
                        }

                    });
                });

            });

        });

    });
};

TestManager.prototype.testCaseStats = function(jenkinsTestCaseData) {
    var thisManager = this;

    if (jenkinsTestCaseData.status == 'FAILED') {
        thisManager.data.failed_cases_count += 1;
    } else {
        thisManager.data.succeeded_cases_count += 1;
    }

    thisManager.refreshTestCastStatOnUI();
};

TestManager.prototype.refreshTestCastStatOnUI = function() {

    var casesInTotal = this.data.succeeded_cases_count + this.data.failed_cases_count;

    this.divFailedCaseStat.text( this.data.failed_cases_count.toString() + " / " + casesInTotal.toString());
    this.divPassedCaseStat.text( this.data.succeeded_cases_count.toString() + " / " + casesInTotal.toString());
};

TestManager.prototype.createPopOverElement = function(href, title, content, text) {
    // <a href="#" title="Dismissible popover" data-toggle="popover" data-trigger="focus" data-content="Click anywhere in the document to close this popover">Click me</a>

    var aLink = $('<a></a>').attr('href', href).attr('title', title).attr('data-toggle', 'popover').attr('data-trigger', 'focus')
        .attr('data-content', content).text('');

    return aLink;
};

TestManager.prototype.loadJenkinsCaseData = function(newTableRow, jenkinsCase, jobInfo) {

    var popOverElement = this.createPopOverElement('aaa', 'bbb', 'ccc', 'ddd');


    var statusButton = $('<button></button>').attr('type', 'button').addClass('btn btn-block');

    popOverElement.append(statusButton);
    newTableRow.tds.testCase.append(popOverElement);

    if (jenkinsCase.status == 'FAILED') {
        statusButton.addClass('btn-danger').text(jenkinsCase.testDescription);
    } else {
        statusButton.addClass('btn-success').text(jenkinsCase.testDescription);
    }

    // for Jenkins
    // td > div > a > button
    var divJenkins = $('<div></div>');
    newTableRow.tds.jenkins.append(divJenkins);

    var aLink = $('<a></a>').attr("target", "blank").attr("href", jobInfo.url);
    divJenkins.append(aLink);

    var statusButton = $('<button></button>').attr('type', 'button').addClass('btn btn-block').text(jobInfo.name);
    aLink.append(statusButton);

    if (jobInfo.color == 'red') {
        statusButton.addClass('btn-danger');
    } else {
        statusButton.addClass('btn-success');
    }

    newTableRow.tds.vm.text(jobInfo.vm);

    newTableRow.tds.branch.text(jobInfo.branchName);

};

TestManager.prototype.loadTestDefinitionData = function(newTableRow, testDefinition) {

    if ('publisher' in testDefinition) {

        var imgPublisher = $('<img></img>').addClass('publisher_logo').attr('alt', testDefinition.publisher).attr('src', '/images/' + testDefinition.publisher + '.png');
        newTableRow.tds.publisher.append(imgPublisher);
    } else {
        newTableRow.tds.publisher.text('-------------------------');
    }

    if ('feature' in testDefinition) {
        newTableRow.tds.feature.text(testDefinition.feature);
    } else {
        newTableRow.tds.feature.text('-------------------------');
    }

    if ('vo' in testDefinition) {
        newTableRow.tds.vo.text(testDefinition.vo);
    } else {
        newTableRow.tds.vo.text('-------------------------');
    }

    if ('checkpoints' in testDefinition) {

        var checkPointListGroup = $('<ul></ul>').addClass('list-group');
        newTableRow.tds.checkpoints.append(checkPointListGroup);

        $.each(testDefinition.checkpoints, function( index, checkpoint ) {
            var checkPointListItem = $('<li></li>').addClass('list-group-item').text(checkpoint);
            checkPointListGroup.append(checkPointListItem);
        });
    } else {
        newTableRow.tds.checkpoints.text('-------------------------');
    }

    if ('priority' in testDefinition) {
        newTableRow.tds.priority.text(testDefinition.priority);
    } else {
        newTableRow.tds.priority.text('-------------------------');
    }
};

TestManager.prototype.initialize = function() {

    var tHeader = $('#tableTests thead');

    var headerRow = $('<tr></tr>');
    tHeader.append(headerRow);

    var columns = [
        '#',
        'Publisher',
        'Feature',
        'VO',
        'Checkpoints',
        'Test Case',
        "Priority",
        'Jenkins',
        'Branch',
        'VM'
    ];

    $.each(columns, function( index, column ) {
        var newColumn = $('<th></th>').text(column);
        headerRow.append(newColumn);
    });

    this.tagMenuManager = new TagMenuManager(this);

};

TestManager.prototype.newTableRow = function() {
    var tBody = $('#tableTests tbody');

    var rowObject = {};

    var existingRowCount = $('#tableTests tbody tr').length;

    var newRow = $('<tr></tr>');
    tBody.append(newRow);

    rowObject['row'] = newRow;
    rowObject['tds'] = {};

    var tdNumber = $('<td></td>').text(existingRowCount + 1);
    newRow.append(tdNumber);
    rowObject['tds']['buildNumber'] = tdNumber;

    var tdPublisher = $('<td></td>');
    newRow.append(tdPublisher);
    rowObject['tds']['publisher'] = tdPublisher;

    var tdFeature = $('<td></td>');
    newRow.append(tdFeature);
    rowObject['tds']['feature'] = tdFeature;

    var tdVo = $('<td></td>');
    newRow.append(tdVo);
    rowObject['tds']['vo'] = tdVo;

    var tdCheckpoints = $('<td></td>');
    newRow.append(tdCheckpoints);
    rowObject['tds']['checkpoints'] = tdCheckpoints;

    var tdTestCase = $('<td></td>');
    newRow.append(tdTestCase);
    rowObject['tds']['testCase'] = tdTestCase;

    var tdPriority = $('<td></td>');
    newRow.append(tdPriority);
    rowObject['tds']['priority'] = tdPriority;

    var tdJenkins = $('<td></td>');
    newRow.append(tdJenkins);
    rowObject['tds']['jenkins'] = tdJenkins;

    var tdBranch = $('<td></td>');
    newRow.append(tdBranch);
    rowObject['tds']['branch'] = tdBranch;

    var tdVM = $('<td></td>');
    newRow.append(tdVM);
    rowObject['tds']['vm'] = tdVM;

    return rowObject;
};
