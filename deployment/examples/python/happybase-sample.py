#!/usr/bin/env python3
import os

#####################################################################################################################
#
# Here are some useful links relevant for hbase thrift api:
# http://hbase.apache.org/0.94/book/thrift.html
# https://issues.apache.org/jira/browse/HBASE-5946
# https://happybase.readthedocs.io/en/latest/user.html
# https://happybase.readthedocs.io/en/latest/api.html
#
#####################################################################################################################
import happybase

HBASE_THRIFT = os.environ["HBASE_THRIFT_API"]

print("HBASE Thrift server: {0}".format(HBASE_THRIFT))

pool = happybase.ConnectionPool(size=10, host=HBASE_THRIFT, table_prefix='bravehub', table_prefix_separator=":")
with pool.connection() as connection:
    users_tbl = connection.table("projectowners")
    users = users_tbl.scan(filter="SingleColumnValueFilter('attrs','authentication_provider',=,'binary:github')")

    for key, data in users:
        print("%s--->%s" % (key, data))
