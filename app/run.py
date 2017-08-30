from flask import Flask, render_template, jsonify, request

from app.modules.jenkins import Jenkins
from app.modules.maven import Mavener

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/jenkins')
def jenkins():
    return render_template("jenkins.html")

@app.route('/case')
def caseHistory():
    return render_template("case_history.html")


# http://127.0.0.1:5000/jenkins/view/jobs?view=http://ci.marinsw.net/view/Qe/view/Release/view/release-011/view/Tests/
@app.route('/api/jenkins/jobs')
def getJobsByView():
    viewUrl = request.args['view']
    if (not viewUrl):
        return jsonify({"error": "missing query arg of 'view'!"})

    jenkins = Jenkins()
    jobs = jenkins.getJobsOfView(viewUrl)

    return jsonify(jobs)


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


if __name__ == '__main__':
    app.run()
