/**
 * Created by mxu on 1/6/17.
 */

/*
 * Open source under the GPLv2 License or later.
 * Copyright (c) 2016, Mac Xu <mxu@marinsoftware.com>.
 */

var JobViewManager = function(containerDivName) {

    this.containerDivName = containerDivName;
    this.containerDiv = $('#' + this.containerDivName);

    this.buildUrl = this.containerDiv.attr('buildUrl');
    this.jobInfo = null;

    this.data = {};
    this.data['methods'] = {};

};

JobViewManager.prototype.load = function() {

    var thisManager = this;

    console.log('build url=' + this.buildUrl);

    $.get('/jenkins/job/' + this.buildUrl, function(jenkinsJobInfo, status) {

        thisManager.jobInfo = jenkinsJobInfo;
        thisManager.jobInfo.projectPath = thisManager.jobInfo.POM_PATH.replace('/pom.xml', '');

        thisManager.showJobName();

        // Jenkins api has some problem with url like this:
        // http://qa-build.marinsoftware.com/job/qa2-bulk-bing-tests-campaign-master/461/testReport/api/json?pretty=true
        // because the info returned from it is NOT complete
        // instead, we use the url with module info in it to get the module specific case info.
        // like this:
        // http://qa-build.marinsoftware.com/job/qa2-bulk-bing-tests-campaign-master/461/com.marin.qa$qa-bulk-bing-tests/testReport/
        // or:
        // http://qa-build.marinsoftware.com/job/qa2-bulk-bing-tests-campaign-master/com.marin.qa$qa-bulk-bing-tests/461/testReport/

        $.each(thisManager.jobInfo.modules, function( index, jobModule ) {

            var jobModuleBuildUrl = jobModule.url + thisManager.jobInfo.lastBuildNumber + '/';

            $.get('/jenkins/build/cases/' + jobModuleBuildUrl, function(jenkinsModuleCaseInfos, status) {

                $.each(jenkinsModuleCaseInfos, function( moduleFullName, moduleMethodInfos ) {

                    // get the test class info, ( test methods, and their test definition file paths etc )
                    $.get('/qacode/testclass/' + moduleFullName + "/" + thisManager.jobInfo.projectPath, function(qaTestClassInfos) {

                        $.each(moduleMethodInfos, function( testMethodName, testMethodCases) {

                            console.log(testMethodName);
                            if (!(testMethodName in qaTestClassInfos.methods)) {
                                console.log("Unrecognized test method: " + testMethodName + " in class " + moduleFullName);
                            } else {

                                var methodViewManager = new MethodViewManager(thisManager.containerDiv);
                                methodViewManager.jobInfo = jenkinsJobInfo;
                                methodViewManager.className = moduleFullName;
                                methodViewManager.methodName = testMethodName;
                                methodViewManager.testCases = testMethodCases;

                                methodViewManager.testDefinitionFile = qaTestClassInfos.methods[testMethodName]['testDefinitionFile'];
                                methodViewManager.testClassFile = qaTestClassInfos.classFile;

                                methodViewManager.initialize();

                            }

                        });

                    });

                });

            });

        });
    });

};

JobViewManager.prototype.showJobName = function() {

    $('#aJenkinsJob').text(this.jobInfo.displayName).attr('target', '_blank').attr('href', this.jobInfo.url);
};


JobViewManager.prototype.createDivForTestMethod = function(jenkinsTestClassName, testMethodName, testCases) {

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

    var headingI = $('<i></i>').addClass('fa fa-bar-chart-o').text(jenkinsTestClassName + "." + testMethodName);
    headingH3.append(headingI);

    var divPanelBody = $('<div></div>').addClass('panel-body');
    primaryPanelDiv.append(divPanelBody);

    this.createDataTable(divPanelBody, testCases);

};

JobViewManager.prototype.createDataTable = function(parentElement, testCases) {

    var thisManager = this;

    var table = $('<table></table>').addClass('table table-bordered table-hover');
    $(parentElement).append(table);

    var tHeader = $("<thead></thead>");
    table.append(tHeader);

    var headerRow = $('<tr></tr>');
    tHeader.append(headerRow);

    var columns = [
        '#',
        'Test Case',
        'Duration'
    ];

    $.each(columns, function( index, column ) {
        var newColumn = $('<th></th>').text(column);
        headerRow.append(newColumn);
    });

    var tBody = $('<tbody></tbody>');
    table.append(tBody);

    var lineIndex = 0;
    $.each(testCases, function( testCaseName, testCaseData ) {
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

        var statusButton = $('<button></button>').attr('type', 'button').addClass('btn btn-block').text(testCaseData.testDescription);
        statusButton.click(function() {
            thisManager.loadTestDefinitionData(table, testCaseData);
        });
        divCaseName.append(statusButton);

        if (testCaseData.status == 'FAILED') {
            statusButton.addClass('btn-danger');
        } else {
            statusButton.addClass('btn-success');
        }

        // test case duration:
        var tdDuration = $('<td></td>').text(testCaseData.duration);
        tr.append(tdDuration);

    });

};


JobViewManager.prototype.createDetailDivs = function(tableElement, headerText, divId) {

    var divDivContainer = $('<div></div>').addClass('panel panel-default');
    $(divDivContainer).insertAfter(tableElement);

    var divHeading = $('<div></div>').addClass('panel-heading').text(headerText);
    divDivContainer.append(divHeading);

    var divBody = $('<div></div>').addClass('panel-body');
    divDivContainer.append(divBody);

    $(tableElement).data(divId, divBody);

};

JobViewManager.prototype.fetchTestClassInfo = function(tableElement, testCaseData, callback) {
    var thisManager = this;

    if ( !$(tableElement).data('test_class_data')) {
        var projectPath = thisManager.jobInfo.POM_PATH.replace('/pom.xml', '');
        $.get('/qacode/testclass/' + testCaseData.className + "/" + projectPath, function(qaTestClassInfos) {

            thisManager.data.methods = qaTestClassInfos.methods;
            callback();
        });
    } else {
        callback();
    }
};


JobViewManager.prototype.newInputGroup = function(parentElement, itemKey, itemValue) {
    // <div class="input-group">
    //     <span class="input-group-addon" id="sizing-addon2">@</span>
    //     <input type="text" class="form-control" placeholder="Username" aria-describedby="sizing-addon2">
    // </div>

    var inputGroup = $('<div></div>').addClass('input-group');
    parentElement.append(inputGroup);

    var span = $('<span></span>').addClass('input-group-addon').text(itemKey);
    inputGroup.append(span);

    var input = $('<input></input>').attr('type', 'text').attr('aria-describedby', 'sizing-addon2').prop('readonly', true)
        .addClass('form-control').attr('placeholder', itemValue);
    inputGroup.append(input);

};


JobViewManager.prototype.loadTestDefinitionData = function(tableElement, testCaseData) {
    if ( !$(tableElement).data('test_definition_div')) {
        this.createDetailDivs(tableElement, 'Test Definition', 'test_definition_div');
    }

    var div = $(tableElement).data('test_definition_div');
    $(div).empty();

    var thisManager = this;
    this.fetchTestClassInfo(tableElement, testCaseData, function() {

        var testJsonFullPath = thisManager.data.methods[testCaseData.methodName]['testDefinitionFile'];
        $.get('/qacode/gettestdefinitions' + testJsonFullPath, function(testDefinitions) {

            var testDefinition = testDefinitions[testCaseData.testDescription];

            thisManager.newInputGroup(div, 'Publisher', testDefinition.publisher);
            thisManager.newInputGroup(div, 'Priority', testDefinition.priority);
            thisManager.newInputGroup(div, 'VO', testDefinition.vo);
            thisManager.newInputGroup(div, 'Description', testDefinition.description);

            console.log(testDefinitions);
        });
    });

};
