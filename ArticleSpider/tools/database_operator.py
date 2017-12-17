# coding=utf-8
import MySQLdb
import datetime
from MySQLdb.cursors import DictCursor
from DBUtils.PooledDB import PooledDB


class DataBaseOperator:
    # 连接池对象
    __pool = None

    def __init__(self):

        # 数据库构造函数，从连接池中取出连接，并生成操作游标
        self._conn = DataBaseOperator.__get_conn()
        self._cursor = self._conn.cursor()

    @staticmethod
    def __get_conn():
        """
        @summary: 静态方法，从连接池中取出连接
        @return MySQLdb.connection
        """
        if DataBaseOperator.__pool is None:
            __pool = PooledDB(creator=MySQLdb, mincached=1, maxcached=20,
                              host='localhost', user='root', passwd='krzz1937',
                              db="scrapyspider", charset='utf8', cursorclass=DictCursor)
        return __pool.connection()

    def insert_table(self, sql):
        self._cursor.execute(sql)
        self._conn.commit()
        return

    def query_table(self, sql):
        self._cursor.execute(sql)
        return self._cursor.fetchall()

    def save_authorization(self, auth_key, auth_value, user_id=None):
        update_time = datetime.datetime.now()
        sql = "select auth_value from cookies where auth_key = '%s'" % auth_key
        if user_id:
            sql = "%s and user_id = '%s'" % (sql, user_id)
        result = self.query_table(sql)
        if len(result) == 0:
            sql = "insert into cookies (auth_key, auth_value, user_id, update_time)" \
                  " values ('%s','%s','%s', '%s')" \
                  % (auth_key, auth_value, user_id, update_time)
        else:
            sql = "update cookies set auth_value = '%s',update_time = '%s' where auth_key = '%s'" \
                  % (auth_value, update_time, auth_key)
            if user_id:
                sql = "%s and user_id = '%s'" % (sql, user_id)

        self.insert_table(sql)
        return

    def get_authorization(self, auth_key, user_id=None):
        sql = "select auth_value from cookies where auth_key = '%s' " % auth_key
        if user_id:
            sql = "%s and user_id='%s'" % (sql, user_id)
        sql = sql + " order by update_time desc"
        result = self.query_table(sql)
        if len(result) > 0:
            return result[0]['auth_value']
        else:
            return None


db_operator = DataBaseOperator()
if __name__ == "__main__":

    db_operator.save_authorization('lagou', 'cookies test', 'suyajie')
    print(db_operator.query_table("select *  from cookies"))
    print(db_operator.get_authorization('lagou'))

