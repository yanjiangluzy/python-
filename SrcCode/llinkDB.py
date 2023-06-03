#!/usr/bin/env python
# -*- coding:utf-8 -*-
import pymssql  # 引入pymssql模块


def AddToDB(user_name, password):
    conn = pymssql.connect(server="127.0.0.1:1433", user="sa", password="cn1314m?", database="ChatRoom", charset="GBK",
                           autocommit=True)
    cursor = conn.cursor(as_dict=True)
    if cursor:
        print("连接数据库成功!")
    sql_select = f"select * from [chat_user]"
    sql_insert = f"insert into [chat_user] values('{user_name}', '{password}')"
    cursor.execute(sql_insert)
    print("插入完毕")
    cursor.close()
    conn.close()  # 关闭数据库连接


def FindInDB(user_name):
    conn = pymssql.connect(server="127.0.0.1:1433", user="sa", password="cn1314m?", database="ChatRoom", charset="GBK",
                           autocommit=True)
    cursor = conn.cursor(as_dict=True)
    if cursor:
        print("连接数据库成功!")
    print(f"开始查找: {user_name, len(user_name)}")
    sql_select = f"select * from [chat_user]"
    cursor.execute(sql_select)
    results = cursor.fetchall()
    for result in results:
        name = str(result['name']).rstrip()
        if name == user_name:
            return True
    cursor.close()
    conn.close()  # 关闭数据库连接
    return False


def DelInDB(user_name):
    conn = pymssql.connect(server="127.0.0.1:1433", user="sa", password="cn1314m?", database="ChatRoom", charset="GBK",
                           autocommit=True)
    cursor = conn.cursor(as_dict=True)
    if cursor:
        print("连接数据库成功!")
    sql_del = f"delete from [chat_user] where [name] = '{user_name}'"
    cursor.execute(sql_del)
    print("删除完毕")
    cursor.close()
    conn.close()  # 关闭数据库连接


def GetAllUsersFromDB():
    conn = pymssql.connect(server="127.0.0.1:1433", user="sa", password="cn1314m?", database="ChatRoom", charset="GBK",
                           autocommit=True)
    cursor = conn.cursor(as_dict=True)
    if cursor:
        print("连接数据库成功!")
    sql_select = f"select * from [chat_user]"
    cursor.execute(sql_select)
    results = cursor.fetchall()
    res = []
    for result in results:
        name = str(result['name']).rstrip()
        password = str(result['password'])
        res.append((name, password))
    cursor.close()
    conn.close()  # 关闭数据库连接
    return res
