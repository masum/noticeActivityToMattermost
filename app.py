# coding:utf-8
 
import argparse
import requests
import datetime
import json
import sys
import os.path
from urlparse import urlparse
import dateutil.parser
from datetime import datetime
from pytz import timezone

parser = argparse.ArgumentParser()
parser.add_argument("url", help="")
parser.add_argument("project", help="")
parser.add_argument("group", help="")
parser.add_argument("id", help="")
parser.add_argument("pw", help="")
parser.add_argument("repository", help="")
parser.add_argument("icon", help="")
parser.add_argument("mattermost", help="")
args = parser.parse_args()

def push(data):
    print "(((((((("
    d = dateutil.parser.parse(data["date"])
    print json.dumps(data, indent=2)
    print str(last) + " < " + str(d)
    if str(last) < str(d):
        print "■ POST Mattermost"
        j = {}
        j["username"] = data["mattermost_post_user"]
        j["icon_url"] = data["mattermost_icon"]
        j["text"] = data["message"]
        body = "payload=" + json.dumps(j)
        print body
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        res = requests.post(args.mattermost, body, headers=headers)
        print res

    print "))))))))"
    return data

def mrlink(id):
    return args.url + args.group + "/" + args.project + "/merge_requests/" + str(id)

def commitlink(id):
    return args.url + args.group + "/" + args.project + "/commits/" + str(id)

def userlink(id):
    return args.url + "/u/" + str(id)

def prjlink():
    return args.url + args.group + "/" + args.project

def grouplink():
    return args.url + "/groups/" + args.group

def format_mergerequest(mr):
    data = {}
    a = "---------------- \n"
    a+= "### MergeRequest / [" + args.project + "](" + prjlink() + ")\n\n"
    a+= "| | |\n"
    a+= "|--|--|\n"
    #a+= "| Type | Merge Request |\n"
    a+= "| Project | [" + args.group + "](" + grouplink() + ") / [" + args.project + "](" + prjlink() + ") |\n"
    a+= "| Title | [" + mr["title"].strip() + "](" + mrlink(mr["iid"]) + ") |\n"
    a+= "| Source Branch | [" + mr["source_branch"] + "](" + commitlink(mr["source_branch"]) +") |\n"
    a+= "| Target Branch | [" + mr["target_branch"] + "](" + commitlink(mr["target_branch"])+ ") |\n"
    a+= "| Status | " + mr["state"] + " |\n"
    a+= "| User | [" + mr["author"]["name"] + "](" + userlink(mr["author"]["username"]) + ") |\n"
    a+= "| Date | " + mr["updated_at"] + " |  \n"
    a+= mr["description"]
    data["message"] = a
    data["mattermost_post_user"] = "MergeRequest 【" + args.project + "】"
    data["mattermost_icon"] = args.icon
    data["date"] = mr["updated_at"]
    return data

def format_commit(cm, br):
    data = {}
    a = "---------------- \n"
    a+= "### Commit / [" + args.project + "](" + prjlink() + ")\n\n"
    a+= "| | |\n"
    a+= "|--|--|\n"
    #a+= "| Type | Commit |\n"
    a+= "| ID | [" + cm["id"] + "](" + commitlink(cm["id"]) + ") |\n"
    a+= "| Project | [" + args.group + "](" + grouplink() + ") / [" + args.project + "](" + prjlink() + ") |\n"
    a+= "| Title | " + cm["title"].strip() + " |\n"
    a+= "| Branch | " + br["name"] + " |\n"
    a+= "| User | " + cm["author_name"] + " |\n"
    a+= "| Date | " + cm["created_at"] + " |  \n"
    a+= cm["message"]
    data["message"] = a
    data["mattermost_post_user"] = "Commit 【" + args.project + "】"
    data["mattermost_icon"] = args.icon
    data["date"] = cm["created_at"]
    return data
    
filename = args.project + ".txt"
last = "2015-09-08T15:30:33.000+09:00"
if os.path.isfile(filename):
    f = open(filename)
    l = f.readline()
    last = dateutil.parser.parse(l)
    f.close()


#---------------------------------------------------------
# GitLabトークン取得
#---------------------------------------------------------
print ">>> token取得"
url = args.url + "/api/v3/session"
print "  url : " + url
param = "login=%s&password=%s" % (args.id, args.pw)
res = requests.post(url, param)
token = res.json().get("private_token")
print "  token=" + token
print ""

#---------------------------------------------------------
# プロジェクト名からプロジェクトIDを求める
#---------------------------------------------------------
print ">>> projectID検索 : project_name = " + args.project
url = args.url + "/api/v3/projects/search/%s?private_token=%s" % (args.project, token)
print "  url : " + url
res = requests.get(url)
project_id = str(res.json()[0].get("id"))
print "  project_id=" + project_id
print ""

#---------------------------------------------------------
# マージリクストの一覧を取得し、新着をMattermostにPOSTする
#---------------------------------------------------------
print ">>> Merge Request Search"
url = args.url + "/api/v3/projects/%s/merge_requests?private_token=%s" % (project_id, token)
print "  url : " + url
res = requests.get(url)
ar = res.json();
for mr in ar:
    print "  Target Merge Request Count = " + str(len(ar))
    print json.dumps(mr, indent=2)
    push(format_mergerequest(mr))
print ""        

#---------------------------------------------------------
# ブランチの一覧を取得する
#---------------------------------------------------------
print ">>> Get Branch List"
url = args.url + "/api/v3/projects/%s/repository/branches?private_token=%s" % (project_id, token)
print "  url : " + url
res = requests.get(url)
branchlist = res.json();
# todo: commited_date を見て、コミットがないブランチはスルーするべき
print "  branch Count = " + str(len(branchlist))
print ""

#---------------------------------------------------------
# １つずつBranchの中のコミット一覧を取得し、新着のコミットを
#---------------------------------------------------------
for br in branchlist:
    print ">>> Get Commit List From Branch ( " + br["name"] + " )"
    url = args.url + "/api/v3/projects/%s/repository/commits?ref_name=%s&private_token=%s" % (project_id, br["name"], token)
    print "  url : " + url
    commitlist = requests.get(url).json()
    print "  Commit Count = " + str(len(commitlist))
    for cm in commitlist:
        print json.dumps(cm, indent=2)
        push(format_commit(cm, br))

now = datetime.now(timezone('Asia/Tokyo'))
tstr = now.strftime('%Y-%m-%d %H:%M:%S %z')
f = open(filename, "w")
f.write(tstr)
f.close()


