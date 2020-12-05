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
                userinfo = query_db('select name, phone_num, description, level from user where name = ?', (args['name'],))
                return {'result': 'success', 'userinfo': userinfo}
            else:
                return {'result': 'fail', 'errMsg': 'wrong password'}
        else:
            return {'result': 'fail', 'errMsg': 'user not exist'}

api.add_resource(CheckUserSignin, '/signin')

if __name__ == '__main__':
  app.run(host='0.0.0.0', debug=True)



