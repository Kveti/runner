import subprocess
from tr.testrail import * 
import json
import requests
from bs4 import BeautifulSoup
import time
import os
import datetime
from tr import nextcloud_upload as cloud
from pprint import pprint

user = ''
password = ''

def tr_upload_results(config, project, title, output_file):
    print("Sir, I am UPLOADING RESULTS TO THE TEST RAIL.")

    cmd = f"trcli -y -c {config} --project {project} parse_robot -f {output_file} --title {title}"
    result = subprocess.run(cmd, shell=True, text=True, capture_output=True)

    stdout = result.stdout.split('\n')
    stderr = result.stderr.split('\n')
    exit_code = result.returncode

    return {"stdout":stdout, "stderr": stderr, "return_code":exit_code}

def setAPI():
    client = APIClient('http://maurit.testrail.io/')
    client.user = user
    client.password = password
    return client

def all_projects():
    client = setAPI()
    case = client.send_get(f"get_projects")
    return case

def get_templates(id: int):
    client = setAPI()
    case = client.send_get(f"get_reports/{id}")
    return case

def run_report(id):
    client = setAPI()
    case = client.send_get(f"run_report/{id}")
    return case

def download_report(url: str, path: str):
    credentials = {
        'name': user,
        'password': password
    }

    session = requests.Session()
    session.headers.update({'User-Agent': 'Teresa'})
    response = session.get(url)

    soup = BeautifulSoup(response.content, 'html.parser')
    # Find the form tag and get the value of the action attribute
    form_tag = soup.find('form')
    if form_tag:
        # index.php?/auth/login/L3JlcG9ydHMvZ2V0X3BkZi8xNjgtZDAyZDAyNmJiYzk0MmNiNjQwZTM4MDA5MTUxODBmNTg3YzFlNjM4MzY4ZTg4NDY2NGQzYWQ5MzA2ZTcwNDgyMw::
        action_value = form_tag.get('action')
        
        url2 = "https://maurit.testrail.io/" + action_value
        r = session.post(url2, data=credentials)
        #print(r.content)
        response = session.get(url)
    
        with open(path, 'wb') as f:
            f.write(response.content)
        
        # Close the session (optional)
        session.close()


def generate_all_reports(path: str):
    reports = []
    ret = []
    projects = all_projects()
    templs = []

    #get templates
    print(f"Processing templates")
    for project in projects['projects']:
        print(project['name'])
        templates = get_templates(project['id'])
        for template in templates:
            templ = {}
            templ['project'] = {'id': project['id'], 'name': project['name']}
            templ['template'] = template
            templs.append(templ)
        
    print(f"Generating reports")
    for templ in templs:
        try:
            urls = run_report(int(templ['template']['id']))
            report = {}
            report['template'] = templ['template']
            report['pdf'] = urls['report_pdf']
            report['html'] = urls['report_html']
            report['name'] = templ['template']['name']
            report['project'] = templ['project']['name']
            report['project_id'] = templ['project']['id']
            reports.append(report)
        except Exception as error:
            print("An error occurred:", error) # An error occurred: name 'x' is not defined

    return reports

def time_folder() -> str:
    current_date = datetime.datetime.now()
    month_number = current_date.month-1
    if month_number == 0:
        month_name = str(current_date.year-1) + ".12"
    else:
        month_name = str(current_date.year) + "." + '{:02d}'.format(month_number)
    return month_name

def write_reports_to_file(reports, path):
    #Specify the file path where you want to save the dictionary
    #file_path = path + "data.json"
    
    # Save the dictionary to a file in JSON format
    with open(path, "w") as file:
        json.dump(reports, file)


def read_reports_from_file(path):
    # Specify the file path from which you want to read the JSON data
    #file_path = path + "data.json"
    
    # Read JSON data from the file and load it into a Python dictionary
    with open(path, "r") as file:
        reporty = json.load(file)

def download_all_reports(reports, path: str):
    month_name = time_folder()
    
    #ret.append("Stahujem reporty")
    for report in reports:
        # vytvorim cestu pre reporty
        disk_path = path + report['project'] + "/" + month_name + "/"
        cloud_path = report['project'] + "/REPORTY/" + month_name + "/"
        if_not_dir_create(disk_path)
        # stiahnem reporty
        #ret.append(f"project: {report['project']}, report: {report['name']}, pdf: {report['pdf']}, html: {report['html']}")
        download_report(report['pdf'], disk_path + report['name'] + ".pdf")
        #download_report(report['html'], disk_path + report['name'] + ".html")
        



def upload_reports(reports, path: str):
    month_name = time_folder()
    ret = []
    ret.append("Stahujem reporty")
    for report in reports:
        # vytvorim cestu pre reporty
        disk_path = path + report['project'] + "/" + month_name + "/"

        cloud_path = report['project'] #+ "/reporty/" + month_name + "/"

        if not cloud.cloud_check_path(cloud_path):
            print(f"vytvaram priecinok na cloude {cloud_path=}")
            try:
                cloud.cloud_make_path(cloud_path)
            except Exception as error:
                print("An error occurred:", error) # An error occurred: name 'x' is not defined

        cloud_path = report['project'] + "/reporty/" #+ month_name + "/"

        if not cloud.cloud_check_path(cloud_path):
            print(f"vytvaram priecinok na cloude {cloud_path=}")
            try:
                cloud.cloud_make_path(cloud_path)
            except Exception as error:
                print("An error occurred:", error) # An error occurred: name 'x' is not defined

        cloud_path = cloud_path + month_name + "/"


        # stiahnem reporty
        ret.append(f"project: {report['project']}, report: {report['name']}, pdf: {report['pdf']}, html: {report['html']}")
        print(f"check {cloud_path=}")
        if not cloud.cloud_check_path(cloud_path):
            print(f"vytvaram priecinok na cloude {cloud_path=}")
            try:
                cloud.cloud_make_path(cloud_path)
            except Exception as error:
                print("An error occurred:", error) # An error occurred: name 'x' is not defined

        print(f"uploadujem subor {disk_path + report['name'] + '.pdf'}")
        cloud.cloud_report_upload(cloud_path + report['name'] + ".pdf",disk_path + report['name'] + ".pdf")
        #cloud.cloud_report_upload("martin.varga", cloud_path + report['name'] + ".html",disk_path + report['name'] + ".html")

    return ret

def if_not_dir_create(path):
    if not os.path.exists(os.path.dirname(path)):
        # If the folder does not exist, create it
        os.makedirs(os.path.dirname(path))
        #os.makedirs(os.path.dirname(report_path), exist_ok=True)

def down_up_reps(report_path: str):
    if_not_dir_create(report_path)
    print("generujem reporty")
    reports = generate_all_reports(report_path)
    print("Writeing reports metadata to file")
    meta_path = report_path + "meta/" + time_folder() + ".json"
    if_not_dir_create(meta_path)
    write_reports_to_file(reports, meta_path)
    # 1800sec is a half of hour to waint, so I am certain, all reports are generated
    sec = 300
    print(f"cakam {sec} secundes")
    time.sleep(sec)
    print("stahujem reporty")
    download_all_reports(reports, report_path)
    print("uploadujem reporty")
    dr = upload_reports(reports, report_path)
    #pprint(dr)


if __name__ == "__main__":
    report_path = "/home/kveti/reporty/"
    down_up_reps(report_path)
