from flask import Flask, request, render_template, redirect, url_for, session
from flask import current_app as app
from flask_login import login_required
import requests
import datetime
from models import Log, User

url = "http://127.0.0.1:5000"

'''
#Routes
"/", GET ==> get all trackers
"/", POST ==> create new tracker
"/tracker_id/delete" ==> delete a tracker
"/tracker_id/edit" ==> get edit page of tracker
"/tracker_id/update" ==> update a tracker

"/logs/tracker_id/tracker_name" ==> get all logs of a tracker
"/logs/tracker_id/tracker_name/log_id/delete" ==> delete a log of a tracker
"/logs/tracker_id/tracker_name/log_id/edit" ==> get the edit page of a log
"/logs/tracker_id/tracker_name/log_id/update" ==> update log of a tracker

'''


@app.route("/", methods = ["GET", "POST"])
@login_required
def trackers():
    id = session["_user_id"]
    print(session.keys())
    if request.method == 'GET':
        x = requests.get(url+"/api/trackers/{}".format(id))
        trackers = x.json()
        return render_template("trackers.html", template_folder = "templates", trackers = trackers)
    elif request.method == 'POST':
        (tracker_name, tracker_type, description, settings) = (request.form['tracker_name'], request.form['tracker_type'], request.form['description'], request.form['settings'])
        if tracker_type not in ['1', '2', '3', '4', '5']:
            return redirect(url_for(trackers))
        tracker = {
            "tracker_name": tracker_name,
            "tracker_type": tracker_type,
            "description": description,
            "last_review": "",
            "settings": settings
        }
        x = requests.post(url+"/api/tracker/post/{}".format(id), data = tracker)
        print(x)
        return redirect(url_for('trackers'))
    
    
@app.route("/<int:tracker_id>/delete", methods = ["GET"])
def trackers_d(tracker_id):
    id = session["_user_id"]
    x = requests.delete(url+"/api/tracker/{}/{}".format(id, tracker_id))
    # print(str(x))
    return redirect(url_for('trackers'))



@app.route("/<int:tracker_id>/edit", methods = ["GET"])
def trackers_e(tracker_id):
    id = session["_user_id"]
    x = requests.get(url+"/api/tracker/{}/{}".format(id, tracker_id))
    x_json = x.json()
    settings = x_json['settings']
    setting1 = ""
    for i in settings:
        print(settings)
        setting1 += i['setting_name'] + "," + str(i['setting_value']) + ","
    setting1 = setting1[:-1]
    return render_template('edit_tracker.html', template_folder = 'templates', id = tracker_id, name = x_json['tracker_name'], type = x_json['tracker_type'], description = x_json['description'], setting = setting1)


@app.route("/<int:tracker_id>/update", methods = ["POST"])
def trackers_p(tracker_id):
    id = session["_user_id"]
    setting = ""
    (tracker_name, description, type) = (request.form['tracker_name'], request.form['description'], request.form['tracker_type'])
    if type == '5' or type == 5:
        setting = request.form['setting']
    tracker = {
        "tracker_name": tracker_name,
        "tracker_type": "",
        "description": description,
        "last_review": "",
        "settings": setting
    }
    x = requests.put(url+"/api/tracker/{}/{}".format(id, tracker_id), data = tracker)
    print(x)
    return redirect(url_for('trackers'))    



@app.route("/logs/<int:tracker_id>/<string:tracker_name>", methods = ["GET", "POST"])
def logs(tracker_id, tracker_name):
    id = session["_user_id"]
    if request.method == 'GET':
        x = requests.get(url+"/api/logs/{}/{}".format(id, tracker_id))
        logs = x.json()
        y = requests.get(url+"/api/dashboard/{}/{}".format(id,tracker_id))
        image_url_1 = "/visualizations/" + "{}/{}_{}_1.png".format(id, id, tracker_id)
        image_url_2 = "/visualizations/" + "{}/{}_{}_2.png".format(id, id, tracker_id)
        aggs = y.json()
        return render_template("logs.html", template_folder = "templates", logs = logs['logs'], name = tracker_name, id = tracker_id, type=logs['tracker_type'], settings = logs['settings'], value_multi = "none", image_url_1 = image_url_1, image_url_2 = image_url_2, agg = aggs)
    elif request.method == 'POST':
        (desc, type) = (request.form['desc'], request.form['type'])
        x = ""
        if type=='5':
            (x) = (request.form['value_multi'])
            if x == "":
                return redirect(url_for('logs', tracker_id = tracker_id, tracker_name = tracker_name)) 
        else:
            (x) = (request.form['value'])
            
            if type == '3':
                if x != '0' and x != '1':
                    return redirect(url_for('logs', tracker_id = tracker_id, tracker_name = tracker_name)) 
                    
        log = {
            "desc": desc,
            "value": x,
            "timestamp": ""
        }
        x = requests.post(url+"/api/log/post/{}/{}".format(id, tracker_id), data = log)
        print(x)
        return redirect(url_for('logs', tracker_id = tracker_id, tracker_name = tracker_name)) 
    
@app.route("/logs/<int:tracker_id>/<string:tracker_name>/<int:log_id>/delete", methods = ["GET"])
def logs_d(log_id, tracker_id, tracker_name):
    id = session["_user_id"]
    x = requests.delete(url+"/api/log/{}/{}".format(id, log_id))
    return redirect(url_for('logs', tracker_id = tracker_id, tracker_name = tracker_name))


@app.route("/logs/<int:tracker_id>/<string:tracker_name>/<int:log_id>/edit", methods = ["GET"])
def logs_e(log_id, tracker_id, tracker_name):
    id = session["_user_id"]
    log = Log.query.filter_by(log_id = log_id).first()
    x = requests.get(url+"/api/tracker/{}/{}".format(id, tracker_id))
    x_json = x.json()
    timestamp = log.timestamp.strftime("%d-%m-%Y_%H:%M:%S")
    return render_template("edit_log.html", template_folder = 'templates', tracker_id = tracker_id, name = tracker_name, log_id = log.log_id, value = log.value, desc = log.desc, timestamp = timestamp, type=x_json['tracker_type'], settings = x_json['settings'])



@app.route("/logs/<int:tracker_id>/<string:tracker_name>/<int:log_id>/update", methods = ["POST"])
def logs_p(log_id, tracker_id, tracker_name):
    id = session["_user_id"]
    (desc, type, ts) = (request.form['desc'], request.form['type'], request.form['timestamp'])
    timestamp = datetime.datetime.strptime(ts, '%d-%m-%Y_%H:%M:%S')
    timestamp += datetime.timedelta(milliseconds=500)

    x = ""
    if type=='5':
        (x) = (request.form['value_multi'])
    else:
        (x) = (request.form['value'])
    log = {
        "desc": desc,
        "value": x,
        "timestamp": timestamp
    }
    x = requests.put(url+"/api/log/{}/{}".format(id, log_id), data = log)
    print(x)
    return redirect(url_for('logs', tracker_id = tracker_id, tracker_name = tracker_name))
