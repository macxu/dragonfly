/**
 * Created by mxu on 1/6/17.
 */

/*
 * Open source under the GPLv2 License or later.
 * Copyright (c) 2016, Mac Xu <mxu@marinsoftware.com>.
 */

var BuildReporter = function(parentElementId) {
    this.parentElement = $('#' + parentElementId);

    this.statusElements = {};
    this.url =  "/mongo/builds";

    var thisClass = this;

    // auto refresh every 3 seconds.
    // this.intervalId = setInterval(function () {
    //     thisClass.update();
    // }, 3 * 1000);

};

BuildReporter.prototype.update = function() {

    var thisClass = this;
    $.get( thisClass.url, function( buildDatas ) {

        for (var jobUrl in buildDatas) {
            var buildNumbers = buildDatas[jobUrl];

            if (!(jobUrl in thisClass.statusElements)) {
                // create the progress bar elements for this job

                var jobProgressBarDivContainer = $('<div></div>').addClass('progress');

                thisClass.parentElement.append(jobProgressBarDivContainer);

                var divProgressBar = $('<div></div>').addClass('progress-bar progress-bar-info')
                    .attr('role', 'progressbar')
                    .attr('aria-valuemin', 0)
                    .css('width', '100%')
                    .text('');
                jobProgressBarDivContainer.append(divProgressBar);

                thisClass.statusElements[jobUrl] = divProgressBar;
            }

            thisClass.statusElements[jobUrl]
                .attr('aria-valuemax', buildNumbers.length)
                .attr('aria-valuenow', buildNumbers.length)
                .text(jobUrl + " : " + buildNumbers.length + " builds to parse");
        }

    });

};
