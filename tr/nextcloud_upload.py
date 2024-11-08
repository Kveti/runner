import requests
import datetime

G_USERNAME = ''
G_PASSWORD = ''
G_USER = ''
G_FOLDER = 'PROJEKTY'
 
def cloud_check_path(path: str):
    # Nextcloud API endpoint and folder path
    nextcloud_url = 'https://cloud.maurit.sk/remote.php/dav/files/' + G_USER + '/' + G_FOLDER + '/' + path
    
    # Nextcloud credentials
    username = G_USERNAME
    password = G_PASSWORD
    
    # Send a PROPFIND request to check if the folder exists
    response = requests.request('PROPFIND', nextcloud_url, auth=(username, password))
    
    if response.status_code == 207:
        print("Folder exists at", path)
        return True
    else:
        print("Folder does not exist at", path)
        return False


def cloud_make_path(path: str):
    # Nextcloud credentials and API endpoint
    username = G_USERNAME
    password = G_PASSWORD
    nextcloud_url = 'https://cloud.maurit.sk/remote.php/dav/files/' + G_USER + '/' + G_FOLDER + '/' + path
    response = requests.request('MKCOL', nextcloud_url, auth=(username, password))
    if response.status_code == 201:
        print("Folder created successfully")
    else:
        print("Folder creation failed. Status code:", response.status_code)
        print("Response:", response.text)

def cloud_report_upload(path: str, pdf: str):
    # Nextcloud credentials and API endpoint
    username = G_USERNAME
    password = G_PASSWORD
    nextcloud_url = 'https://cloud.maurit.sk/remote.php/dav/files/' + G_USER + '/' + G_FOLDER + '/' + path
    # Read file content
    with open(pdf, 'rb') as file:
        file_content = file.read()
    # Perform the WebDAV PUT request to upload the file
    response = requests.put(nextcloud_url, auth=(username, password), data=file_content)
    # if response is ok
    if response.status_code == 201:
        print("File uploaded successfully.")
    elif response.status_code == 405:
        print("Method NOT Allowed.")
    else:
        print("File upload failed. Status code:", response.status_code)




if __name__ == "__main__":
    current_date = datetime.datetime.now()
    month_name = str(current_date.year) + "." + '{:02d}'.format(current_date.month)
    path = "Uznavanie/REPORTY/" + month_name + "/"
    if not cloud_check_path(path):
        cloud_make_path(path)
    cloud_report_upload(path + "local_file.txt","./local_file.txt")
