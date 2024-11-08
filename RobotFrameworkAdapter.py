import os
import sys
import subprocess
import glob
#import pymysql.cursors
from shutil import copyfile, which
from datetime import datetime
from pathlib import Path
import xml.etree.ElementTree as ET
import argparse

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

def get_log_timestamp(path_results: str, ts: str = None):
    # Get execution datetime from output file
    if ts != None:
        ts_name = ts.split('.robot')[0] + "_"
    else:
        ts_name = ""
    tree = ET.parse(f"{path_results}/{ts_name}output.xml")
    root = tree.getroot()
    try:
        exe_datetime = root.attrib['generated']
    except Exception:
        print_to_terminal("Sir, It seems something went wrong. I can't find the execution datetime of the last test run.")

    # Split execution datetime
    if 'T' in exe_datetime:
        exe_time = exe_datetime.split('T')[1] # 2024-02-27T10:47:23.922483 T oddeluje datum a cas
        exe_date = exe_datetime.split('T')[0]
    else:
        exe_time = exe_datetime.split()[1] # 2024-02-27T10:47:23.922483 T oddeluje datum a cas
        exe_date = exe_datetime.split()[0]

    if "-" not in exe_date:
        new_date = exe_date[:4] + "-" + exe_date[4:6] + "-" + exe_date[6:]
        exe_date = new_date

    # Format execution time
    exe_time = ''.join(exe_time.split(':'))
    exe_time = exe_time.split('.')[0]

    # Join execution time and date
    exe_datetime = '-'.join([exe_date, exe_time])
    
    return exe_datetime


def get_screenshots(path_results: str, ts: str = None):
    if ts != None:
        ts_name = ts.split('.robot')[0] + "_"
    else:
        ts_name = ""

    if not os.path.exists(f"{path_results}/{ts_name}output.xml"):
        raise Exception(f"Sir, I'am unable to locate the file '{path_results}/{ts_name}output.xml'")

    with open(f"{path_results}/{ts_name}output.xml", encoding='utf-8') as log:
        read_data = log.read()

    words = read_data.split('"')
    screen_names = set([word for word in words if word.startswith('selenium-screenshot-')])

    return screen_names


def get_target_path(subfolder):
    path_list = os.getcwd().split('\\')


    removed = None
    while (removed != 'automaticke' and removed != 'API') and len(path_list) != 0:
        removed = path_list.pop()
    
    if len(path_list) == 0:
        raise Exception("Sir, I can't the find the folder 'automaticke'. It seems you don't have the correct folder tree.")
    
    today = datetime.now()
    month = today.strftime('%m')
    year = today.strftime('%Y')
    project_root_path = '\\'.join(path_list)
    target_path = f"{project_root_path}\\logy\\{year}_{month}\\{subfolder}\\"
    
    return target_path


def get_last_screenshot_num(target_path: str):
    if os.path.exists(target_path):
        listed_files = os.listdir(target_path)
        screenshots = [file_name for file_name in listed_files if 'screenshot' in file_name]
        screen_numbers = [int(screenshot.split('-')[-1].split('.')[0]) for screenshot in screenshots]
        last_screen_num = max(screen_numbers) if len(screen_numbers) > 0 else 0
    else:
        last_screen_num = 0

    return last_screen_num

def get_screenshots_names_obj(path_results: str, target_path: str, ts: str = None):
    screen_num = get_last_screenshot_num(target_path)+1
    if ts != None:
        screen_names = list(get_screenshots(path_results, ts))
    else:
        screen_names = list(get_screenshots(path_results))
    screen_names.sort()

    screen_names_final = []
    for screen_name in screen_names:
        screen_names_final.append({'old': screen_name, 'new': f"selenium-screenshot-{screen_num}.png" })
        screen_num += 1

    return screen_names_final


def rename_screenshots_in_log(path, screenshots):
    ret = []
    if not os.path.exists(path):
        raise Exception(f"Sir, path '{path}' does not exist.")

    with open(path, encoding='utf-8') as log:
        file_text = log.read()

    for screenshot in screenshots:
        file_text = file_text.replace(screenshot['old'], screenshot['new'])
        ret.append({"old": screenshot['old'], "new": screenshot['new']})
    
    with open(path, 'w', encoding='utf-8') as log:
        log.write(file_text)

    return ret


def get_test_name(dir_to_run):
    path_list = os.getcwd().split('\\')

    removed = None
    while removed != 'automaticke' and len(path_list) != 0:
        removed = path_list.pop()

    root_folder = path_list[-1]
    test_name = f"{root_folder}_{dir_to_run}"

    return test_name


class RobotFrameworkAdapter():

    def __init__(self, dir_to_run):
        # Object variables
        self.dir_to_run = dir_to_run
        self.path_results = f"{self.dir_to_run}/Results"
        self.path_tests = f"{self.dir_to_run}/*.robot"




    #-------------------#
    # GETTERS & SETTERS #
    #-------------------#
    @property
    def dir_to_run(self):
        return self.__dir_to_run
    
    @dir_to_run.setter
    def dir_to_run(self, dir_to_run):
        # Check if dir_to_run exists
        pwd = os.getcwd()
        listed_dirs = os.scandir(pwd)
        dirs = [directory.name for directory in listed_dirs]

        dirs_to_run = dir_to_run.split(os.path.sep)
        #print(dirs_to_run)
        #print("len of dirs_to_run: ")
        #print(len(dirs_to_run))
        if len(dirs_to_run) == 1:
            if dir_to_run not in dirs:
                sys.tracebacklimit = 0
                raise Exception(f"Im'sorry Sir, I can't find directory 1 {dir_to_run}.")
        elif len(dirs_to_run) == 2:
            if dirs_to_run[0] not in dirs:
                sys.tracebacklimit = 0
                raise Exception(f"Im'sorry Sir, I can't find directory 2 {dir_to_run}.")
            listed_dirs = os.scandir(os.path.join(pwd, dirs_to_run[0]))
            dirs = [directory.name for directory in listed_dirs]
            if dirs_to_run[1] not in dirs:
                sys.tracebacklimit = 0
                raise Exception(f"Im'sorry Sir, I can't find directory 3 {dir_to_run}.")
        elif len(dirs_to_run) == 3:
            if dirs_to_run[0] not in dirs:
                sys.tracebacklimit = 0
                raise Exception(f"Im'sorry Sir, I can't find directory 4 {dir_to_run}.")
            listed_dirs = os.scandir(os.path.join(pwd, dirs_to_run[0]))
            dirs = [directory.name for directory in listed_dirs]
            if dirs_to_run[1] not in dirs:
                sys.tracebacklimit = 0
                raise Exception(f"Im'sorry Sir, I can't find directory 5 {dir_to_run}.")
            listed_dirs = os.scandir(os.path.join(pwd, dirs_to_run[0], dirs_to_run[1]))
            dirs = [directory.name for directory in listed_dirs]
            if dirs_to_run[2] not in dirs:
                sys.tracebacklimit = 0
                raise Exception(f"Im'sorry Sir, I can't find directory 6 {dir_to_run}.")
        else:
            sys.tracebacklimit = 0
            raise Exception(f"Im'sorry Sir, I can't find directory 7 {dir_to_run}.")
        self.__dir_to_run = dir_to_run
    

    @property
    def path_tests(self):
        return self.__path_tests
    
    @path_tests.setter
    def path_tests(self, path_tests):
        # Check if there are any test-*.robot files in dir_to_run directory
        files = glob.glob(path_tests)
        if len(files) == 0:
            sys.tracebacklimit = 0
            raise Exception(f"Sir, I didn't find any correctly named tests to run in folder {self.dir_to_run}.")
        
        self.__path_tests = path_tests
        

    @property
    def local_mode(self):
        return self.__local_mode

    @local_mode.setter
    def local_mode(self, local_mode):
        if local_mode == True:
            self.__local_mode = True
        else:
            self.__local_mode = False
    

    @property
    def path_results(self):
        return self.__path_results

    @path_results.setter
    def path_results(self, path_results):
        self.__path_results = path_results 




    #---------#
    # METHODS #
    #---------#




    def clear_local_results_folder(self):
        files = glob.glob(self.path_results+"/*")
        #print_to_terminal(f"Sir, 1. of all I'm DELETING {len(files)} LOG FILES FROM PREVIOUS RUN.")
        for f in files:
            os.remove(f)

    #subprocess.call(['c:\\python3.11\\Scripts\\pipenv.exe', '--python', 'c:\\python3.11\\python.exe', 'run', 'robot', '-d', self.path_results, '-o', f"{test_suite_name}_output.xml", '-l', f"{test_suite_name}_log.html", '-r', f"{test_suite_name}_report.html",  f"{self.dir_to_run}/{test_suite}"])
    #subprocess.call(['robot', '-d', self.path_results, '-o', f"{test_suite_name}_output.xml", '-l', f"{test_suite_name}_log.html", '-r', f"{test_suite_name}_report.html",  f"{self.dir_to_run}/{test_suite}"])
    #subprocess.call(['pipenv', '--python', 'c:\\python3.11\\python.exe', 'run', 'robot', '-d', self.path_results, '-o', f"{test_suite_name}_output.xml", '-l', f"{test_suite_name}_log.html", '-r', f"{test_suite_name}_report.html",  f"{self.dir_to_run}/{test_suite}"])
    #subprocess.call([which('pipenv'), '--python', 'c:\\python3.11\\python.exe', 'run', 'robot', '-d', self.path_results, '-o', f"{test_suite_name}_output.xml", '-l', f"{test_suite_name}_log.html", '-r', f"{test_suite_name}_report.html",  f"{self.dir_to_run}/{test_suite}"])
    #subprocess.call([which('pipenv'), '--python', 'C:\\Users\\teste\\AppData\\Local\\Programs\\Python\\Python311\\python.exe', 'run', 'robot', '-d', self.path_results, '-o', f"{test_suite_name}_output.xml", '-l', f"{test_suite_name}_log.html", '-r', f"{test_suite_name}_report.html",  f"{self.dir_to_run}/{test_suite}"])
    #C:\Users\Simon\.virtualenvs\NEW-VERSION-x-d1Ht35\Scripts\python.exe test_all.py
    #
    # potrebujem aby mi to vrátilo zopár vecí
    # cesty log súborov
    # true / false výsledok
    # testy a ich vysledky, možno aj trvanie
    # poruchy? (malfunction)
    def run(self, test_suite: str = None):
        if test_suite:
            test_suite_name = test_suite.split('.robot')[0] + "_"
        else:
            test_suite_name = ""
        # pôvodný spôsob
        #subprocess.call(['pipenv', 'run', 'robot', '-d', self.path_results, '-o', f"{test_suite_name}_output.xml", '-l', f"{test_suite_name}_log.html", '-r', f"{test_suite_name}_report.html",  f"{self.dir_to_run}/{test_suite}"])
        
        if test_suite:
            cmd = f"pipenv run robot -d {self.path_results} -o {test_suite_name}output.xml -l {test_suite_name}log.html -r {test_suite_name}report.html {self.dir_to_run}/{test_suite}"
        else:
            cmd = f"pipenv run robot -d {self.path_results} {self.dir_to_run}"
        result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
        
        ## Print the standard output (stdout)
        #print(result.stdout)        
        ## Print the standard error output (stderr)
        #print(result.stderr)


        #------------------------------------------------------------------------------
        #Test-Crs                                                             | FAIL |
        #12 tests, 1 passed, 11 failed
        #==============================================================================
        #Output:  C:\testy\dev_crs\automaticke\webapp\Results\test-crs_output.xml
        #Log:     C:\testy\dev_crs\automaticke\webapp\Results\test-crs_log.html
        #Report:  C:\testy\dev_crs\automaticke\webapp\Results\test-crs_report.html
        

        lines = result.stdout.split('\n')
        
        length = len(lines) - 1
        ret = {
            "log_files": {
                "report": "nic",
                "log": "nic",
                "output": "nic"
            },
            "NOT": "nic",
            "status": "nic",
            "stdout": [],
            "stderr": [],
            "exit_code": 0
            }

        if len(lines) > 3:
            ret["log_files"]["report"] = lines[length-1].split(' ')[-1] # Report
            ret["log_files"]["log"] = lines[length-2].split(' ')[-1] # Log
            ret["log_files"]["output"] = lines[length-3].split(' ')[-1] # Output

        if len(lines) > 5:
             ret["NOT"] = lines[length-5]

        if len(lines) > 6:
            ret["status"] = lines[length-6]

        ret["stdout"] = lines
        ret["stderr"] = result.stderr.split('\n')
        ret["exit_code"] = result.returncode

        return ret

        return ret


    def get_test_results(self):
        tree = ET.parse(f"{self.path_results}/output.xml")
        root = tree.getroot()

        try:
            test_stats = root.findall("./statistics/total/stat")[0].attrib
        except Exception as e:
            print_to_terminal("Sir, It seems something went wrong. I can't find the statistics of the last test run.")
            print_to_terminal(e)
        
        try:
            test_name = [t_name.attrib for t_name in root.findall("./suite/suite/test")]                        
        except Exception as e:
            print_to_terminal("Sir, It seems something went wrong. I can't find the names of the last test run.")
            print_to_terminal(e)
            
        try:
            test_name2 = [test.attrib for t_name in root.findall("./suite/suite") for test in t_name.findall("./test")]                        
        except Exception as e:
            print_to_terminal("Sir, It seems something went wrong. I can't find the names of the last test run.")
            print_to_terminal(e)

        try:
            test_status = [t_status.attrib for t_status in root.findall("./suite/suite/test/status")]
        except Exception as e:
            print_to_terminal("Sir, It seems something went wrong. I can't find the statuses of the last test run.")
            print_to_terminal(e)

        try:
            test_suites = [t_status.attrib for t_status in root.findall("./suite/suite/")]
        except Exception as e:
            print_to_terminal("Sir, It seems something went wrong. I can't find the statuses of the last test run.")
            print_to_terminal(e)

        try:
            test_suites_status = [t_status.attrib for t_status in root.findall("./statistics/suite/stat")]
        except Exception as e:
            print_to_terminal("Sir, It seems something went wrong. I can't find the statuses of the last test run.")
            print_to_terminal(e)
              
        
        return {"test_names": test_name, "test_name_2": test_name2, "test_statuses": test_status, "test_suites": test_suites, "test_suites_status": test_suites_status, "test_stats": test_stats}


    def evaluate_test_results(self): # pravdepodobne nepotrebna funkcia, mozno pouzielna len na failnutie buildu v pripade fail testu.
        test_results = self.get_test_results()
        
        #if int(test_results['fail']) > 0:
        #    sys.tracebacklimit = 0
        #    raise Exception(f"I'm throwing an exception to fail the build in jenkins.")
        return test_results

    def copy_log_files(self, ts: str = None):
        ret = {}
        if ts:
            ts_name = ts.split('.robot')[0] + "_"
        else:
            ts_name = ""
        log_timestamp = get_log_timestamp(self.path_results, ts)
        logs = [f"{ts_name}log.html", f"{ts_name}report.html", f"{ts_name}output.xml"]
        source_path = os.getcwd()+"\\"+self.path_results.replace('/', '\\')+"\\"
        target_path = get_target_path(self.path_results.split('/')[0])
        screenshots = get_screenshots_names_obj(self.path_results, target_path, ts)

        if not os.path.exists(target_path):
            Path(target_path).mkdir(parents=True, exist_ok=True)

        # Kopirovanie screenshotov
        for screenshot in screenshots:
            if not os.path.exists(source_path+screenshot['old']):
                raise Exception(f"Sir, I'm unable to copy the file '{source_path+screenshot['old']}'. It seems the file does not exist.")
            copyfile(source_path+screenshot['old'], target_path+screenshot['new'])

        # Kopirovanie logov + uprava logov v Results zlozke
        for idx, log in enumerate(logs):
            if not os.path.exists(source_path+log):
                raise Exception(f"Sir, I'm unable to copy the file '{source_path+log}'. It seems the file does not exist.")
                
            file_name_with_timestamp = f"{log_timestamp}-{log}"  #log.replace(".", f"-{log_timestamp}.")
            # print(file_name_with_timestamp)
            copyfile(source_path+log, target_path+file_name_with_timestamp)
            #print_to_terminal("from: " + source_path+log)
            #print_to_terminal(" to : " + target_path+file_name_with_timestamp)
            ret[idx] = {"from": source_path+log, "to": target_path+file_name_with_timestamp}
            # os.rename(source_path+log, source_path+vanilla_log_file_name)  # Premenovanie logu na nazov bez timestampu, kvoli jenkinsu
            rename = rename_screenshots_in_log(target_path+file_name_with_timestamp, screenshots) # Premenovanie screenshotov, aby nevznikali kolizie s predoslymi screenshotmi
            ret[idx]["rename_screenshots_in_log"] = rename
        return ret

    def get_suites_in_dir(self):
        files = os.listdir(self.dir_to_run)
        test_suites = []
        for file in files:
            if file.endswith('robot'):
                test_suites.append(file)
        return test_suites

    def upload_results_to_db(self):
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
        

    def merge_outputs(self):
        path = os.getcwd()+"\\"+self.path_results.replace('/', '\\')+"\\*.xml"
        cmd = f"rebot --outputdir {self.path_results} --output output.xml {path}"
        
        result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
        
        stdout = result.stdout.split('\n')
        stderr = result.stderr.split('\n')
        exit_code = result.returncode

        return {"stdout": stdout, "stderr": stderr, "exit": exit_code, "path": f"{self.path_results}\\output.xml"}


    def stary_tr_upload_results(self):
        print("Sir, I am UPLOADING RESULTS TO THE TEST RAIL.")

        # pipenv run rebot -x .\webapp-mail\Results\junit.xml .\webapp-mail\Results\output-20231206-184950.xml

        # trcli -y -c c:\testy\global_assets\trcli_config.yaml -f ".\webapp-mail\Results\junit.xml"
        # trcli -y -c ..\..\global_assets\trcli_config.yaml --project "PrihlaskaVS" parse_robot -f ".\webapp-mail\Results\junit.xml" --title "webmail"
        # trcli -y -c ..\..\global_assets\trcli_config.yaml --project "PrihlaskaVS" parse_robot -f ".\webapp-mail\Results\output.xml" --title "webmail"

        of = f".\\{self.dir_to_run}\\Results\\output.xml"
        print("toto je output file: " + of)

        subprocess.call([which('trcli'), '-y', '-c', 'c:\\testy\\global_assets\\trcli_config.yaml', '--project', self.project, 'parse_robot', '-f', of, '--title', self.title])

        print_to_terminal("")
        print_to_terminal(f"Sir, the tests are done.")



    def tr_upload_results(self):
        print("Sir, I am UPLOADING RESULTS TO THE TEST RAIL.")

        # pipenv run rebot -x .\webapp-mail\Results\junit.xml .\webapp-mail\Results\output-20231206-184950.xml

        # trcli -y -c c:\testy\global_assets\trcli_config.yaml -f ".\webapp-mail\Results\junit.xml"
        # trcli -y -c ..\..\global_assets\trcli_config.yaml --project "PrihlaskaVS" parse_robot -f ".\webapp-mail\Results\junit.xml" --title "webmail"
        # trcli -y -c ..\..\global_assets\trcli_config.yaml --project "PrihlaskaVS" parse_robot -f ".\webapp-mail\Results\output.xml" --title "webmail"

        of = f".\\{self.dir_to_run}\\Results\\output.xml"
        print("toto je output file: " + of)

        #subprocess.call([which('trcli'), '-y', '-c', 'c:\\testy\\global_assets\\trcli_config.yaml', '--project', self.project, 'parse_robot', '-f', of, '--title', self.title])

        
        cmd = f"trcli -y -c c:\\testy\\global_assets\\trcli_config.yaml --project {self.project} parse_robot -f {of} --title {self.title}"
        
        result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
        
        stdout = result.stdout.split('\n')
        stderr = result.stderr.split('\n')
        exit_code = result.returncode

        return [stdout, stderr, exit_code]
