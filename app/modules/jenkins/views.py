
"""Module for Jenkins data parsing"""
from app.modules.jenkins.jenkins import Jenkins
from app.modules.jenkins.jenkinsJob import JenkinsJob

__author__    = "Copyright (c) 2017, Marin Software>"
__copyright__ = "Licensed under GPLv2 or later."


from flask import Blueprint, request, jsonify, render_template

jenkinsAPI = Blueprint('jenkinsAPI', __name__, url_prefix='/api/jenkins')
jenkinsPage = Blueprint('jenkinsPage', __name__, url_prefix='/jenkins')

# API
@jenkinsAPI.route('/build', methods=['GET'])
# retrieves/adds polls from/to the database
def getBuildData():
    if (not request.args.get('build')):
        return jsonify({})

    jenkinsBuildUrl = request.args.get('build')
    jenkins = Jenkins()
    jobUrl = jenkins.getJobByBuild(jenkinsBuildUrl)

    reporter = JenkinsJob(jobUrl)
    reporter.load()
    report = reporter.getReport()

    return jsonify(report)


# API
# http://127.0.0.1:5000/jenkins/view/jobs?view=http://ci.marinsw.net/view/Qe/view/Release/view/release-011/view/Tests/
@jenkinsAPI.route('/jobs', methods=['GET'])
def getJobsByView():
    viewUrl = request.args['view']
    if (not viewUrl):
        return jsonify({"error": "missing query arg of 'view'!"})

    jenkins = Jenkins()
    jobs = jenkins.getJobsOfView(viewUrl)

    return jsonify(jobs)


# API
@jenkinsAPI.route('/releases')
def getJenkinsReleaseData():

    if (not request.args.get('release')):
        return jsonify({})

    releaseNumber = request.args.get('release')
    viewUrl = 'http://ci.marinsw.net/view/Qe/view/Release/view/' + releaseNumber + '/view/Tests/'
    print("view URL: " + viewUrl)

    reports = []

    jenkins = Jenkins()
    jobs = jenkins.getJobsByView(viewUrl)
    for job in jobs:
        reports.append(job.getReport())

    return jsonify(reports)


# Page
@jenkinsPage.route('/')
def jenkins():
    if (request.args.get('release')):
        return render_template("jenkins_release.html")
    elif (request.args.get('build')):
        jenkinsBuildUrl = request.args.get('build')
        jenkins = Jenkins()
        jobUrl = jenkins.getJobByBuild(jenkinsBuildUrl)

        reporter = JenkinsJob(jobUrl)
        reporter.load()
        report = reporter.getReport()

        reportJson = jsonify(report)
        return render_template("jenkins_build.html", report = reportJson)
    else:
        return render_template("jenkins.html")