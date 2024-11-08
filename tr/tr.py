


#
#  HOW TO USE
#  Z terminalu spusti "pipenv run python runner.py -h"
#


def print_to_terminal(message):
    subprocess.call(['echo', message], shell=True)

def tr_upload_results(project, title, upload_file):
    #print("Sir, I am UPLOADING RESULTS TO THE TEST RAIL.")

    # pipenv run rebot -x .\webapp-mail\Results\junit.xml .\webapp-mail\Results\output-20231206-184950.xml

    # trcli -y -c c:\testy\global_assets\trcli_config.yaml -f ".\webapp-mail\Results\junit.xml"
    # trcli -y -c ..\..\global_assets\trcli_config.yaml --project "PrihlaskaVS" parse_robot -f ".\webapp-mail\Results\junit.xml" --title "webmail"
    # trcli -y -c ..\..\global_assets\trcli_config.yaml --project "PrihlaskaVS" parse_robot -f ".\webapp-mail\Results\output.xml" --title "webmail"

    #of = f".\\{self.dir_to_run}\\Results\\output.xml"
    #print("toto je output file: " + of)

    #subprocess.call([which('trcli'), '-y', '-c', 'c:\\testy\\global_assets\\trcli_config.yaml', '--project', project, 'parse_robot', '-f', upload_file, '--title', title])
    subprocess.call(['trcli', '-y', '-c', 'c:\\testy\\global_assets\\trcli_config.yaml', '--project', project, 'parse_robot', '-f', upload_file, '--title', title])

    #print_to_terminal("")
    #print_to_terminal(f"Sir, the tests are done.")

def druha(nieco):
    print("pisem ti nieco: " + nieco)
