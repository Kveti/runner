import os
import sys
import subprocess
import glob
import json
#import pymysql.cursors
from shutil import copyfile, which
from datetime import datetime
from pathlib import Path
import xml.etree.ElementTree as ET
import argparse
from tr import test_rail_wrapper as trw
from tr import nextcloud_upload as cloud
from RobotFrameworkAdapter import RobotFrameworkAdapter as Adapter
from pprint import pprint
from mail.email_notifier import send_email_notification as send_mail
from console import consoleFile

# sys.tracebacklimit = 0

#
#  HOW TO USE
#  Z terminalu spusti "pipenv run python runner.py -h"
#

#------------------#
# HELPER FUNCTIONS #
#------------------#

def print_to_terminal(message):
    subprocess.call(['echo', message], shell=True)


def parse_arguments():
    parser = argparse.ArgumentParser(description='Script to run robot framework tests')
    parser.add_argument('-d', '--database', action='store_true', help='If this flag is used, test results will NOT be copied into "logy" folder and will NOT be uploaded to database.')
    parser.add_argument('tests_folder', nargs='?', help='Name of the folder containing tests you want to run.')
    parser.add_argument('-p', '--project', action='store', help='Name of project for test rail upload.')
    parser.add_argument('-t', '--title', help='Title of results uploading into test rail.')
    parser.add_argument('-r', '--results', action='store_true', help='If this flag is used, test results will be uploaded to test rail.')
    parser.add_argument('-s', '--single', action='store_true', help='If this flag is used, all test suites will be launch in one run')
    parser.add_argument('-n', '--notification', action='store_true', help='If this flag is used, there will be email notifications')
    parser.add_argument('-o', '--reports', action='store_true', help='If this flag is used, there will be email notifications')

    args = parser.parse_args()
    return args


def args_to_dict(args):
    args_dict = vars(args)
    args_list = list(args_dict.items())
    return {sublist[0]: sublist[1] for sublist in args_list}


def trim_tests_folder(tests_folder: str):
    return tests_folder.lstrip(".\\").rstrip("\\")


def upload_results_to_db(test_run: list):
    print_to_terminal("Sir, I am UPLOADING RESULTS TO THE DATABASE...")

    test_results = self.get_test_results()
    log_timestamp = get_log_timestamp(self.path_results)
    test_name = get_test_name(self.dir_to_run)

    log_datetime = datetime.strptime(log_timestamp, '%Y%m%d-%H%M%S')
    log_datetime_str = log_datetime.strftime('%Y-%m-%d %H:%M:%S')  # Format ktoremu bude rozumiet SQL

    # Connect to the database
    connection = pymysql.connect(host='localhost',
                                 user='teresa',
                                 password='Etfx2y20i1Zw',
                                 database='teresa',
                                 cursorclass=pymysql.cursors.DictCursor)

    with connection:
        with connection.cursor() as cursor:
            # Create a new record
            sql = "INSERT INTO `results` (`test_name`, `cases_failed`, `cases_passed`, `test_datetime`) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (test_name, test_results['fail'], test_results['pass'], log_datetime_str))

        # connection is not autocommit by default. So you must commit to save your changes.
        connection.commit()
        
        print_to_terminal(f"Results successfully uploaded to the databse with name {test_name}.")


def tab_to_dict(tab: list[str]) -> dict:
    pkgs = {}
    idx = 0
    for row in tab:
        if idx < 2:
            idx += 1
            continue
        pkg = [word for word in row.split(" ") if word]
        if pkg != []:
            pkgs[pkg[0]] = pkg[1]
    return pkgs


def pipenv_list():
    cmd = "pipenv run pip list"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.returncode == 0:
        out = result.stdout.split("\n")
        err = result.stderr.split("\n")
        status = result.returncode
        pkgs = tab_to_dict(out)
        ret = {"stdout": out, "stderr": err, "return_code": status, "pkgs": pkgs}
        return ret

    else:
        out = result.stdout.split("\n")
        err = result.stderr.split("\n")
        status = result.returncode
        #pkgs = tab_to_dict(out)
        ret = {"stdout": out, "stderr": err, "return_code": status}
        return ret



def suites_tests(testy: list, statuses: list, test_results: list) -> list:
    ret = []
    r = 0;

    for test in testy:
        if "id" not in test:
            continue

        for idx, stat in enumerate(statuses):
            if idx == 0:
                continue

            row = []
            
            if stat["id"] in test["id"]:
                row.append(stat["name"])
                row.append(test["name"])
                #row.append(list(test_results[r].items()))
                #row.append(list(test_results[r].values()))
                #{"status": "PASS", "start": "2024-05-10T01:15:55.610639", "elapsed": "12.197204"},
                row.append(test_results[r]["status"])
                if 'start' in test_results[r]:
                    row.append(test_results[r]["start"])
                if 'elapsed' in test_results[r]:
                    row.append(test_results[r]["elapsed"])
                r += 1
                ret.append(row)
        
    return ret

#"parameters": {
#   "database": false,
#   "tests_folder": "webapp",
#   "project": null,
#   "title": null,
#   "results": false,
#   "single": false,
#   "notification": false,
#   "mail_to": [
#       "Tester <tester@maurit.sk>",
#       "tester@maurit.sk"
#   ]
#}
def run(params) -> list :
    ret = {"parameters": params}
    ret["sequence"] = []
    pkgs = pipenv_list()
    ret["pipenv_list"] = pkgs
    ret["sequence"].append("1. pipenv list")

    if pkgs["return_code"] != 0:
        msg = "Sir, there was a problem with pipenv list"
        print_to_terminal(msg)
        if params["notification"] == True:
            subject = "Teresa - err"
            send_mail(params["mail_to"], subject, msg)

    if params["results"] == True and params["title"] == None:
        #raise Exception(f"Sir, I need you to enter title parameter.")
        msg = "Sir, I need you to enter title parameter."
        print_to_terminal(msg)
        if params["notification"] == True:
            subject = "Teresa - err"
            send_mail(params["mail_to"], subject, msg)
        #
        ret["return_code"] = 2
        return ret

    #if params["results"] == True and len(params["title"]) < len(params["tests_folder"]):
    #    msg = "Sir, I need you to enter same number of titles as test suite folders."
    #    print_to_terminal(msg)
    #    subject = "Teresa - err"
    #    send_mail(params["mail_to"], subject, msg)
    #    #
    #    ret["return_code"] = 3
    #    return ret

    if params["results"] == True and params["project"] == None:
        msg = "Sir, I need you to enter project parameter."
        print_to_terminal(msg)
        if params["notification"] == True:
            subject = "Teresa - err"
            send_mail(params["mail_to"], subject, msg)
        #
        ret["return_code"] = 4
        return ret


    # if tests_folder zacina ".\" a/alebo konci "\" tak to trimnem
    tf = trim_tests_folder(params["tests_folder"])
    ret["test_folder"] = tf
    ret["sequence"].append("2. test_folder")
    # test suite list

    runner = Adapter(tf)
    tss = runner.get_suites_in_dir()
    ret["test_suites_list"] = tss #"Sir, I am getting list of test suites"
    ret["sequence"].append("3. test suites list")
    ret["sequence"].append("4. Sir, I am cleaning result folder")
    runner.clear_local_results_folder()


    if params["single"] == False:
        # Run Process
        ret["test_suite"] = {} #"Sir, I am going to launch tests in test suites"
        ret["sequence"].append("5. test_suite v cykle spustim jednotlive test suity")
        for idx, ts in enumerate(tss):
            ts_ret = {}
            output = runner.run(ts)
            ts_ret["run"] = output
            cpy = runner.copy_log_files(ts)
            ts_ret["copy_logs"] = cpy
            if params["database"] == True:
                test_run = ["projekt", "prostredie", "modul", "test_suite", "test_failed", "test_passed", "duration"]
                upload_results_to_db(test_run)
                ts_ret["db_upload"] = test_run
            if params["results"] == True:
                output_file = ts_ret["copy_logs"][2]["from"]
                tr_ret = trw.tr_upload_results("c:\\testy\\global_assets\\trcli_config.yaml", params["project"], params["title"], output_file)  #runner.tr_upload_results()
                ts_ret["testrail"] = tr_ret
                #ret["sequence"].append("8. Uploadujem vysledny output subor do testrailu")
                #pprint("Sir, I am about to upload the outputs to TestRail ")
                #pprint(out)
                if tr_ret["return_code"] != 0:
                    print("Problem pri testrail uploade! ", ts)
                    ret["return_code"] = 5
                #pprint("Sir, End of uploading the outputs to TestRail")
            ret["test_suite"][ts] = ts_ret
            #runner.clear_local_results_folder()
            # prehodil som poradie lebo evaluate mi vyhodi exception ak najde fail aby vyhodilo jenkins build fail
        ret["merge_outputs"] = runner.merge_outputs()
        ret["sequence"].append("6. mergnem output subory jednotlivych test suitov do jednoho vysledneho")
        ret["merge_outputs"]["copy_merged_outputs"] = runner.copy_log_files()
        ret["sequence"].append("7. skopirujem do log priecinka vysledne merge logy")
        
        evaluate = runner.evaluate_test_results()
        ret["evaluate_test_results"] = evaluate
        # devinu som prepisal na 8
        ret["sequence"].append("8. evalueate test results")

        #print_to_terminal("")
        #print_to_terminal("")
        #print_to_terminal("===========================================================")
        #eval_tab = suites_tests(evaluate["test_suites"], evaluate["test_suites_status"], evaluate["test_statuses"])
        #print(json.dumps(eval_tab, indent=4))
        #print_to_terminal("===========================================================")
        #print_to_terminal("")
        #print_to_terminal("")




        # vytiahol som tento upload od tiaľto a dal som ho do cyklu,
        # lebo keď som uploadoval mergnuty file, ktorý mal TS_01_.. & TS_02_.. & TS_0x
        # tak bol dlhý názov a bol problém s takým uploadom
        #if params["results"] == True:
        #    output_file = ret["copy_merged_outputs"][2]["to"]
        #    tr_ret = trw.tr_upload_results("c:\\testy\\global_assets\\trcli_config.yaml", params["project"], params["title"], output_file)  #runner.tr_upload_results()
        #    ret["testrail"] = tr_ret
        #    ret["sequence"].append("8. Uploadujem vysledny output subor do testrailu")
        #    #pprint("Sir, I am about to upload the outputs to TestRail ")
        #    #pprint(out)
        #    if tr_ret["return_code"] != 0:
        #        print("Problem pri testrail uploade! ")
        #        ret["return_code"] = 5
        #    #pprint("Sir, End of uploading the outputs to TestRail")
        
        if (int(ret["evaluate_test_results"]["test_stats"]["fail"]) > 0) and "return_code" not in ret:
            ret["return_code"] = 1
        elif "return_code" not in ret:
            ret["return_code"] = 0

    else:
        raise Exception("Proces nie je implementovany")
        ## Run Process
        #for i in range(0, len(args.tests_folder)):       
        #    if args.results == True:
        #        runner = Adapter(args.tests_folder[i], args.database, args.project, args.title[i])
        #    else:
        #        runner = Adapter(args.tests_folder[i], args.database, "", "")
        #    #runner.clear_local_results_folder()
        #    runner.run()
        #    runner.stredny_copy_log_files()
        #    if args.database == True:
        #        runner.upload_results_to_db()
        #        #runner.clear_local_results_folder()
        #        # prehodil som poradie lebo evaluate mi vyhodi exception ak najde fail aby vyhodilo jenkins build fail
        #    if args.results == True:
        #        runner.tr_upload_results()
        #    runner.evaluate_test_results()
    return ret


def spracuj_output(output: dict):
    print(json.dumps(output, indent=4))
    console_file_name = consoleFile.console_name(output["merge_outputs"]["copy_merged_outputs"][0]['to'])
    consoleFile.save_json(output, console_file_name)

def test_rail_reporty():
    report_path = "C:\\reporty\\"
    reporty = trw.down_up_reps(report_path)

if __name__ == "__main__":
    adresat = ["Tester <tester@maurit.sk>", "tester@maurit.sk"]
    try:
        args = parse_arguments()
        params = args_to_dict(args)
        params["mail_to"] = adresat
    except:
        msg = "Sir, I need you to enter at least one folder with robot test suite(s)"
        print_to_terminal(msg)
        subject = "Teresa - err"        
        send_mail(adresat, subject, msg)
        exit(1)
#
    pprint(params)
    if params['reports'] == True:
        test_rail_reporty()
    else:
        if params['tests_folder'] == None:
            raise Exception("No folder with tests entered!")
        output = run(params)
        spracuj_output(output)
        exit(output["return_code"])


