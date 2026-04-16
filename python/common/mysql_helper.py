# -*- coding: utf-8 -*-

from datetime import datetime
import json
import mysql.connector.pooling


class MySQLHelper:
    __instance = None

    @staticmethod
    def get_instance():
        if MySQLHelper.__instance is None:
            MySQLHelper.__instance = MySQLHelper()
        return MySQLHelper.__instance

    def __init__(self, host='localhost', port=3306, user='root', password='123456', database='test'):
        if MySQLHelper.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            config = {
                "user": user,
                "password": password,
                "host": host,
                "database": database
            }
            self.cnxpool = mysql.connector.pooling.MySQLConnectionPool(pool_name="mypool", pool_size=3, **config)
            MySQLHelper.__instance = self

    def execute(self, sql, data=None):
        conn = self.cnxpool.get_connection()
        cursor = conn.cursor()
        if data:
            cursor.execute(sql, data)
        else:
            cursor.execute(sql)
        conn.commit()
        cursor.close()
        conn.close()

    def fetch_all(self, sql):
        conn = self.cnxpool.get_connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result

    # ** 此方法用于查询数据，目前支持Null，datetime，字符串，数字，如果以后有报错，需要进行优化 **
    def fetch_one2dict(self, sql):
        conn = self.cnxpool.get_connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        result = cursor.fetchone()
        if result is None:
            cursor.close()
            conn.close()
            return None
        my_list = list(result)

        for i in range(len(my_list)):
            if my_list[i] is None:
                my_list[i] = 'None'
            elif isinstance(my_list[i], datetime):
                my_list[i] = my_list[i].isoformat()
            elif type(my_list[i]) is bytes:
                my_list[i] = my_list[i].decode('utf-8')
        result = tuple(my_list)
        # 将字段名和对应的值转为字典
        columns = [column[0] for column in cursor.description]
        data = dict(zip(columns, result))
        cursor.close()
        conn.close()
        # 将字典对象转换为 JSON 字符串
        json_str = json.dumps(data)
        return json_str

    def select(self, table, columns, condition=None):
        column_str = ",".join(columns)
        sql = f"SELECT {column_str} FROM {table}"
        if condition:
            sql += f" WHERE {condition}"
        return self.fetch_all(sql)

    def insert(self, table, data):
        # {'id':101,'name':'gail','password':'123123'}
        column_str = ",".join(data.keys())
        value_str = ",".join(["'%s'" % v for v in data.values()])
        sql = f"INSERT INTO {table}({column_str}) VALUES({value_str})"
        self.execute(sql)

    def update(self, table, data, condition=None):
        update_str = ",".join([f"{k}='{v}'" for k, v in data.items()])
        sql = f"UPDATE {table} SET {update_str}"
        if condition:
            sql += f" WHERE {condition}"
        self.execute(sql)

    def delete(self, table, condition):
        sql = f"DELETE FROM {table} WHERE {condition}"
        self.execute(sql)
