import datetime
from werkzeug.security import generate_password_hash
from models import Tracker, Log, User, Setting
from flask_restful import reqparse, Resource
from database import db

from flask import current_app as app


#................APIs.........................#
create_user_parser = reqparse.RequestParser()
create_user_parser.add_argument('email', type=str)
create_user_parser.add_argument('user_password', type=str)

class user_api(Resource):
    def post(self):
        args = create_user_parser.parse_args()
        email = args.get("email", None)
        user_password = args.get("user_password", None)

        if email is None or user_password is None:
            return "Bad Request", 400
        
        if User.query.filter_by(email = email).first() is None:
            user = User(email = email, user_password = generate_password_hash(user_password))
        else:
            return "Username Exists", 400
        
        try:
            db.session.add(user)
            db.session.flush()
        except:
            db.session.rollback()
            return "Internal Server Error", 500
        
        db.session.commit()
        
        return {"user_id": user.id, "email": user.email}, 201
    

create_tracker_parser = reqparse.RequestParser()
create_tracker_parser.add_argument('tracker_name', type=str)
create_tracker_parser.add_argument('tracker_type', type=str)
create_tracker_parser.add_argument('description', type=str)
create_tracker_parser.add_argument('last_review', type=str)
create_tracker_parser.add_argument('settings', type=str)

class tracker_api(Resource):
    # @auth.login_required
    def post(self, user_id):
        args = create_tracker_parser.parse_args()

        tracker_name = args.get("tracker_name", None)
        tracker_type = args.get("tracker_type", None)
        description = args.get("description", None)
        settings = args.get("settings", None)
        
        if tracker_name is None or tracker_type is None or description is None:
            return "Bad Request", 404

        tracker = Tracker(user_id = user_id, tracker_name = tracker_name, tracker_type = tracker_type, description = description)

        try:
            db.session.add(tracker)
            settings1 = settings.split(",")
            if len(settings1) % 2 == 0 and len(settings1) > 0:
                for i in range(0, len(settings1), 2):
                    tracker.settings.append(Setting(tracker_id = tracker.tracker_id, setting_name = settings1[i], setting_value = settings1[i+1]))
            db.session.flush()
        except Exception as error:
            print(error)
            db.session.rollback()
            return "Internal Server Error", 500
        
        db.session.commit()
        
        return {"tracker_id": tracker.tracker_id, "tracker_name": tracker.tracker_name, "tracker_type": tracker.tracker_type, "description": tracker.description}, 201 
    
    
    def get(self, user_id, tracker_id):
        tracker = Tracker.query.filter_by(user_id = user_id, tracker_id = tracker_id).first()
        settings = tracker.settings
        if tracker is None:
            return "No such tracker", 400
        else:
            settings_obj = []
            if tracker.tracker_type == 5:
                for i in settings:
                    settings_obj.append({
                        "setting_name": i.setting_name,
                        "setting_value": i.setting_value
                    })
            return {
                "tracker_id": tracker.tracker_id,
                "tracker_name": tracker.tracker_name,
                "description": str(tracker.description),
                "tracker_type": tracker.tracker_type,
                "last_review": str(tracker.last_review),
                "settings": settings_obj
                }
    
    def put(self, user_id, tracker_id):
        args = create_tracker_parser.parse_args()
        tracker_name = args.get("tracker_name", None)
        description = args.get("description", None)
        settings = args.get("settings", None)
        
        
        if tracker_name is None or description is None:
            return "Bad Request", 400
        
        tracker = Tracker.query.filter_by(user_id = user_id, tracker_id = tracker_id).first()
        if tracker is None:
            return "No such tracker", 400
        else:
            tracker.tracker_name = tracker_name
            tracker.description = description
        
        try:
            db.session.add(tracker)
            if settings is not None:
                settings1 = settings.split(",")
                a = []
                if len(settings1) % 2 == 0 and len(settings1) > 0:
                    for i in range(0, len(settings1), 2):
                        a.append(Setting(tracker_id = tracker.tracker_id, setting_name = settings1[i], setting_value = settings1[i+1]))
                tracker.settings = a
            db.session.flush()
        except Exception as error:
            print(error)
            db.session.rollback()
            return "Internal Server Error", 500
        
        db.session.commit()
        return {"tracker_name": tracker.tracker_name, "tracker_type": tracker.tracker_type, "description": tracker.description}, 201 
        
    def delete(self, user_id, tracker_id):
        tracker = Tracker.query.filter_by(user_id = user_id, tracker_id = tracker_id).first()
        if tracker is None:
            return "No such tracker", 400
        try:
            db.session.delete(tracker)
            db.session.flush()
        except Exception as error:
            print(error)
            db.session.rollback()
            return "Internal Server Error", 500
        db.session.commit()
        return "Successfully Deleted", 200
        
class trackers_api(Resource):
    def get(self, user_id):
        user = User.query.filter_by(id = user_id).first()
        trackers = user.trackers
        if trackers == []:
            return [], 200
        else:
            trackers_obj = []
            for i in trackers:
                trackers_obj.append({"tracker_id": i.tracker_id, "tracker_name": i.tracker_name, "tracker_type": i.tracker_type, "description": i.description, "last_review": str(i.last_review), "last_value": str(i.last_value)})
            return trackers_obj, 200
                  
    
    
create_log_parser = reqparse.RequestParser()
create_log_parser.add_argument('desc', type=str, help = "Did not recieve desc")
create_log_parser.add_argument('value', type=str, help = "Did not receive value")
create_log_parser.add_argument('timestamp', type=str, help = "Did not receive timestamp")

class log_api(Resource):
    def post(self, user_id, tracker_id):

        args = create_log_parser.parse_args()
        
        desc = args.get("desc", None)
        value = args.get("value", None)
        
        if desc is None or value is None:
            return "Bad Request", 404
        
        timestamp = datetime.datetime.utcnow()
        

        
        log = Log(user_id = user_id, tracker_id = tracker_id, value = value, desc= desc, timestamp = timestamp)
        tracker = Tracker.query.filter_by(tracker_id = tracker_id).first()
        tracker.last_review = timestamp
        tracker.last_value = value
        try:
            db.session.add(log)
            db.session.add(tracker)
            db.session.flush()
        except:
            db.session.rollback()
            return "Internal Server Error", 500
        
        db.session.commit()
        
        return {"user_id": log.user_id, "tracker_id": log.tracker_id, "log_id": log.log_id, "value": str(log.value), "desc": log.desc, "timestamp": str(log.timestamp)}, 201 

    def get(self, user_id, log_id):
        log = Log.query.filter_by(user_id = user_id, log_id = log_id).first()
        if log is None:
            return "No such log", 400
        
        return {
            "log_id": log.log_id,
            "value": str(log.value),
            "desc": log.desc
        }
    
    def put(self, user_id, log_id):
        args = create_log_parser.parse_args()
        desc = args.get("desc", None)
        value = args.get("value", None)
        timestamp = args.get("timestamp", None)
        
        if desc is None or value is None or timestamp is None:
            return "Bad Request", 400
        
        log = Log.query.filter_by(user_id = user_id, log_id = log_id).first()
        if log is None:
            return "No such log", 400
        
        d = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f")
        
        log.desc = desc
        log.value = value
        log.timestamp = d
        
        try:
            db.session.add(log)
            db.session.flush()
        except Exception as e:
            db.session.rollback()
            print(e)
            return "Internal Server Error", 500
        db.session.commit()
        
        return {"user_id": log.user_id, "tracker_id": log.tracker_id, "log_id": log.log_id, "value": str(log.value), "desc": log.desc, "timestamp": str(log.timestamp)}, 201 
 
    def delete(self, user_id, log_id):
        log = Log.query.filter_by(user_id = user_id, log_id = log_id).first()
        if log is None:
            return "No such log", 400
        try:
            db.session.delete(log)
            db.session.flush()
        except:
            db.session.rollback()
            return "Internal Server Error", 500
        db.session.commit()
        
        return "Successfully Deleted", 200

class logs_api(Resource):
    def get(self, user_id, tracker_id):
        tracker = Tracker.query.filter_by(user_id = user_id, tracker_id = tracker_id).first()
        logs = []
        settings = []
        logs_obj = []
        settings_obj = []
        if tracker is None:
            return {
                "tracker_type": tracker.tracker_type,
                "logs": [],
                "settings": []
                }, 400
        else:
            logs = tracker.logs
            settings = tracker.settings
            if tracker.tracker_type == '5' or 5 and len(settings) > 0:
                for i in settings:
                    settings_obj.append({
                        "setting_name": i.setting_name,
                        "setting_value": i.setting_value
                    })
        if logs == []:
            return {
                "tracker_type": tracker.tracker_type,
                "logs": [],
                "settings" : settings_obj
                }, 200
        else:
            for i in logs:
                logs_obj.append({
                    "log_id": i.log_id,
                    "value": str(i.value),
                    "desc": i.desc,
                    "timestamp": str(i.timestamp)
                })
            return {
                "tracker_type": tracker.tracker_type,
                "logs": logs_obj,
                "settings": settings_obj
            }
                

create_settings_parser = reqparse.RequestParser()
create_settings_parser.add_argument('setting_name', type=str)
create_settings_parser.add_argument('setting_value', type=str)

class setting_api(Resource):
    def post(self, tracker_id):
        args = create_settings_parser.parse_args()
        setting_name = args.get("setting_name", None)
        setting_value = args.get("setting_value", None)
        
        if setting_name is None or setting_value is None:
            return "Bad Request", 404
        
        setting = Setting(tracker_id = tracker_id, setting_name = setting_name, setting_value = setting_value)
        
        try:
            db.session.add(setting)
            db.session.flush()
        except:
            db.session.rollback()
            return "Internal Servor Error", 500
        db.session.commit()
        
        return {"tracker_id": tracker_id, "setting_name": setting_name, "setting_value": setting_value}

    def get(self, tracker_id):
        tracker = Tracker.query.filter_by(tracker_id = tracker_id).first()
        settings = tracker.settings
        settings_obj = []
        for i in settings:
            settings_obj.append({
                "setting_name": i.setting_name,
                "setting_value": i.setting_value
            })
        return settings_obj
    
    def delete(self, tracker_id):
        args = create_settings_parser.parse_args()
        setting_name = args.get("setting_name", None)
        
        setting = Setting.query.filter_by(tracker_id = tracker_id, setting_name = setting_name).first()
        
        try:
            db.session.delete(setting)
            db.session.flush()
        except:
            db.session.rollback()
            return "Internal Server Error", 500
        db.session.commit()
        return "Successfully Deleted"

import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as md
import numpy as np
import datetime as dt
import json
import os

mpl.rcParams['lines.linewidth'] = 4
mpl.rcParams['axes.titlesize'] = 24
mpl.rcParams['axes.titlecolor'] = 'k'
mpl.rcParams['ytick.labelsize'] = 16

class dashboard_api(Resource):
    def get(self, user_id, tracker_id):
        if user_id is None or tracker_id is None:
            return "Bad Request", 404
        #Make Directory of User
        script_dir = os.path.dirname(__file__)
        user_dir = "visualizations/{}/".format(user_id)
        results_dir = os.path.join(script_dir, user_dir)
        
        if not os.path.isdir(results_dir):
            os.makedirs(results_dir)
        
        tracker = Tracker.query.filter_by(tracker_id = tracker_id).first()
        tracker_type = tracker.tracker_type
        if tracker_type == 1:
        #Numerical
            #Trendline
            result_1 = db.session.execute('SELECT value, timestamp from LOG where user_id = :user_id and tracker_id = :tracker_id', {"user_id": user_id, "tracker_id" : tracker_id})
            #Scatter
            result_2 = db.session.execute('SELECT value, count(DISTINCT(value)) FROM LOG where user_id = :user_id and tracker_id = :tracker_id group by value', {"user_id": user_id, "tracker_id" : tracker_id})
            #Aggregation
            result_3 = db.session.execute('SELECT sum(value), ROUND(avg(value),2), max(value), min(value) FROM LOG where user_id = :user_id and tracker_id = :tracker_id;',  {"user_id": user_id, "tracker_id" : tracker_id})

            #result_1
            dates = []
            values = []
            for i in result_1:
                dates.append(datetime.datetime.strptime(i['timestamp'], "%Y-%m-%d %H:%M:%S.%f"))
                values.append(i['value'])
            print(dates)
            plt.subplots_adjust(bottom=0.2) #adds space on the bottom
            plt.xticks( rotation=25 ) #sets the angle of the x-ticks
            plt.title("Trendline")
            plt.ylabel("Value")
            ax=plt.gca() #gets the current axes
            xfmt = md.DateFormatter('%Y-%m-%d %H:%M:%S')
            ax.xaxis.set_major_formatter(xfmt)
            plt.plot(dates,values)
            filename = user_dir + "{}_{}_1".format(user_id, tracker_id)
            plt.savefig(fname = filename, edgecolor = "black", orientation = "potrait")
            plt.clf()
            # plt.show()
            
            #result_2
            values_2 = []
            count = []
            for i in result_2:
                print(i)
                values_2.append(i[0])
                count.append(i[1])
            colors = np.random.rand(len(values_2))
            plt.scatter(x=values_2,y=count,c=colors,alpha=0.5)
            plt.title("Scatter")
            plt.xlabel("Numerical Values", fontweight="bold")
            plt.ylabel("count", fontweight="bold")
            filename_2 = user_dir + "{}_{}_2".format(user_id, tracker_id)
            plt.savefig(fname = filename_2, edgecolor = "black", orientation = "potrait")
            plt.clf()
            aggregations = result_3.fetchall()
            final = {
                "sum": aggregations[0][0],
                "avg": aggregations[0][1],
                "max": aggregations[0][2],
                "min": aggregations[0][3]
            }
            # print(final)
            return final, 200
        elif tracker_type == 2:
        #Decimal
            #Trendline
            result_1 = db.session.execute('SELECT value, timestamp from LOG where user_id = :user_id and tracker_id = :tracker_id', {"user_id": user_id, "tracker_id" : tracker_id})
            #Scatter
            result_2 = db.session.execute('SELECT value, count(DISTINCT(value)) FROM LOG where user_id = :user_id and tracker_id = :tracker_id group by value', {"user_id": user_id, "tracker_id" : tracker_id})
            #Aggregation
            result_3 = db.session.execute('SELECT coalesce(sum(value),0), coalesce(avg(value),0), coalesce(max(value),0), coalesce(min(value),0) FROM LOG where user_id = :user_id and tracker_id = :tracker_id;',  {"user_id": user_id, "tracker_id" : tracker_id})

            #result_1
            dates = []
            values = []
            for i in result_1:
                dates.append(datetime.datetime.strptime(i['timestamp'], "%Y-%m-%d %H:%M:%S.%f"))
                values.append(i['value']/100)
            print(dates)
            plt.subplots_adjust(bottom=0.2) #adds space on the bottom
            plt.xticks( rotation=25 ) #sets the angle of the x-ticks
            plt.title("Trendline")
            plt.ylabel("Value")
            ax=plt.gca() #gets the current axes
            xfmt = md.DateFormatter('%Y-%m-%d %H:%M:%S')
            ax.xaxis.set_major_formatter(xfmt)
            plt.plot(dates,values)
            filename = user_dir + "{}_{}_1".format(user_id, tracker_id)
            plt.savefig(fname = filename, edgecolor = "black", orientation = "potrait")
            plt.clf()
            # plt.show()
            
            #result_2
            values_2 = []
            count = []
            for i in result_2:
                print(i)
                values_2.append(i[0]/100)
                count.append(i[1])
            colors = np.random.rand(len(values_2))
            plt.scatter(x=values_2,y=count,c=colors,alpha=0.5)
            plt.title("Scatter")
            plt.xlabel("Decimal Values", fontweight="bold")
            plt.ylabel("count", fontweight="bold")
            filename_2 = user_dir + "{}_{}_2".format(user_id, tracker_id)
            plt.savefig(fname = filename_2, edgecolor = "black", orientation = "potrait")
            plt.clf()
            aggregations = result_3.fetchall()
            final = {
                "sum": aggregations[0][0]/100,
                "avg": aggregations[0][1]/100,
                "max": aggregations[0][2]/100,
                "min": aggregations[0][3]/100
            }
            # print(final)
            return final, 200
        elif tracker_type == 3:
        #Boolean
            #Pie and Horizontal Graph:
            result_1 = db.session.execute('SELECT value, count((value)) FROM LOG where user_id = :user_id and tracker_id = :tracker_id group by value',{"user_id": user_id, "tracker_id" : tracker_id})
            #Pie
            values_3 = []
            labels = ["False", "True"]
            for i in result_1:
                    values_3.append(i[1])
            if len(values_3) == len(labels):
                # print(values_3, labels)
                plt.pie(values_3, labels=labels)
                plt.legend()
                filename = user_dir + "{}_{}_1".format(user_id, tracker_id)
                plt.savefig(fname=filename,edgecolor="black", orientation="potrait")
                plt.clf()
                #Horizontal Graph
                h = plt.barh(labels, values_3, color=[(0.2,0.7,0.6), (0.1,0.3,0.9)])
                plt.legend(h, labels)
                filename_2 = user_dir + "{}_{}_2".format(user_id, tracker_id)
                plt.savefig(fname=filename_2, edgecolor="black", orientation="potrait")
                plt.clf()
            return [], 200
        elif tracker_type == 4:
        #Time Duration
            #Scatter:
            result_1 = db.session.execute('SELECT value, count((value)) FROM LOG where user_id = :user_id and tracker_id = :tracker_id group by value', {"user_id": user_id, "tracker_id": tracker_id})
            #Aggregation:
            result_2 = db.session.execute('SELECT sum(value), avg(value), max(value), min(value)  FROM LOG where user_id = :user_id and tracker_id = :tracker_id', {"user_id": user_id, "tracker_id": tracker_id})
            
            #result_1
            values = []
            count = []
            for i in result_1:
                values.append(i[0])
                count.append(i[1])
            plt.scatter(x=values,y=count, s=100, alpha=0.5)
            plt.title("Scatter")
            plt.xlabel("Time Spent(minutes)", fontweight="bold")
            plt.ylabel("count", fontweight="bold")
            filename = user_dir + "{}_{}_1".format(user_id, tracker_id)
            plt.savefig(fname = filename, edgecolor = "black", orientation = "potrait")
            plt.clf()
            aggregations = result_2.fetchall()
            final = {
                "sum": aggregations[0][0],
                "avg": aggregations[0][1],
                "max": aggregations[0][2],
                "min": aggregations[0][3]
            }
            # print(final)
            return final, 200
        elif tracker_type == 5:
        #Multiple Choice
            #Pie and Horizontal Graph:
            result_1 = db.session.execute('SELECT value, count((value))  FROM LOG where user_id = :user_id and tracker_id = :tracker_id group by value', {"user_id": user_id, "tracker_id": tracker_id})   
            tracker = Tracker.query.filter_by(tracker_id = tracker_id).first()
            settings = tracker.settings
            labels = []
            for i in settings:
                labels.append(i.setting_name)
            print(labels)
            #Pie
            values_3 = []
            for i in result_1:
                values_3.append(i[1])
            print(values_3)
            if len(values_3) == len(labels):
                plt.pie(values_3, labels=labels)
                plt.legend()
                filename = user_dir + "{}_{}_1".format(user_id, tracker_id)
                plt.savefig(fname=filename,edgecolor="black", orientation="potrait")
                plt.clf()
                #Horizontal Graph
                colors = []
                for i in labels:
                    x = tuple(np.random.choice(range(99), size=3)/100)
                    colors.append(x)
                print(colors)
                h = plt.barh(labels, values_3, color=colors)
                plt.legend(h, labels)
                filename_2 = user_dir + "{}_{}_2".format(user_id, tracker_id)
                plt.savefig(fname=filename_2, edgecolor="black", orientation="potrait")
                plt.clf()
            return [], 200
        else:
            return "Bad Request", 404   
        plt.close()

app.api.add_resource(user_api, '/api/user')
app.api.add_resource(tracker_api, '/api/tracker/post/<int:user_id>', '/api/tracker/<int:user_id>/<int:tracker_id>')
app.api.add_resource(log_api, '/api/log/post/<int:user_id>/<int:tracker_id>', '/api/log/<int:user_id>/<int:log_id>')
app.api.add_resource(setting_api, '/api/setting/post/<int:tracker_id>', '/api/setting/<int:tracker_id>')
app.api.add_resource(trackers_api, '/api/trackers/<int:user_id>')
app.api.add_resource(logs_api, '/api/logs/<int:user_id>/<int:tracker_id>') 
app.api.add_resource(dashboard_api, '/api/dashboard/<int:user_id>/<int:tracker_id>')   