from flask import Flask, g, request
from webargs import fields
from webargs.flaskparser import use_args
import flask_cors
import flask_restful as restful
import sqlite3

DATABASE = 'database/callup_system.db'

app = Flask(__name__)
api = restful.Api(app)
# 允许跨域请求，因为后端是运行在5000端口上的，而前端是3000端口
flask_cors.CORS(app, supports_credentials=True)

@app.before_request
def before_request():
  g.db = sqlite3.connect(DATABASE)

@app.teardown_request
def teardown_request(exception):
  if hasattr(g, 'db'):
    g.db.close()

def query_db(query, args=(), onlyonerow=False):
    c = g.db.execute(query, args)
    rv = [dict((c.description[idx][0], value) for idx, value in enumerate(row)) for row in c.fetchall()]
    return (rv[0] if rv else None) if onlyonerow else rv


class HandleUserSignup(restful.Resource):
    @use_args({
        'name': fields.Str(required=True),
        'password': fields.Str(required=True),
        'phone_num': fields.Str(required=True),
        'description': fields.Str(required=True, allow_none=True),
        'identity_type': fields.Str(required=True),
        'identity_num': fields.Str(required=True),
        'city': fields.Str(required=True),
    }, location='json')
    def post(self, args):
        userexist = query_db('select count(*) as count from user where name = ?', (args['name'],), onlyonerow=True)['count']
        if userexist == 1:
            return {'result': 'fail', 'errMsg': 'user name exist, change a name'}
        else:
            userNum = query_db('select count(*) as count from user', onlyonerow=True)['count']
            newID = userNum + 1
            userType = 1
            nowTime = query_db('select date("now") as now', onlyonerow=True)['now']
            values = '(' + str(newID) + ', "' + args['name'] + '", "' + args['password'] + '", "' + args['phone_num'] + '", "' + args['description'] + '", ' + str(userType) + ', ' + args['identity_type'] + ', "' + args['identity_num'] + '", ' + str(1) + ', "' + args['city'] + '", "' + nowTime + '", "' + nowTime + '")'
            print(values)
            c = g.db.cursor()
            c.execute('insert into user values ' + values)
            g.db.commit()
            return {'result': 'success'}


class CheckUserSignin(restful.Resource):
    @use_args({
        'name': fields.Str(required=True),
        'password': fields.Str(required=True)
    }, location='query')
    def get(self, args):
        userexist = query_db('select count(*) as count from user where name = ?', (args['name'],), onlyonerow=True)['count']
        if userexist == 1:
            rightpassword = query_db('select count(*) as count from user where name = ? and password = ?', (args['name'], args['password']), onlyonerow=True)['count']
            if rightpassword == 1:
                userinfo = query_db('select name, phone_num, description, user_type, identity_type, identity_num, level, city from user where name = ?', (args['name'],))
                return {'result': 'success', 'userinfo': userinfo}
            else:
                return {'result': 'fail', 'errMsg': 'wrong password'}
        else:
            return {'result': 'fail', 'errMsg': 'user not exist'}


class ChangeUserInfo(restful.Resource):
    @use_args({
        'user': fields.Str(required=True),
        'password': fields.Str(required=True, allow_none=True),
        'phone': fields.Str(required=True),
        'description': fields.Str(required=True, allow_none=True)
    }, location='json')
    def post(self, args):
        print(args['password'], args['phone'], args['description'], args['user'])
        nowTime = query_db('select date("now") as now', onlyonerow=True)['now']
        if args['password']:
            changeuserinfo = 'update user set password = "' + args['password'] + '", phone_num = "' + args['phone'] + '", description = "' + args['description'] + '", modify_time = "' + nowTime + '" where name = "' + args['user'] + '"'
            print(changeuserinfo)
            c = g.db.cursor()
            c.execute(changeuserinfo)
            g.db.commit()
        else:
            changeuserinfo = 'update user set phone_num = "' + args['phone'] + '", description = "' + args['description'] + '", modify_time = "' + nowTime + '" where name = "' + args['user'] + '"'
            print(changeuserinfo)
            c = g.db.cursor()
            c.execute(changeuserinfo)
            g.db.commit()
        
        userinfo = query_db('select name, phone_num, description, user_type, identity_type, identity_num, level, city from user where name = ?', (args['user'],))
        return {'result': 'success', 'userinfo': userinfo}


class GetUserList(restful.Resource):
    def get(self):
        userinfo = query_db('select name, phone_num, description, user_type, identity_type, identity_num, level, city, modify_time from user')
        return {'result': 'success', 'userinfo': userinfo}







class AddCallUp(restful.Resource):
    @use_args({
        'username': fields.Str(required=True),
        'title': fields.Str(required=True),
        'type': fields.Str(required=True),
        'endtime': fields.Str(required=True),
        'description': fields.Str(required=True),
        'population': fields.Str(required=True),
        'img': fields.Str(required=True)
    }, location='json')

    def post(self, args):
        userID = str(query_db('select id from user where name = ?', (args['username'], ), onlyonerow=True)['id'])
        name = args['title']
        type = str(args['type'])
        description = args['description']
        member = str(args['population'])
        endTime = args['endtime']
        img = args['img']
        createTime = query_db('select date("now") as now', onlyonerow=True)['now']
        modifyTime = createTime
        state = str(2)

        print(userID, name, type, description, member, endTime, img, createTime, modifyTime, state)
        c = g.db.cursor()
        c.execute('''insert into callup (user_id,name,type,description,member,end_time,img,create_time,
        modify_time,state) values (?,?,?,?,?,?,?,?,?,?)''',
                  (userID, name, type, description, member, endTime, img, createTime, modifyTime, state))
        g.db.commit()
        return {'result': 'success'}


class ChangeCallUp(restful.Resource):
    @use_args({
        'id': fields.Str(required=True),
        'title': fields.Str(required=True),
        'type': fields.Str(required=True),
        'endtime': fields.Str(required=True),
        'description': fields.Str(required=True),
        'population': fields.Str(required=True),
        'img': fields.Str(required=True)
    }, location='json')

    def post(self, args):
        id = args['id']
        name = args['title']
        type = str(args['type'])
        description = args['description']
        member = str(args['population'])
        endTime = args['endtime']
        img = args['img']
        modifyTime = query_db('select date("now") as now', onlyonerow=True)['now']

        print(id, name, type, description, member, endTime, img, modifyTime)
        c = g.db.cursor()
        c.execute('''
            update callup 
            set name=?,type=?,description=?,member=?,end_time=?,img=?,modify_time=?
            where id=?''', (name, type, description, member, endTime, img, modifyTime, id))
        g.db.commit()
        return {'result': 'success'}



class GetCallupList(restful.Resource):
    def get(self):
        callupinfo = query_db('select callup.id as id, user.name as owner, user.id as owner_id, callup.name as name, callup.type as type, user.city as city, callup.description as description, callup.member as member, end_time, img, create_time as ctime, callup.modify_time as mtime from user inner join callup on user.id = callup.user_id')
        for i in range(len(callupinfo)):
            callupinfo[i]['requests'] = query_db('select * from callup_request where callup_id = ?', (callupinfo[i]['id'],))
        return {'result': 'success', 'callupinfo': callupinfo}


# class GetMyCallupList(restful.Resource):
#     @use_args({
#         'name': fields.Str(required=True)
#     }, location='query')
#     def get(self, args):
#         mycallupinfo = query_db('select callup.id as id, user.name as owner, callup.name as name, callup.type as type, callup.description as description, callup.member as member, end_time, img, create_time as ctime, callup.modify_time as mtime, state from user inner join callup on user.id = callup.user_id where user.name = ?', (args['name'],))
#         print(mycallupinfo)
#         for i in range(len(mycallupinfo)):
#             mycallupinfo[i]['requests'] = query_db('select * from callup_request where callup_id = ?', (mycallupinfo[i]['id'],))
#         return {'result': 'success', 'mycallupinfo': mycallupinfo}


# class GetMyReqList(restful.Resource):
#     @use_args({
#         'name': fields.Str(required=True)
#     }, location='query')
#     def get(self, args):
#         myID = query_db('select id from user where name = ?', (args['name'],), onlyonerow=True)['id']
#         # myrequest = query_db('select * from callup_request where user_id = ?', (myID,))
#         myreqinfo = query_db('select callup.id as id, callup.name as name, callup.type as type, callup.description as description, callup.member as member, callup.end_time as end_time, img, callup.create_time as ctime, callup.modify_time as mtime, callup.state as state, callup_request.description as reqdescription, callup_request.create_time as reqctime, callup_request.modify_time as reqmtime, callup_request.state as reqstate from callup_request inner join callup on callup.id = callup_request.callup_id where callup_request.user_id = ?', (myID,))
#         return {'result': 'success', 'myreqinfo': myreqinfo}


api.add_resource(HandleUserSignup, '/signup')
api.add_resource(CheckUserSignin, '/signin')
api.add_resource(ChangeUserInfo, '/changeuserinfo')
api.add_resource(GetUserList, '/userlist')
api.add_resource(GetCallupList, '/calluplist')
# api.add_resource(GetMyCallupList, '/mycalluplist')
# api.add_resource(GetMyReqList, '/myreqlist')


api.add_resource(AddCallUp, '/addcallup')
api.add_resource(ChangeCallUp, '/changecallup')

if __name__ == '__main__':
  app.run(host='0.0.0.0', debug=True)



