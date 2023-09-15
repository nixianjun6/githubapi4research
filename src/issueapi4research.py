import os
import json
import requests
import urllib3
from githubapi4research import GithubAPI4Research

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class IssueAPI4Research(GithubAPI4Research):
    def get(self, start_time=None, end_time=None, checkpoint=200, author=None):
        try:
            json_list = []
            index = 0

            if os.path.exists(f"{self.to_dir}/{self.repo_name}IssueIndexTmp.log"):
                with open(f"{self.to_dir}/{self.repo_name}IssueIndexTmp.log") as fp:
                    index = int(fp.readline())

            while True:
                if author == None:
                    response = requests.get(url="https://api.github.com/repos/{}/{}/issues?state=all&per_page=100&page={}".format(self.repo_owner, self.repo_name, index), headers={'Authorization': 'token {}'.format(self.api_token)}, verify=False)
                else:
                    response = requests.get(url="https://api.github.com/repos/{}/{}/issues?state=all&per_page=100&page={}&author={}".format(self.repo_owner, self.repo_name, index, author), headers={'Authorization': 'token {}'.format(self.api_token)}, verify=False)
                response.raise_for_status()
                if response.status_code == requests.codes.ok:
                    response_json_list = response.json()
                    if len(response.json()) > 0:
                        json_list = json_list + response_json_list
                        index += 1
                    else:
                        print("Get all Issues successfully") 
                        break
                else:
                    print("Stop to get Issues due to {}".format(response.text))
                    break
                
                if index != 0 and index % checkpoint == 0:
                    with open(f"{self.to_dir}/{self.repo_name}IssueIndexTmp.log", "w", encoding='utf-8') as fp:
                        fp.write(str(index))

                    with open(f"{self.to_dir}/{self.repo_name}IssueTmp.json", "a", encoding='utf-8') as fp:
                        json.dump(json_list, fp=fp, indent=4)
                        json_list = []
            
            if os.path.exists(f"{self.to_dir}/{self.repo_name}IssueIndexTmp.log"):
                os.remove(f"{self.to_dir}/{self.repo_name}IssueIndexTmp.log")
            
            if os.path.exists(f"{self.to_dir}/{self.repo_name}IssueTmp.json"):
                os.remove(f"{self.to_dir}/{self.repo_name}IssueTmp.json")
        
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)