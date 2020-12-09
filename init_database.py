import sqlite3

DATABASE = 'database/callup_system.db'

def create_table(table_name):
    db = sqlite3.connect(DATABASE)
    c = db.cursor()
    c.execute(table_name)
    db.commit()
    db.close()

def insert_into_table(table_name, values):
    db = sqlite3.connect(DATABASE)
    c = db.cursor()
    c.execute('insert into ' + table_name + ' values ' + values)
    db.commit()
    db.close()

user_table = '''create table user(
    id int primary key not null,
    name text not null, -- 注册必备
    password text not null, -- 注册必备
    phone_num text not null, -- 注册必备
    description char(100),
    user_type int not null, -- 1：普通用户 2：管理员 管理员只能后台注册
    identity_type int not null, -- 1：身份证 2：护照 注册必备
    identity_num text not null, -- 注册必备
    level int, -- 1-3等级逐渐增大
    city text not null, -- 注册必备
    signup_time text not null,
    modify_time text not null
);'''

user_HHX = '(1, "HHX", "hhx100", "12345678910", "", 2, 1, 111111111111111111, 3, "beijing", "2020-12-5", "2020-12-5")'
user_FB = '(2, "FB", "fb100", "12345678911", "", 2, 1, 111111111111111112, 3, "beijing", "2020-12-5", "2020-12-5")'


if __name__ == '__main__':
    insert_into_table("user", user_HHX)
    insert_into_table("user", user_FB)
