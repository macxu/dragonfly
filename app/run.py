from flask import Flask, render_template, jsonify, request

from app.modules.jenkins import Jenkins

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")


# http://127.0.0.1:5000/jenkins/view/jobs?view=http://ci.marinsw.net/view/Qe/view/Release/view/release-011/view/Tests/
@app.route('/api/jenkins/jobs')
def getJobsByView():
    viewUrl = request.args['view']
    if (not viewUrl):
        return jsonify({"error": "missing query arg of 'view'!"})

    jenkins = Jenkins()
    jobs = jenkins.getJobsOfView(viewUrl)

    return jsonify(jobs)


if __name__ == '__main__':
    app.run()
