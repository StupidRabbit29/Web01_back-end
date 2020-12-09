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


api.add_resource(HandleUserSignup, '/signup')
api.add_resource(CheckUserSignin, '/signin')


if __name__ == '__main__':
  app.run(host='0.0.0.0', debug=True)



