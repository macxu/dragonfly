/**
 * Created by mxu on 1/6/17.
 */

/*
 * Open source under the GPLv2 License or later.
 * Copyright (c) 2016, Mac Xu <mxu@marinsoftware.com>.
 */

var TagViewManager = function(tableName, divPassRateName) {
    this.tableName = tableName;
    this.table = $('#' + this.tableName);

    this.divPassRateName = divPassRateName;
    this.passRateChart = null;

    this.passJobCountPerTag = 0;
    this.failedJobCountPerTag = 0;
    this.skippedJobCountPerTag = 0;

    this.data = {};
    this.data['builds'] = {};
    this.data['failed_cases_count'] = 0;
    this.data['succeeded_cases_count'] = 0;
};

TagViewManager.prototype.clearUIDatas = function() {
    this.passJobCountPerTag = 0;
    this.failedJobCountPerTag = 0;
    this.skippedJobCountPerTag = 0;
    this.updatePassRateChart();

    $('#' + this.tableName + ' tbody > tr').remove();
};


TagViewManager.prototype.loadDatasByJenkinsUrls = function(jenkinsJobUrls) {

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

TagViewManager.prototype.loadDatas = function() {

    var thisManager = this;
    $.get('trackedjobs', function(jenkinsUrls, status) {
        thisManager.loadDatasByJenkinsUrls(jenkinsUrls);

        $('[data-toggle="popover"]').popover();
    });
};

TagViewManager.prototype.loadJobDatas = function(jobUrl) {
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

        var newLine = thisManager.newTableRow();

        newLine.tds.branch.text(jobData.BRANCH_NAME);
        newLine.tds.vm.text(jobData.VM);

        // Jenkins column:
        var divJenkins = $('<div></div>');
        newLine.tds.jenkins.append(divJenkins);

        var lastBuildUrl = jobUrl + jobInfo['lastBuildNumber'];
        var aLink = $('<a></a>').attr("target", "blank").attr("href", 'job/' + lastBuildUrl);
        divJenkins.append(aLink);

        var statusButton = $('<button></button>').attr('type', 'button').addClass('btn btn-block').text(jobInfo.name);
        aLink.append(statusButton);

        if (jobInfo.color == 'red') {
            statusButton.addClass('btn-danger');
            thisManager.oneMoreFailedJob();
        } else {
            statusButton.addClass('btn-success');
            thisManager.oneMorePassedJob();
        }
    });
};

TagViewManager.prototype.testCaseStats = function(jenkinsTestCaseData) {
    var thisManager = this;

    if (jenkinsTestCaseData.status == 'FAILED') {
        thisManager.data.failed_cases_count += 1;
    } else {
        thisManager.data.succeeded_cases_count += 1;
    }

    thisManager.refreshTestCastStatOnUI();
};

TagViewManager.prototype.refreshTestCastStatOnUI = function() {

    var casesInTotal = this.data.succeeded_cases_count + this.data.failed_cases_count;

    this.divFailedCaseStat.text( this.data.failed_cases_count.toString() + " / " + casesInTotal.toString());
    this.divPassedCaseStat.text( this.data.succeeded_cases_count.toString() + " / " + casesInTotal.toString());
};

TagViewManager.prototype.createPopOverElement = function(href, title, content, text) {
    // <a href="#" title="Dismissible popover" data-toggle="popover" data-trigger="focus" data-content="Click anywhere in the document to close this popover">Click me</a>

    var aLink = $('<a></a>').attr('href', href).attr('title', title).attr('data-toggle', 'popover').attr('data-trigger', 'focus')
        .attr('data-content', content).text('');

    return aLink;
};

TagViewManager.prototype.loadJenkinsCaseData = function(newTableRow, jenkinsCase, jobInfo) {

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

TagViewManager.prototype.loadTestDefinitionData = function(newTableRow, testDefinition) {

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

TagViewManager.prototype.initialize = function() {

    var tHeader = $('#' + this.tableName + ' thead');

    var headerRow = $('<tr></tr>');
    tHeader.append(headerRow);

    var columns = [
        '#',
        'Jenkins',
        'Branch',
        'VM'
    ];

    $.each(columns, function( index, column ) {
        var newColumn = $('<th></th>').text(column);
        headerRow.append(newColumn);
    });

    this.sideMenuManager = new SideMenuManager(this);
};

TagViewManager.prototype.oneMorePassedJob = function () {

  this.passJobCountPerTag += 1;
  this.updatePassRateChart();

};

TagViewManager.prototype.oneMoreFailedJob = function () {

    this.failedJobCountPerTag += 1;
    this.updatePassRateChart();

};

TagViewManager.prototype.oneMoreSkippedJob = function () {

    this.skippedJobCountPerTag += 1;
    this.updatePassRateChart();

};

TagViewManager.prototype.initializePassRateChart = function () {

    this.passRateChart = c3.generate({
        bindto: '#' + this.divPassRateName,
        data: {
            columns: [
                ['Passed', this.passJobCountPerTag],
                ['Failed', this.failedJobCountPerTag],
                ['Skipped', this.skippedJobCountPerTag]
            ],
            type : 'donut',
            colors: {
                Passed: "green",
                Failed: 'red',
                Skipped: "orange"
            }
        },
        donut: {
            title: "Job Pass Rate"
        },
        legend: {
            show: true,
            position: 'right'
        }
    });
};

TagViewManager.prototype.updatePassRateChart = function(overallData) {

    if (!this.passRateChart) {
        this.initializePassRateChart();
    }

    this.passRateChart.load({
        columns: [
            ['Passed', this.passJobCountPerTag],
            ['Failed', this.failedJobCountPerTag],
            ['Skipped', this.skippedJobCountPerTag]
        ],
        keys: {
            value: ['']
        }
    });

};

TagViewManager.prototype.newTableRow = function() {
    var tBody = $('#' + this.tableName + ' tbody');

    var rowObject = {};

    var existingRowCount = $('#' + this.tableName + ' tbody tr').length;

    var newRow = $('<tr></tr>');
    tBody.append(newRow);

    rowObject['row'] = newRow;
    rowObject['tds'] = {};

    var tdNumber = $('<td></td>').text(existingRowCount + 1);
    newRow.append(tdNumber);
    rowObject['tds']['lineNumber'] = tdNumber;

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
