/**
 * Created by mxu on 1/6/17.
 */

/*
 * Open source under the GPLv2 License or later.
 * Copyright (c) 2016, Mac Xu <mxu@marinsoftware.com>.
 */

var MethodViewManager = function(containerDiv) {

    this.containerDiv = containerDiv;

    this.methodRootDiv = null;

    this.className = null;
    this.methodName = null;
    this.jobInfo = null;
    this.testCases = null;

    this.table = null;

    this.divTestDefinition = null;
    this.divJenkinsLog = null;

    this.testMethodInfo = null;

    this.testDefinitions = null;
    this.testDefinitionFile = null;

    this.testClassFile = null;
    this.jenkinsLogs = null;

};

MethodViewManager.prototype.initialize = function() {

    var thisManager = this;
    this.createRootDiv();

    var caseTableDiv = thisManager.createPanelGroup(thisManager.methodRootDiv, 'Test Cases');
    thisManager.createTable(caseTableDiv);

    // this.preFetchTestClassData(function() {
    //     var caseTableDiv = thisManager.createPanelGroup(thisManager.methodRootDiv, 'Test Cases');
    //     thisManager.createTable(caseTableDiv);
    // });

};

MethodViewManager.prototype.preFetchTestClassData = function(callback) {
    var thisManager = this;

    var projectPath = this.jobInfo.POM_PATH.replace('/pom.xml', '');
    $.get('/qacode/testclass/' + this.className + "/" + projectPath, function(qaTestClassInfos) {

        thisManager.testMethodInfo = qaTestClassInfos.methods[thisManager.methodName];
        callback();
    });
};

MethodViewManager.prototype.createRootDiv = function () {

    var rowDiv = $('<div></div>').addClass('row');
    this.containerDiv.append(rowDiv);

    var colLg12Div = $('<div></div>').addClass('col-lg-12');
    rowDiv.append(colLg12Div);

    var primaryPanelDiv = $('<div></div>').addClass('panel panel-primary');
    colLg12Div.append(primaryPanelDiv);

    var panelHeadingDiv = $('<div></div>').addClass('panel-heading');
    primaryPanelDiv.append(panelHeadingDiv);

    var headingH3 = $('<h3></h3>').addClass('panel-title');
    panelHeadingDiv.append(headingH3);

    var headingI = $('<i></i>').addClass('fa fa-bar-chart-o').text(this.className + "." + this.methodName);
    headingH3.append(headingI);

    var divPanelBody = $('<div></div>').addClass('panel-body');
    primaryPanelDiv.append(divPanelBody);

    this.methodRootDiv = divPanelBody;
};

MethodViewManager.prototype.createPanelGroup = function(container, headerText) {

    var divDivContainer = $('<div></div>').addClass('panel panel-info');
    container.append(divDivContainer);
    // $(divDivContainer).insertAfter(container);

    var divHeading = $('<div></div>').addClass('panel-heading').text(headerText);
    divDivContainer.append(divHeading);

    var divBody = $('<div></div>').addClass('panel-body');
    divDivContainer.append(divBody);

    return divBody;
};

MethodViewManager.prototype.createTable = function (container) {

    var thisManager = this;

    var table = $('<table></table>').addClass('table table-bordered table-hover');
    container.append(table);

    var tHeader = $("<thead></thead>");
    table.append(tHeader);

    var headerRow = $('<tr></tr>');
    tHeader.append(headerRow);

    var columns = [
        '#',
        'Test Case',
        'Duration',
        "Status"
    ];

    $.each(columns, function( index, column ) {
        var newColumn = $('<th></th>').text(column);
        headerRow.append(newColumn);
    });

    var tBody = $('<tbody></tbody>');
    table.append(tBody);

    var lineIndex = 0;

    $.each(thisManager.testCases, function( testCaseName, testCaseData ) {
        lineIndex += 1;

        var tr = $('<tr></tr>');
        tBody.append(tr);

        // line number:
        var tdNumber = $('<td></td>').text(lineIndex.toString());
        tr.append(tdNumber);

        // test case description:
        var tdCaseName = $('<td></td>');
        tr.append(tdCaseName);

        var divCaseName = $('<div></div>');
        tdCaseName.append(divCaseName);

        var testDescriptionButton = $('<button></button>').attr('type', 'button').addClass('btn btn-block').text(testCaseData.testDescription);
        testDescriptionButton.click(function() {
            thisManager.loadTestDefinitionData(thisManager.divTestDefinition, testCaseData);
            thisManager.loadJenkinsResults(thisManager.divTestDefinition, testCaseData);
        });
        divCaseName.append(testDescriptionButton);

        // test case duration:
        var tdDuration = $('<td></td>').text(testCaseData.duration);
        tr.append(tdDuration);

        // status:
        var tdStatus = $('<td></td>');
        tr.append(tdStatus);

        var divStatus = $('<div></div>');
        tdStatus.append(divStatus);

        var statusButton = $('<button></button>').attr('type', 'button').addClass('btn btn-block');
        divStatus.append(statusButton);

        if (testCaseData.status == 'FAILED') {
            statusButton.addClass('btn-danger').text("Failed");
        } else if (testCaseData.status == 'PASSED'){
            statusButton.addClass('btn-success').text("Passed");
        } else if (testCaseData.status == 'FIXED'){
            statusButton.addClass('btn-success').text("Fixed");
        } else if (testCaseData.status == 'SKIPPED'){
            statusButton.text("Skipped");
        } else {
            console.log("Unknown jenkins case status: " + testCaseData.status);
        }

    });

};


MethodViewManager.prototype.loadTestDefinitionData = function(container, testCaseData) {

    var thisManager = this;

    if(!this.testDefinitions) {

        $.get('/qacode/gettestdefinitions' + this.testDefinitionFile, function(testDefinitions) {

            thisManager.testDefinitions = testDefinitions;

            thisManager.loadTestDefinitionData(container, testCaseData);

        });
    } else {

        if (!thisManager.divTestDefinition) {
            thisManager.divTestDefinition = thisManager.createPanelGroup(thisManager.methodRootDiv, 'Test Definitions');
        }
        thisManager.divTestDefinition.empty();

        var testDefinition = this.testDefinitions[testCaseData.testDescription];

        if (!testDefinition) {
            console.log("This case is not found in Jenkins execution result:");
            console.log(testCaseData.testDescription);
        } else {

            this.newInputGroup(thisManager.divTestDefinition, 'Publisher', testDefinition.publisher || 'Not Specified in Test Definition');
            this.newInputGroup(thisManager.divTestDefinition, 'Priority', testDefinition.priority || 'Not Specified in Test Definition');
            this.newInputGroup(thisManager.divTestDefinition, 'VO', testDefinition.vo || 'Not Specified in Test Definition');
            this.newInputGroup(thisManager.divTestDefinition, 'Description', testDefinition.description || testDefinition.testDescription || 'Not Specified in Test Definition');

            if (testDefinition.checkpoints) {
                this.newInputGroupForList(thisManager.divTestDefinition, 'Check points', testDefinition.checkpoints);
            }
        }
    }
};

MethodViewManager.prototype.loadJenkinsResults = function(container, testCaseData) {

    var thisManager = this;

    var lastBuildNumber = this.jobInfo.nextBuildNumber -1;
    var lastBuildUrl = this.jobInfo.url + lastBuildNumber.toString();
    if(!this.jenkinsLogs) {
        $.get('/jenkins/log/' + lastBuildUrl, function(jenkinsLogs) {

            thisManager.jenkinsLogs = jenkinsLogs;

            thisManager.loadJenkinsResults(container, testCaseData);

        });
    } else {

        if (!thisManager.divJenkinsLog) {
            thisManager.divJenkinsLog = thisManager.createPanelGroup(thisManager.methodRootDiv, 'Jenkins Logs');

            var jenkinsLog = this.jenkinsLogs['ClassA']['MethodA']['testDescriptionA1'];

            var divTestStepListGroup = $('<div></div>').addClass('list-group');
            thisManager.divJenkinsLog.append(divTestStepListGroup);

            var testStepLogs = jenkinsLog.testSteps;

            $.each(testStepLogs, function( stepIndex, testStepLog ) {

                var stepLogButton = $('<button></button>').attr('type', 'button').addClass('list-group-item list-group-item-action')
                    .text(testStepLog);
                divTestStepListGroup.append(stepLogButton);
            });
        }

    }

};

MethodViewManager.prototype.newInputGroup = function(parentElement, itemKey, itemValue) {
    // <div class="input-group">
    //     <span class="input-group-addon" id="sizing-addon2">@</span>
    //     <input type="text" class="form-control" placeholder="Username" aria-describedby="sizing-addon2">
    // </div>

    var inputGroup = $('<div></div>').addClass('input-group');
    parentElement.append(inputGroup);

    var brElement = $('<br></br>');
    parentElement.append(brElement);

    var span = $('<span></span>').addClass('input-group-addon input-group-key').text(itemKey);
    inputGroup.append(span);

    var input = $('<input></input>').attr('type', 'text').attr('aria-describedby', 'sizing-addon2').prop('readonly', true)
        .addClass('form-control').attr('placeholder', itemValue);
    inputGroup.append(input);

};

MethodViewManager.prototype.newInputGroupForList = function(parentElement, itemKey, itemValues) {
    // <div class="input-group">
    //     <span class="input-group-addon" id="sizing-addon2">@</span>
    //     <input type="text" class="form-control" placeholder="Username" aria-describedby="sizing-addon2">
    // </div>

    var inputGroup = $('<div></div>').addClass('input-group');
    parentElement.append(inputGroup);

    var brElement = $('<br></br>');
    parentElement.append(brElement);

    var span = $('<span></span>').addClass('input-group-addon input-group-key').text(itemKey);
    inputGroup.append(span);

    var div = $('<div></div>');
    inputGroup.append(div);

    var itemCount = itemValues.length;
    $.each(itemValues, function( itemIndex, itemValue ) {

        var input = $('<input></input>').attr('type', 'text').attr('aria-describedby', 'sizing-addon2').prop('readonly', true)
            .addClass('form-control').attr('placeholder', itemValue);

        div.append(input);

        var brElement = $('<br></br>');
        div.append(brElement);

        if (itemIndex != itemCount - 1) {
            brElement = $('<br></br>');
            div.append(brElement);
        }
    });

};