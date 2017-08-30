"""Module for CPU related data parsing"""
__author__    = "Copyright (c) 2017, Marin Software>"
__copyright__ = "Licensed under GPLv2 or later."

from app.modules.jenkins import Jenkins

import unittest

class JenkinsTest(unittest.TestCase):


    def test_getJobsOfViews(self):
        url = 'http://ci.marinsw.net/view/Qe/view/Release/view/release-009/view/Tests/'

        jenkins = Jenkins()
        jobs = jenkins.getJobsOfView(url)

        self.assertTrue(len(jobs) > 0, "no jobs were found")

        jobUrl = 'http://ci.marinsw.net/job/qe-costrev-google-cost-tests-qa2-release-009/'
        jobFound = False
        for job in jobs:
            if (job['url'] == jobUrl):
                jobFound = True
                break
        self.assertTrue(jobFound, "costrev google job NOT found")



if( __name__ =='__main__' ):
    unittest.main()
