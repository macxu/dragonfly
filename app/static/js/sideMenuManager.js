/**
 * Created by mxu on 1/6/17.
 */

/*
 * Open source under the GPLv2 License or later.
 * Copyright (c) 2016, Mac Xu <mxu@marinsoftware.com>.
 */

var SideMenuManager = function(tagViewManager) {
    this.tagViewManager = tagViewManager;

    this.ul = $('#ulTags');

    this.tagItems = {};

    this.loadTags();
};

SideMenuManager.prototype.loadTags = function() {
    var thisClass = this;
    $.get('jobtags', function(jobs) {
        $.each(jobs, function(index, jobTagsInfo) {
            $.each(jobTagsInfo.tags, function(index, jobTag) {

                if ( !(jobTag in thisClass.tagItems)) {
                    var li = $('<li></li>');
                    thisClass.ul.append(li);

                    var aLink = $('<a></a>').text(' ' + jobTag);
                    li.append(aLink);

                    aLink.click(function() {
                        $(".nav li").removeClass("active");
                        $(this).parent().addClass("active");
                    });

                    thisClass.tagItems[jobTag] = {};

                    thisClass.tagItems[jobTag]['li']= li;
                    thisClass.tagItems[jobTag]['aLink'] = aLink;

                    li.click(function () {
                       console.log(li.data('jenkinsUrls'));

                       thisClass.tagViewManager.loadDatasByJenkinsUrls(li.data('jenkinsUrls'));
                    });
                }

                if (!thisClass.tagItems[jobTag]['li'].data('jenkinsUrls')) {
                    thisClass.tagItems[jobTag]['li'].data('jenkinsUrls', []);
                }

                var JenkinsUrlData = thisClass.tagItems[jobTag]['li'].data('jenkinsUrls');
                JenkinsUrlData.push(jobTagsInfo.url);
                thisClass.tagItems[jobTag]['li'].data('jenkinsUrls', JenkinsUrlData);

            });
        });
    });

};
