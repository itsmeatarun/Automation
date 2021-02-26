import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import gzip
import shutil
import tarfile
import os
import json
import requests

def handler(context, inputs):
    certificatesData = inputs["certificatesData"]
    rootCA = inputs["rootCA"]
    workingDir = "/tmp/cert"
    token = inputs["token"]
    domain = inputs["domain"]
    host = inputs["host"]

    os.mkdir(workingDir)
    os.mkdir(workingDir + "/" + domain)

    rootCAFile = open(workingDir + "/" + domain + "/rootca.crt", "a")
    rootCAFile.write(rootCA)
    rootCAFile.close()
    
    for certificateData in certificatesData:
        os.mkdir(workingDir + "/" + domain + "/" + certificateData["name"])

        crtFile = open(workingDir + "/" + domain + "/" + certificateData["name"] + "/" + certificateData["name"] + ".crt", "a")
        crtFile.write(certificateData["crt"])
        crtFile.close()

    for root, dirs, files in os.walk(workingDir + "/"):
        for file in files:
            print("Zipping: " + os.path.join(root, file))

    tardir(workingDir, '/tmp/' + domain + '.tar.gz')

    headers = {
        'Accept': 'application/json',
        'Authorization': token
    }

    endpoint = "https://" + host + "/v1/domains/" + domain + "/certificates/uploads"
    files = {'file': (domain + '.tar.gz', open('/tmp/' + domain + '.tar.gz', 'rb'),'application/tar+gzip')}
    response = requests.put(endpoint, files=files, headers=headers, verify=False)

    outputs = '{"status": "done"}'
    
    return outputs

def tardir(path, tar_name):
    with tarfile.open(tar_name, "w:gz") as tar_handle:
        for root, dirs, files in os.walk(path):
            for file in files:
                tar_handle.add(os.path.join(root, file), arcname=os.path.join(root, file).replace(path + "/",""))
