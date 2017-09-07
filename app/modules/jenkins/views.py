
"""Module for Jenkins data parsing"""
from app.modules.jenkins.jenkins import Jenkins
from app.modules.jenkins.jenkinsJobReporter import JenkinsJobReporter
from app.modules.rester import Rester

__author__    = "Copyright (c) 2017, Marin Software>"
__copyright__ = "Licensed under GPLv2 or later."


from flask import Blueprint, request, jsonify

jenkinsViews = Blueprint('jenkins', __name__, url_prefix='/api/jenkins')

@jenkinsViews.route('/build', methods=['GET'])
# retrieves/adds polls from/to the database
def getBuildData():
    if (not request.args.get('build')):
        return jsonify({})

    jenkinsBuildUrl = request.args.get('build')
    jenkins = Jenkins()
    jobUrl = jenkins.getJobByBuild(jenkinsBuildUrl)

    reporter = JenkinsJobReporter(jobUrl)
    reporter.load()
    report = reporter.getReport()

    return jsonify(report)


# http://127.0.0.1:5000/jenkins/view/jobs?view=http://ci.marinsw.net/view/Qe/view/Release/view/release-011/view/Tests/
@jenkinsViews.route('/jobs', methods=['GET'])
def getJobsByView():
    viewUrl = request.args['view']
    if (not viewUrl):
        return jsonify({"error": "missing query arg of 'view'!"})

    jenkins = Jenkins()
    jobs = jenkins.getJobsOfView(viewUrl)

    return jsonify(jobs)


@jenkinsViews.route('/releases')
def getJenkinsReleaseData():

    if (not request.args.get('release')):
        return jsonify({})

    releaseNumber = request.args.get('release')
    viewUrl = 'http://ci.marinsw.net/view/Qe/view/Release/view/' + releaseNumber + '/view/Tests/'
    print("view URL: " + viewUrl)

    reports = []

    jenkins = Jenkins()
    reporters = jenkins.getReportersByView(viewUrl)
    for reporter in reporters:
        reports.append(reporter.getReport())

    return jsonify(reports)