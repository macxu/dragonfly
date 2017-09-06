from flask import Flask, render_template, jsonify, request, json

from app.modules.jenkins import Jenkins
from app.modules.jenkinsJobReporter import JenkinsJobReporter
from app.modules.maven import Mavener
from app.modules.mongo import Mongo

app = Flask(__name__)
mongo = Mongo(app)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/jenkins')
def jenkins():
    if (request.args.get('release')):
        return render_template("jenkins_release.html")
    elif (request.args.get('build')):
        jenkinsBuildUrl = request.args.get('build')
        jenkins = Jenkins()
        jobUrl = jenkins.getJobByBuild(jenkinsBuildUrl)

        reporter = JenkinsJobReporter(jobUrl)
        reporter.load()
        report = reporter.getReport()

        reportJson = jsonify(report)
        return render_template("jenkins_build.html", report=reportJson)
    else:
        return render_template("jenkins.html")



@app.route('/job')
def jobHistory():
    return render_template("job_history.html")


# http://127.0.0.1:5000/jenkins/view/jobs?view=http://ci.marinsw.net/view/Qe/view/Release/view/release-011/view/Tests/
@app.route('/api/jenkins/jobs')
def getJobsByView():
    viewUrl = request.args['view']
    if (not viewUrl):
        return jsonify({"error": "missing query arg of 'view'!"})

    jenkins = Jenkins()
    jobs = jenkins.getJobsOfView(viewUrl)

    return jsonify(jobs)


@app.route('/api/mongo/releases_stats')
def getJenkinsReleaseStats():

    stats = mongo.getReleasesStats()
    return jsonify(stats)

@app.route('/api/jenkins/build')
def getJenkinsBuildData():
    if (not request.args.get('build')):
        return jsonify({})

    jenkinsBuildUrl = request.args.get('build')
    jenkins = Jenkins()
    jobUrl = jenkins.getJobByBuild(jenkinsBuildUrl)

    reporter = JenkinsJobReporter(jobUrl)
    reporter.load()
    report = reporter.getReport()

    return jsonify(report)


@app.route('/api/jenkins/releases')
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


# http://127.0.0.1:5000/jenkins/view/jobs?view=http://ci.marinsw.net/view/Qe/view/Release/view/release-011/view/Tests/
@app.route('/api/test/definitions')
def getTestDefinitions():

    mavener = Mavener()

    if (request.args['project']):

        return jsonify(mavener.loadTestDefinitionsByProjectName(request.args['project']))

    elif (request.args['file']):

        return jsonify(mavener.loadTestDefinitionsByFilePath(request.args['file']))

    else:
        return jsonify({"error": "'project' or 'file' must be specified in the query"})



# http://127.0.0.1:5000/jenkins/view/jobs?view=http://ci.marinsw.net/view/Qe/view/Release/view/release-011/view/Tests/
@app.route('/api/test/projects')
def getTestProjects():

    mavener = Mavener()
    return jsonify(mavener.getTestProjects())


# NEED to set host='0.0.0.0' otherwise the service won't be reachable when running in a Docker container
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=2906)
