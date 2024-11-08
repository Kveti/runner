import os
import json
from datetime import datetime

def save_json(data: dict, path: str):
    with open(path, 'w') as json_file:
        json.dump(data, json_file, indent=4)


def console_name(log_target_path: str) -> str:
    # Get the current date and time
    current_datetime = datetime.now()
    timestamp = current_datetime.strftime("%Y-%m-%d-%H%M%S")

    # Split path of log time for path
    target_path, log_file_name = os.path.split(log_target_path)
    
    # Add timestamp to console file
    target_path += "\\" + timestamp + "-console.json"
    return target_path

"""
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
.collapsible {
  background-color: #777;
  color: white;
  cursor: pointer;
  padding: 18px;
  width: 100%;
  border: none;
  text-align: left;
  outline: none;
  font-size: 15px;
}

.active, .collapsible:hover {
  background-color: #555;
}

.content {
  padding: 0 18px;
  display: none;
  overflow: hidden;
  background-color: #f1f1f1;
}
</style>
</head>
<body>

<h2>Collapsibles</h2>

<p>A Collapsible:</p>
<button type="button" class="collapsible">Open Collapsible</button>
<div class="content">
  <p>Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p>
</div>

<p>Collapsible Set:</p>
<button type="button" class="collapsible">Open Section 1</button>
<div class="content">
  <p>Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p>
</div>
<button type="button" class="collapsible">Open Section 2</button>
<div class="content">
  <p>Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p>
</div>
<button type="button" class="collapsible">Open Section 3</button>
<div class="content">
  <p>Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p>
</div>

<script>
var coll = document.getElementsByClassName("collapsible");
var i;

for (i = 0; i < coll.length; i++) {
  coll[i].addEventListener("click", function() {
    this.classList.toggle("active");
    var content = this.nextElementSibling;
    if (content.style.display === "block") {
      content.style.display = "none";
    } else {
      content.style.display = "block";
    }
  });
}
</script>

</body>
</html>
"""
def console_to_array(json: str) -> list:
    blocs = []
    for point in json["sequence"]:
        blocs.append(json[point])

    return blocs




# BLOKY
#
#"sequence": [
#        "1. pipenv list",
#        "2. test_folder",
#        "3. test suites list",
#        "4. Sir, I am cleaning result folder",
#        "5. test_suite v cykle spustim jednotlive test suity",
#        "6. mergnem output subory jednotlivych test suitov do jednoho vysledneho",
#        "7. skopirujem do log priecinka vysledne merge logy",
#        "9. evalueate test results"
#    ],
#
#"sequence": [
#        "pipenv list",
#        "test_folder",
#        "3. test suites list",
#        "4. Sir, I am cleaning result folder",
#        "5. test_suite v cykle spustim jednotlive test suity",
#        "6. mergnem output subory jednotlivych test suitov do jednoho vysledneho",
#        "7. skopirujem do log priecinka vysledne merge logy",
#        "9. evalueate test results"
#    ],
#
#1. json["pipenv_list"]["pkgs"] (zoznam balickov)
#2. vseobecne
#        json["test_folder"]
#        json["test_suites_list"]
#        json["4"] = "4. Sir, I am cleaning result folder",
#
#3. cyklus s test suite testami
#        run
#        merge
#        copy
#        a tieto veci
#
#4. zapis do db
#5. upload do db
#