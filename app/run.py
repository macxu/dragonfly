from flask import Flask, render_template, jsonify, request

from app.modules.jenkins.jenkins import Jenkins
from app.modules.maven import Mavener
from app.modules.mongo import Mongo

app = Flask(__name__)
mongo = Mongo(app)

# Jenkins APIs
from app.modules.jenkins.views import jenkinsAPI
app.register_blueprint(jenkinsAPI)

# Jenkins Pages
from app.modules.jenkins.views import jenkinsPage
app.register_blueprint(jenkinsPage)

@app.route('/')
def index():
    return render_template("jenkins.html")

@app.route('/job')
def jobHistory():
    return render_template("job_history.html")


@app.route('/api/mongo/releases_stats')
def getJenkinsReleaseStats():

    stats = mongo.getReleasesStats()
    return jsonify(stats)

@app.route('/api/mongo/jenkins', methods=['POST'])
def mongoTestCasesByView():
    viewUrl = request.args['view']
    if (not viewUrl):
        return jsonify({"error": "missing query arg of 'view'!"})

    jenkins = Jenkins()
    testCases = jenkins.getTestCasesByView(viewUrl)

    return jsonify({})


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
