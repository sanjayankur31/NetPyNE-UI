#!/usr/bin/env python
import sys
import os
import re
import string
import subprocess
import tempfile
import getopt
import time
import shutil
import traceback
import requests
import xml.etree.ElementTree as ET
from jupyter_geppetto import utils
# Flush stdout for debugging
sys.stdout.flush()

# Warning: you probably want to get rid of this line and follow the advice 
# here https://urllib3.readthedocs.org/en/latest/security.html.
requests.packages.urllib3.disable_warnings()

# verbose is enabled/disabled via property file.  See main() below.
verbose=False

def _prefixProperty(property, prefix):
    if property.startswith(prefix):
        return property
    return "%s%s" % (prefix, property)


class Client(object):
    global verbose
    def __init__(self, appID, username, password, baseUrl):
        self.appID = appID
        self.username = username
        self.password = password
        self.baseUrl = baseUrl
        self.headers = {'cipres-appkey': self.appID }
        self.endUsername = self.username


    def listJobs(self):
        """ returns list of JobStatus objects """
        r = self.__doGet__(url=self.baseUrl + "/job/" + self.endUsername + "/?expand=true")
        return self.__parseJobList__(r.text)

    def getJobStatus(self, jobHandle):
        """ queries for status and returns JobStatus object """
        return JobStatus(client=self, jobUrl=self.baseUrl + "/job/" + self.endUsername + "/" + jobHandle)

    def submitJob(self, vParams, inputParams, metadata, validateOnly=False ):
        files = {}
        try:
            for key in inputParams:
                paramname = _prefixProperty(key, "input.")
                pathname = inputParams[key]
                files[paramname] = open(pathname, 'rb')
            payload = []
            
            for key in vParams:
                if key == "toolId" or key == "tool":
                    name = "tool"
                else:
                    name = _prefixProperty(key, "vparam.")
                payload.append((name, vParams[key]))
            
            
            for key in metadata:
                name = _prefixProperty(key, "metadata.")
                payload.append((name, metadata[key]))

            if validateOnly:
                url = self.baseUrl + "/job/" + self.endUsername + "/validate"
            else:
                url = self.baseUrl + "/job/" + self.endUsername

            response = requests.post(url, data=payload, files=files, auth=(self.username, self.password), headers=self.headers, verify=False)
            if verbose:
                print("POSTED Payload of ", payload)
                print("POSTED file list of ", files)
                print("\n")
                print("POST Status = %d" % ( response.status_code))
                print("Response Content = %s" % (response.text))

            if response.status_code == 200:
                return JobStatus(self, xml=ET.fromstring(response.text.encode('utf-8')))
            else:
                self.__raiseException__(response)
        finally:
            for _, openfile in files.items():
                openfile.close
                

    def __raiseException__(self, response):
        """ Throws CipresException or ValidationException depending on the type of xml ErrorData 
        Cipres has returned. """

        httpStatus = response.status_code 
        if response.text and len(response.text) > 0:
            rawtext = response.text 
        else:
            rawtext = "No content returned." 

        # Parse displayMessage, code and fieldErrors from response.text
        displayMessage = None
        cipresCode = 0 
        fieldErrors = {}
        if response.text:
            try:
                element = ET.fromstring(response.text.encode('utf8')) 
                if element.tag == "error":
                    displayMessage = element.find("displayMessage").text
                    cipresCode = int(element.find("code").text)
                    if (cipresCode == 5):
                        for fieldError in element.findall("paramError"): 
                            fieldErrors[fieldError.find("param").text] = fieldError.find("error").text
            except:
                return utils.getJSONError("We couldn't handle the error", sys.exc_info())

        # Show user the http status code and the <displayMessage> if available, otherwise the raw text.
        message = f"HTTP Code: {response.status_code}, "
        message += (rawtext, displayMessage)[displayMessage is not None]

        return {
            "type": httpStatus,
            "code": cipresCode,
            "message": message,
            "fieldErrors": fieldErrors,
            "rawtext": rawtext
        }
        

    def __doGet__(self, url, stream=False ):
        """ Returns xml text or throws a CipresError """
        r = requests.get(url, auth=(self.username, self.password), verify=False, headers = self.headers, stream=stream)
        if verbose:
            print("GET %s\nStatus = %d\nText:%s\n" % (url, r.status_code, r.text))
        if r.status_code != 200:
            self.__raiseException__(r)
        return r

    def __doDelete__(self, url):
        """ Returns nothing or throws a CipresError """
        r = requests.delete(url, auth=(self.username, self.password), verify=False, headers = self.headers)
        if r.status_code != 200 and r.status_code != 204 and r.status_code != 202:
            self.__raiseException__(r)
        if verbose:
            print("DELETE %s\nStatus = %d\nContent = %s" % (url, r.status_code, r.text))
        return r

    def __parseJobList__(self, text):
        """ Converts xml job listing to a list of JobStatus object """
        jobList = []
        et = ET.fromstring(text.encode('utf-8'))
        for xmlJobStatus in et.find("jobs"):
            jobList.append(JobStatus(client=self, xml=xmlJobStatus))
        return jobList
        

class JobStatus(object):
    """ Construct with jobUrl parameter and then call update() to fetch the status or construct with 
    xml parameter containing an element of type jobStatus and ctor will parse out the jobUrl """

    def __init__(self, client, jobUrl=None, xml=None):
        self.client = client 
        self.jobUrl = jobUrl
        self.__clear__()
        if xml is not None:
            self.__parseJobStatus__(xml)
        elif jobUrl is not None:
            self.jobUrl = jobUrl
            self.update()

    def __clear__(self):
        self.resultsUrl = None
        self.workingDirUrl = None
        self.jobHandle = None
        self.jobStage = None
        self.terminalStage = None
        self.failed = None
        self.metadata = None
        self.dateSubmitted = None
        self.messages = [ ] 
        self.commandline = None

    def __parseJobStatus__(self, xml):
        if xml.find("commandline") is not None:
            self.commandline = xml.find("commandline").text
        if xml.find("selfUri") is not None:
            self.jobUrl = xml.find("selfUri").find("url").text
        if xml.find("jobHandle") is not None:
            self.jobHandle = xml.find("jobHandle").text
        if xml.find("jobStage") is not None:
            self.jobStage = xml.find("jobStage").text
        if xml.find("terminalStage") is not None:
            self.terminalStage = (xml.find("terminalStage").text == "true")
        if xml.find("failed") is not None:
            self.failed = (xml.find("failed").text == "true")
            # self.metadata = 
        if xml.find("resultsUri") is not None:
            self.resultsUrl = xml.find("resultsUri").find("url").text
        if xml.find("workingDirUri") is not None:
            self.workingDirUrl = xml.find("workingDirUri").find("url").text
        if xml.find("dateSubmitted") is not None:
            self.dateSubmitted = xml.find("dateSubmitted").text
        # self.messages = [ m.find("text").text for elem in xml.find("messages") ] 
        if xml.find("messages") is not None:
            for m in xml.find("messages"):
                self.messages.append("%s: %s" % (m.find("timestamp").text, m.find("text").text))

    def show(self, messages=False):
        """ A debugging method to dump some of the content of this object to stdout """

        if not self.jobHandle and self.commandline:
            print("Submission validated.  Commandline is: '%s'" % (self.commandline))
            return

        str = "Job=%s" % (self.jobHandle)
        if self.terminalStage:
            if self.failed:
                str += ", failed at stage %s" % (self.jobStage)
            else:
                str += ", finished, results are at %s" % (self.resultsUrl)
        else:
            str += ", not finished, stage=%s" % (self.jobStage)
        print(str)
        if messages:
            for m in self.messages:
                print("\t%s" % (m))
            

    def update(self):
        r = self.client.__doGet__(url=self.jobUrl + "/?expand=true")
        self.__parseJobStatus__(ET.fromstring(r.text.encode('utf-8')))

    def delete(self):
        r = self.client.__doDelete__(url=self.jobUrl)

    def isDone(self):
        return self.terminalStage

    def isError(self):
        return self.failed

    def listResults(self, final=True):
        """Returns dictionary where key is filename and value is a ResultFile object.   If job isn't 
        finished yet and you want a list of what's in the job's working dir, use "final=False", though
        be aware that the working dir is transient and only exists once the job has been staged to the
        execution host and before it's been cleaned up."""  
        if final:
            url = self.resultsUrl
        else:
            url = self.workingDirUrl
        r = self.client.__doGet__(url=url)
        resultFiles = {}
        et = ET.fromstring(r.text.encode('utf-8'))
        for child in et.find("jobfiles"):
            resultFiles[child.find("filename").text] = ResultFile(self.client, child)
        return resultFiles

    def downloadResults(self, directory=None, final=True):
        """Downloads all result files to specified, existant directory, or current directory.  Set final=False
        if you want to download files from the working dir before the job has finished.  Once the job is finished
        use final=True to download the final results."""
        resultFiles = self.listResults(final=final)
        for filename in resultFiles: 
            resultFiles[filename].download(directory)

    def waitForCompletion(self, pollInterval=60):
        """ Wait for job to finish.  pollInterval is 60 seconds by default."""
        while not self.isDone():
            time.sleep(pollInterval)
            self.update()

class ResultFile(object): 
    def __init__(self, client, jobFileElement):
        self.client = client
        self.name = jobFileElement.find("filename").text
        self.url = jobFileElement.find("downloadUri").find("url").text 
        self.length = int(jobFileElement.find("length").text)

    def download(self, directory=None):
        if not directory:
            directory = os.getcwd()
        path = os.path.join(directory, self.name)

        if verbose:
            print("downloading from %s to %s" % (self.url, path))
        r = self.client.__doGet__(self.url, stream=True)
        with open(path, 'wb') as outfile:
            shutil.copyfileobj(r.raw, outfile)
    
    def getName(self):
        return self.name

    def getLength(self):
        return self.length

    def getUrl(self):
        return self.url


    # job = client.submitJob(
    #     {"toolId" : "CLUSTALW", "runtime_" : ".1"},
    #     {"infile_" : "/users/u4/terri/samplefiles/fasta/ex1.fasta"},
    #     {"statusEmail" : "true"}, validateOnly=True)
    # job.show(messages=True)
    # job = client.submitJob(
    #     [
    #         ("toolId", "JMODELTEST2_XSEDE"),
    #         ("runtime_", "0.5"),
    #         ("def_topsearch_", "NNI"),
    #         ("criteria_1_", "-AIC"),
    #         ("criteria_1_", "-DT"),
    #         ("criteria_1_", "-AICc"),
    #         ("criteria_1_", "-BIC"),
    #         ("set_subschemes_", "203"),
    #         ("uneq_basefmodels_", "0"),
    #         ("invar_models_", "0"),
    #         ("numratecat_models_", "8"),
    #         ("parameter_importances_", "0"),
    #         ("estimate_modelavg_", "0"),
    #         ("print_paup_", "0")
    #     ],
    #     {"infile_" : "/users/u4/terri/samplefiles/fasta/ex1.fasta"},
    #     {"statusEmail" : "true"}, validateOnly=True)
    # job.show(messages=True)
    