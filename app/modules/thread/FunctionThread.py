import threading

from app.modules.jenkins.jenkinsJob import JenkinsJob


class FunctionThread(threading.Thread):

    def __init__(self, target, *args):
        self._target = target
        self._args = args

        threading.Thread.__init__(self)

    def run(self):
        self._target(*self._args)


if (__name__ == '__main__'):

    jobUrl = 'http://ci.marinsw.net/job/qe-google-bulk-bat-tests-qa2-release-012/'
    jenkinsJob = JenkinsJob(jobUrl)

    t1 = FunctionThread(jenkinsJob.getTestCasesInfo)
    t1.start()
    t1.join()

    print(jenkinsJob.getReport())
    print('sdfsf')

