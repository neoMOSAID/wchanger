#!/usr/bin/python

import sqlite3
import csv
import sys
import os
import uuid
import hashlib
import inspect


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def connectDB():
    try:
        path = os.path.dirname(os.path.realpath(__file__)) + "/wchangerDB.db"
        con = sqlite3.connect(path)
        return con
    except sqlite3.Error as error:
        eprint("@%s: %s" % (inspect.stack()[0][3], error))


def createDB():
    con = connectDB()
    c = con.cursor()
    c.execute(
        """
    CREATE TABLE  IF NOT EXISTS "PASSWORDS" (
        "user"	text NOT NULL UNIQUE,
        "password"	text NOT NULL
    );"""
    )
    c.execute(
        """CREATE TABLE IF NOT EXISTS downloaded(
    id INTEGER PRIMARY KEY  ,
    name text  NOT NULL UNIQUE,
    dir text,
    path text );"""
    )
    c.execute(
        """CREATE TABLE IF NOT EXISTS wtags(
    id INTEGER PRIMARY KEY  ,
    tag integer  NOT NULL,
    wallpaper text NOT NULL
    );"""
    )
    c.execute(
        """ CREATE UNIQUE INDEX IF NOT EXISTS
    tagWallpaper ON wtags (tag,wallpaper)
    """
    )
    c.execute(
        """CREATE TABLE IF NOT EXISTS categories(
    id INTEGER PRIMARY KEY  ,
    name text  NOT NULL UNIQUE,
    category text NOT NULL DEFAULT "s"
    );"""
    )
    c.execute(
        """CREATE TABLE IF NOT EXISTS "tags" (
        "id"	INTEGER,
        "tag"	integer NOT NULL UNIQUE,
        "name"	text NOT NULL,
        "alias"	text NOT NULL,
        "category"	text NOT NULL,
        "value"	INTEGER,
        PRIMARY KEY("id")
    ) """
    )
    c.execute(
        """CREATE UNIQUE INDEX IF NOT EXISTS
    "tagName" ON "tags" ( "tag", "name" )"""
    )
    c.execute(
        """CREATE TABLE IF NOT EXISTS favs(
    id INTEGER PRIMARY KEY  ,
    fid integer NOT NULL,
    name text  NOT NULL
    );"""
    )
    c.execute(
        """ CREATE UNIQUE INDEX IF NOT EXISTS
    fidname ON favs (fid,name)
    """
    )
    c.execute(
        """CREATE TABLE IF NOT EXISTS favslist(
    id INTEGER PRIMARY KEY  ,
    name text  NOT NULL UNIQUE,
    category text NOT NULL DEFAULT "s"
    ) """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS "whistory" (
        "id"	INTEGER NOT NULL,
        "name"	text NOT NULL DEFAULT '' UNIQUE,
        "value"	text NOT NULL DEFAULT '0',
        PRIMARY KEY("id")
    ); """
    )
    c.execute(
        """CREATE TABLE IF NOT EXISTS
        wsTags(name text, tag integer ) """
    )
    c.execute(
        """ CREATE UNIQUE INDEX IF NOT EXISTS
        wstag ON wsTags (name,tag) """
    )
    c.execute(
        """CREATE TABLE IF NOT EXISTS dimensions(
        name text  NOT NULL UNIQUE,
        x INTEGER,
        y INTEGER
    ) """
    )
    con.commit()
    c.close()
    con.close()


def where_c(c):
    where = ""
    if c == "d" or c == "x" or c == "s" or c == "m":
        where = """  where ( category="{c}" ) """.format(c=c)
    if c == "ms" or c == "sm":
        where = """ where  ( category="s" or category= "m" ) """
    if c == "md" or c == "dm":
        where = """ where ( category="d" or category= "m" ) """
    return where


def hash_password(password):
    salt = uuid.uuid4().hex
    s = hashlib.sha256(salt.encode() + password.encode()).hexdigest()
    return s + ":" + salt


def addPass(user, passw):
    try:
        con = connectDB()
        c = con.cursor()
        passw = hash_password(passw)
        c.execute(
            """
        INSERT OR IGNORE INTO PASSWORDS (user,password)
        VALUES ("{u}","{p}") """.format(
                u=user, p=passw
            )
        )
        con.commit()
        c.close()
    except sqlite3.Error as error:
        eprint("@%s: %s" % (inspect.stack()[0][3], error))
    finally:
        if con:
            con.close()


def check_password(hashed_password, user_password):
    password, salt = hashed_password.split(":")
    upass = hashlib.sha256(salt.encode() + user_password.encode()).hexdigest()
    return password == upass


def authenticate(user, password):
    r = 0
    try:
        con = connectDB()
        c = con.cursor()
        c.execute(
            """SELECT password FROM PASSWORDS
                  WHERE user = "{user}" """.format(
                user=user
            )
        )
        row = c.fetchone()
        if row:
            r = check_password(row[0], password)
        c.close()
    except sqlite3.Error as error:
        eprint("@%s: %s" % (inspect.stack()[0][3], error))
    finally:
        if con:
            con.close()
    if r:
        print(1)
    else:
        print(0)


def starTag(tag, stars):
    try:
        con = connectDB()
        c = con.cursor()
        c.execute(
            """ UPDATE tags SET
        value="{s}" WHERE tag="{t}"
        """.format(
                t=tag, s=stars
            )
        )
        con.commit()
        c.close()
    except sqlite3.Error as error:
        eprint("@%s: %s" % (inspect.stack()[0][3], error))
    finally:
        if con:
            con.close()


def updatePaths():
    try:
        con = connectDB()
        c = con.cursor()
        with open("/tmp/wchanger_update_file.csv") as ifile:
            reader = csv.reader(ifile)
            for field in reader:
                c.execute(
                    """ INSERT INTO downloaded (name,dir,path)
                VALUES ("{n}", "{d}", "{p}" )
                ON CONFLICT(name) DO UPDATE SET
                dir="{d}" , path="{p}" ;
                """.format(
                        n=field[0], d=field[1], p=field[2]
                    )
                )
        con.commit()
        c.close()
    except sqlite3.Error as error:
        eprint("@%s: %s" % (inspect.stack()[0][3], error))
    finally:
        if con:
            con.close()


def addDim(name, x, y):
    try:
        con = connectDB()
        c = con.cursor()
        c.execute(
            """
                  INSERT OR IGNORE INTO dimensions (name, x, y)
                  VALUES("{name}", "{x}", "{y}")
                  """.format(
                name=name, x=x, y=y
            )
        )
        con.commit()
        c.close()
    except sqlite3.Error as error:
        eprint("@%s: %s" % (inspect.stack()[0][3], error))
    finally:
        if con:
            con.close()


def wHistory_set(name, value):
    try:
        con = connectDB()
        c = con.cursor()
        c.execute(
            """
        INSERT INTO whistory (name, value)
        VALUES("{name}", "{value}")
        ON CONFLICT(name) DO UPDATE SET
        name="{name}" , value="{value}"
         """.format(
                name=name, value=value
            )
        )
        con.commit()
        c.close()
    except sqlite3.Error as error:
        eprint("@%s: %s" % (inspect.stack()[0][3], error))
    finally:
        if con:
            con.close()


def getAllFavs():
    try:
        con = connectDB()
        c = con.cursor()
        c.execute("""select name from favs""")
        rows = c.fetchall()
        for row in rows:
            print(row[0])
        c.close()
    except sqlite3.Error as error:
        eprint("@%s: %s" % (inspect.stack()[0][3], error))
    finally:
        if con:
            con.close()


def wHistory_get(name):
    try:
        con = connectDB()
        c = con.cursor()
        c.execute(
            """ select value from whistory
                  where name="{name}"
        """.format(
                name=name
            )
        )
        row = c.fetchone()
        if row:
            print(row[0])
        c.close()
    except sqlite3.Error as error:
        eprint("@%s: %s" % (inspect.stack()[0][3], error))
    finally:
        if con:
            con.close()


def addWTAG(tag, wallpaper):
    try:
        con = connectDB()
        c = con.cursor()
        c.execute(
            """
        INSERT OR IGNORE INTO wtags (tag,wallpaper)
        VALUES("{t}","{w}")
        """.format(
                t=tag, w=wallpaper
            )
        )
        con.commit()
        c.close()
    except sqlite3.Error as error:
        eprint("@%s: %s" % (inspect.stack()[0][3], error))
    finally:
        if con:
            con.close()


def addWSTAG(name, tag):
    try:
        con = connectDB()
        c = con.cursor()
        c.execute(
            """
        INSERT OR IGNORE INTO wsTags (name,tag)
        VALUES("{n}","{t}")
        """.format(
                n=name, t=tag
            )
        )
        con.commit()
        c.close()
    except sqlite3.Error as error:
        eprint("@%s: %s" % (inspect.stack()[0][3], error))
    finally:
        if con:
            con.close()


def rmWTAG(tag, wallpaper):
    try:
        con = connectDB()
        c = con.cursor()
        c.execute(
            """
                  DELETE from wtags where
                  wallpaper="{w}" and tag="{t}"
                  """.format(
                w=wallpaper, t=tag
            )
        )
        con.commit()
        c.close()
    except sqlite3.Error as error:
        eprint("@%s: %s" % (inspect.stack()[0][3], error))
    finally:
        if con:
            con.close()


def rmWSTAG(name, tag):
    try:
        con = connectDB()
        c = con.cursor()
        c.execute(
            """
        DELETE from wsTags where
        name="{n}" and tag="{t}"
        """.format(
                n=name, t=tag
            )
        )
        con.commit()
        c.close()
    except sqlite3.Error as error:
        eprint("@%s: %s" % (inspect.stack()[0][3], error))
    finally:
        if con:
            con.close()


def addFav(fid, name):
    try:
        con = connectDB()
        c = con.cursor()
        c.execute(
            """
        INSERT INTO favs (name, fid)
        VALUES("{name}","{fid}")
        """.format(
                name=name, fid=fid
            )
        )
        con.commit()
        c.close()
    except sqlite3.Error as error:
        eprint("@%s: %s" % (inspect.stack()[0][3], error))
    finally:
        if con:
            con.close()


def rmFav(name, fid):
    try:
        con = connectDB()
        c = con.cursor()
        c.execute(
            """ DELETE FROM favs
        WHERE name = "{name}"
        AND fid = "{fid}" """.format(
                name=name, fid=fid
            )
        )
        con.commit()
        c.close()
    except sqlite3.Error as error:
        eprint("@%s: %s" % (inspect.stack()[0][3], error))
    finally:
        if con:
            con.close()


def addFile(name, mdir, path):
    try:
        con = connectDB()
        c = con.cursor()
        query = """
        INSERT INTO downloaded (name,dir, path)
        VALUES("{name}","{mdir}", "{path}")
        ON CONFLICT(name) DO UPDATE SET
        name="{name}" , dir="{mdir}" , path="{path}"
        """.format(
            name=name, mdir=mdir, path=path
        )
        c.execute(query)
        con.commit()
        c.close()
    except sqlite3.Error as error:
        eprint("@%s: %s" % (inspect.stack()[0][3], error))
    finally:
        if con:
            con.close()


def createTag(tag, name, alias, category):
    try:
        con = connectDB()
        c = con.cursor()
        query = """ insert OR ignore INTO tags
        (`tag`, `name`,`alias`,`category`)
        VALUES("{t}", "{n}" , "{a}", "{c}")
        """.format(
            t=tag, n=name, a=alias, c=category
        )
        c.execute(query)
        con.commit()
        c.close()
    except sqlite3.Error as error:
        eprint("@%s: %s" % (inspect.stack()[0][3], error))
    finally:
        if con:
            con.close()


def addFavList(name, category):
    try:
        con = connectDB()
        c = con.cursor()
        c.execute(
            """ insert INTO favslist
        (`name`,`category`) VALUES("{n}","{c}")
         """.format(
                n=name, c=category
            )
        )
        con.commit()
        c.close()
    except sqlite3.Error as error:
        eprint("@%s: %s" % (inspect.stack()[0][3], error))
    finally:
        if con:
            con.close()


def getFavName(mid):
    try:
        con = connectDB()
        c = con.cursor()
        c.execute(
            """ select name from favslist
        where id="{mid}" """.format(
                mid=mid
            )
        )
        row = c.fetchone()
        if row:
            print(row[0])
        c.close()
    except sqlite3.Error as error:
        eprint("@%s: %s" % (inspect.stack()[0][3], error))
    finally:
        if con:
            con.close()


def getWSTAGS_f(name):
    try:
        con = connectDB()
        c = con.cursor()
        c.execute(
            """ select tag from wsTags where
        name="{n}" """.format(
                n=name
            )
        )
        rows = c.fetchall()
        c.close()
    except sqlite3.Error as error:
        eprint("@%s: %s" % (inspect.stack()[0][3], error))
    finally:
        if con:
            con.close()
    return tuple(r[0] for r in rows)


def getWSTAGS(name):
    rows = getWSTAGS_f(name)
    for row in rows:
        print(row)


def getFavList(category):
    try:
        con = connectDB()
        c = con.cursor()
        where = where_c(category)
        c.execute(
            """ select * from favslist {where}
        """.format(
                where=where
            )
        )
        rows = c.fetchall()
        for row in rows:
            print("%d:%s" % (row[0], row[1]))
        c.close()
    except sqlite3.Error as error:
        eprint("@%s: %s" % (inspect.stack()[0][3], error))
    finally:
        if con:
            con.close()


def fileExists(name):
    try:
        con = connectDB()
        c = con.cursor()
        c.execute(
            """ select id from downloaded where
        name="{name}" """.format(
                name=name
            )
        )
        rows = c.fetchone()
        if rows:
            n = len(rows)
        else:
            n = 0
        print(n)
        c.close()
    except sqlite3.Error as error:
        eprint("@%s: %s" % (inspect.stack()[0][3], error))
    finally:
        if con:
            con.close()


def getFileByID(mid):
    try:
        con = connectDB()
        c = con.cursor()
        c.execute(
            """ select path from downloaded
        where id={mid} """.format(
                mid=mid
            )
        )
        row = c.fetchone()
        if row:
            print(row[0])
        c.close()
    except sqlite3.Error as error:
        eprint("@%s: %s" % (inspect.stack()[0][3], error))
    finally:
        if con:
            con.close()


def getFileByName(name):
    try:
        con = connectDB()
        c = con.cursor()
        c.execute(
            """ select path from downloaded
        where name="{name}" """.format(
                name=name
            )
        )
        row = c.fetchone()
        if row:
            print(row[0])
        c.close()
    except sqlite3.Error as error:
        eprint("@%s: %s" % (inspect.stack()[0][3], error))
    finally:
        if con:
            con.close()


def getALL():
    try:
        con = connectDB()
        c = con.cursor()
        c.execute(
            """ select path from downloaded
        where path <> ""
        ORDER BY path asc; """
        )
        rows = c.fetchall()
        for row in rows:
            print(row[0])
        c.close()
    except sqlite3.Error as error:
        eprint("@%s: %s" % (inspect.stack()[0][3], error))
    finally:
        if con:
            con.close()


def getCategoryByName(name):
    try:
        con = connectDB()
        c = con.cursor()
        c.execute(
            """select t1.category from categories t1
        inner join downloaded t2
        on t1.name = t2.name
        where t2.name="{name}" """.format(
                name=name
            )
        )
        row = c.fetchone()
        if row:
            print(row[0])
        c.close()
    except sqlite3.Error as error:
        eprint("@%s: %s" % (inspect.stack()[0][3], error))
    finally:
        if con:
            con.close()


def resetCategories():
    try:
        con = connectDB()
        c = con.cursor()
        c.execute(
            """select t1.category from categories t1
        inner join downloaded t2
        on t1.name = t2.name
        where t2.name="name" ; """
        )
        row = c.fetchone()
        if row:
            print(row[0])
        c.close()
    except sqlite3.Error as error:
        eprint("@%s: %s" % (inspect.stack()[0][3], error))
    finally:
        if con:
            con.close()


def getFavs(fid):
    try:
        con = connectDB()
        c = con.cursor()
        c.execute(
            """ select t1.path, t2.id from downloaded t1
        left join favs t2
        on t1.name = t2.name
        where t2.fid = "{fid}"
        order by t2.id asc """.format(
                fid=fid
            )
        )
        rows = c.fetchall()
        for row in rows:
            print("%s:%s" % (row[1], row[0]))
        c.close()
    except sqlite3.Error as error:
        eprint("@%s: %s" % (inspect.stack()[0][3], error))
    finally:
        if con:
            con.close()


def getFav(fid, index):
    try:
        con = connectDB()
        c = con.cursor()
        index = int(index)
        if index >= 1:
            index = index - 1
        c.execute(
            """
        select t1.path from downloaded t1
        inner join favs t2
        on t1.name = t2.name
        where t2.fid = "{fid}"
        ORDER BY t2.id LIMIT {index} ,1
        """.format(
                fid=fid, index=index
            )
        )
        # ORDER BY rand() LIMIT 0,1 "
        row = c.fetchone()
        if row:
            print(row[0])
    except sqlite3.Error as error:
        eprint("@%s: %s" % (inspect.stack()[0][3], error))
    finally:
        if con:
            con.close()


def getFcount(fid):
    try:
        con = connectDB()
        c = con.cursor()
        c.execute(
            """ select id from favs
        where fid = "{fid}"
        order by id asc """.format(
                fid=fid
            )
        )
        rows = c.fetchall()
        if rows:
            n = len(rows)
        else:
            n = 0
        print(n)
    except sqlite3.Error as error:
        eprint("@%s: %s" % (inspect.stack()[0][3], error))
    finally:
        if con:
            con.close()


def orphanedFavs():
    try:
        con = connectDB()
        c = con.cursor()
        c.execute(
            """select t1.name from favs t1
        left join favslist t2
        on t1.fid = t2.id
        WHERE t2.id IS NULL """
        )
        rows = c.fetchall()
        if rows:
            n = len(rows)
        else:
            n = 0
        if n == 0:
            print("""no orphaned id found""")
        else:
            print(
                """these names exist in favs
                   table and their fid no longer exists \n"""
            )
            for row in rows:
                print(row[0])
        c.close()
    except sqlite3.Error as error:
        eprint("@%s: %s" % (inspect.stack()[0][3], error))
    finally:
        if con:
            con.close()


def resetRemoved():
    try:
        con = connectDB()
        c = con.cursor()
        c.execute(
            """ delete from categories
        where name in (
            select name from downloaded where path = ""
        ) ; """
        )
        c.execute(
            """ delete from favs
        where name in (
            select name from downloaded where path = ""
        ) ; """
        )
        c.execute(
            """ delete from wtags
        where wallpaper in (
            select name from downloaded where path = ""
        ) ; """
        )
        con.commit()
        c.close()
    except sqlite3.Error as error:
        eprint("@%s: %s" % (inspect.stack()[0][3], error))
    finally:
        if con:
            con.close()


# //def getDuplicates(){
#     //    c.execute("""SELECT name, COUNT(*) c FROM downloaded
# GROUP BY name HAVING c > 1;""")
#     //
#


def fixPath(name):
    try:
        con = connectDB()
        c = con.cursor()
        c.execute(
            """update downloaded set path="", dir=""
                  where name="{name}" """.format(
                name=name
            )
        )
        con.commit()
        c.close()
    except sqlite3.Error as error:
        eprint("@%s: %s" % (inspect.stack()[0][3], error))
    finally:
        if con:
            con.close()


def getFCategory(fid):
    try:
        con = connectDB()
        c = con.cursor()
        c.execute(
            """ select category from favslist
        where id="{fid}" """.format(
                fid=fid
            )
        )
        row = c.fetchone()
        if row:
            print(row[0])
        con.commit()
        c.close()
    except sqlite3.Error as error:
        eprint("@%s: %s" % (inspect.stack()[0][3], error))
    finally:
        if con:
            con.close()


def getUncategorised():
    try:
        con = connectDB()
        c = con.cursor()
        c.execute(
            """select t1.path from downloaded t1
        left join categories t2
        on t1.name = t2.name
        WHERE t2.id IS NULL and t1.path <> "" """
        )
        rows = c.fetchall()
        for row in rows:
            print(row[0])
        c.close()
    except sqlite3.Error as error:
        eprint("@%s: %s" % (inspect.stack()[0][3], error))
    finally:
        if con:
            con.close()


def fixCategory(name, category):
    try:
        con = connectDB()
        c = con.cursor()
        c.execute(
            """
        INSERT INTO categories (name, category)
        VALUES("{name}", "{c}")
        ON CONFLICT(name) DO UPDATE SET
        name="{name}" , category="{c}"
        """.format(
                name=name, c=category
            )
        )
        con.commit()
        c.close()
    except sqlite3.Error as error:
        eprint("@%s: %s" % (inspect.stack()[0][3], error))
    finally:
        if con:
            con.close()


def getOrederedCount(category):
    try:
        con = connectDB()
        c = con.cursor()
        where = where_c(category)
        c.execute(
            """ select path from downloaded t1
        inner join categories t2
        on t2.name = t1.name {where}  ORDER BY t1.id
        """.format(
                where=where
            )
        )
        rows = c.fetchall()
        if rows:
            n = len(rows)
        else:
            n = 0
        print(n)
        c.close()
    except sqlite3.Error as error:
        eprint("@%s: %s" % (inspect.stack()[0][3], error))
    finally:
        if con:
            con.close()


def getDir(mdir, category, index, n):
    try:
        con = connectDB()
        c = con.cursor()
        index = int(index)
        where = where_c(category)
        c.execute(
            """ select path from downloaded t1
        inner join categories t2
        on t1.name = t2.name {where} and ( t1.dir = "{mdir}" )
        ORDER BY t1.id
        LIMIT {index},{n}
        """.format(
                where=where, mdir=mdir, index=index, n=n
            )
        )
        rows = c.fetchall()
        for row in rows:
            print(row[0])
        c.close()
    except sqlite3.Error as error:
        eprint("@%s: %s" % (inspect.stack()[0][3], error))
    finally:
        if con:
            con.close()


def getDirs(category):
    try:
        con = connectDB()
        c = con.cursor()
        where = where_c(category)
        c.execute(
            """ select DISTINCT dir from downloaded t1
        inner join categories t2
        on t1.name = t2.name {where}
        """.format(
                where=where
            )
        )
        rows = c.fetchall()
        for row in rows:
            print(row[0])
        c.close()
    except sqlite3.Error as error:
        eprint("@%s: %s" % (inspect.stack()[0][3], error))
    finally:
        if con:
            con.close()


def getDirCount(mdir, category):
    try:
        con = connectDB()
        c = con.cursor()
        where = where_c(category)
        c.execute(
            """ select path from downloaded t1
        inner join categories t2
        on t1.name = t2.name {where} and ( dir = "{mdir}" )
        ORDER BY t1.id
        """.format(
                where=where, mdir=mdir
            )
        )
        rows = c.fetchall()
        if rows:
            n = len(rows)
        else:
            n = 0
        print(n)
        c.close()
    except sqlite3.Error as error:
        eprint("@%s: %s" % (inspect.stack()[0][3], error))
    finally:
        if con:
            con.close()


def getOredered(category, index, n):
    try:
        con = connectDB()
        c = con.cursor()
        index = int(index)
        if index >= 1:
            index = index - 1
        where = where_c(category)
        c.execute(
            """ select path from downloaded t1
        inner join categories t2
        on t2.name = t1.name
        {w}
        ORDER BY t1.id desc
        LIMIT {i},{n}
         """.format(
                w=where, i=index, n=n
            )
        )
        rows = c.fetchall()
        for row in rows:
            print(row[0])
        c.close()
    except sqlite3.Error as error:
        eprint("@%s: %s" % (inspect.stack()[0][3], error))
    finally:
        if con:
            con.close()


def getFavListByName(name):
    try:
        con = connectDB()
        c = con.cursor()
        c.execute(
            """ select t1.id, t1.name from favslist t1
        inner join favs t2
        on t2.fid = t1.id
        where t2.name="{name}" """.format(
                name=name
            )
        )
        rows = c.fetchall()
        for row in rows:
            print("%s:%s" % (row[0], row[1]))
        c.close()
    except sqlite3.Error as error:
        eprint("@%s: %s" % (inspect.stack()[0][3], error))
    finally:
        if con:
            con.close()


def getTagsLike(category, pattern):
    try:
        con = connectDB()
        c = con.cursor()
        where = where_c(category)
        if where == "":
            where = """where name like "%{p}%" """.format(p=pattern)
        else:
            where += """and name like "%{p}%" """.format(p=pattern)
        c.execute(
            """select tag,name,category from tags
                     {where}
                  order by tag asc """.format(
                where=where, p=pattern
            )
        )
        rows = c.fetchall()
        for row in rows:
            print("%s:%s:%s" % (row[0], row[1], row[2]))
            c.close()
    except sqlite3.Error as error:
        eprint("@%s: %s" % (inspect.stack()[0][3], error))
    finally:
        if con:
            con.close()


def getTagsByStars(category, stars):
    where = where_c(category)
    if where == "":
        where = '''where value="''' + stars + '''"'''
    else:
        where += '''and value="''' + stars + '''"'''
    try:
        con = connectDB()
        c = con.cursor()
        c.execute(
            """select tag,name,category from tags
            {w} order by tag asc """.format(
                w=where
            )
        )
        rows = c.fetchall()
        for row in rows:
            print("%s:%s:%s" % (row[0], row[1], row[2]))
            c.close()
    except sqlite3.Error as error:
        eprint("@%s: %s" % (inspect.stack()[0][3], error))
    finally:
        if con:
            con.close()


def getTags(category):
    try:
        con = connectDB()
        c = con.cursor()
        where = where_c(category)
        c.execute(
            """select tag,name,category from tags
        {where} order by tag asc """.format(
                where=where
            )
        )
        rows = c.fetchall()
        for row in rows:
            print("%s:%s:%s" % (row[0], row[1], row[2]))
        c.close()
    except sqlite3.Error as error:
        eprint("@%s: %s" % (inspect.stack()[0][3], error))
    finally:
        if con:
            con.close()


def getWebIds(category):
    try:
        con = connectDB()
        c = con.cursor()
        where = where_c(category)
        c.execute(
            """select name from tags {where}
         """.format(
                where=where
            )
        )
        rows = c.fetchall()
        for row in rows:
            print(row[0])
        c.close()
    except sqlite3.Error as error:
        eprint("@%s: %s" % (inspect.stack()[0][3], error))
    finally:
        if con:
            con.close()


def getRandom(category):
    try:
        con = connectDB()
        c = con.cursor()
        c.execute(
            """ select path from downloaded t1
        inner join categories t2
        on t2.name = t1.name
        where t2.category="{c}"
        order by RANDOM()
        limit 1 """.format(
                c=category
            )
        )
        row = c.fetchone()
        if row:
            print(row[0])
        c.close()
    except sqlite3.Error as error:
        eprint("@%s: %s" % (inspect.stack()[0][3], error))
    finally:
        if con:
            con.close()


def lastName():
    try:
        con = connectDB()
        c = con.cursor()
        c.execute(
            """select name from downloaded
        order by name desc limit 1 ;"""
        )
        row = c.fetchone()
        print(row[0])
        c.close()
    except sqlite3.Error as error:
        eprint("@%s: %s" % (inspect.stack()[0][3], error))
    finally:
        if con:
            con.close()


def getTagC(tag):
    try:
        con = connectDB()
        c = con.cursor()
        c.execute(
            """select category from tags where tag="{tag}"
         """.format(
                tag=tag
            )
        )
        row = c.fetchone()
        if row:
            print(row[0])
        c.close()
    except sqlite3.Error as error:
        eprint("@%s: %s" % (inspect.stack()[0][3], error))
    finally:
        if con:
            con.close()


def getTagID(name):
    try:
        con = connectDB()
        c = con.cursor()
        c.execute(
            """select tag from tags where name="{n}"
         """.format(
                n=name
            )
        )
        row = c.fetchone()
        if row:
            print(row[0])
        c.close()
    except sqlite3.Error as error:
        eprint("@%s: %s" % (inspect.stack()[0][3], error))
    finally:
        if con:
            con.close()


def getWSTAGSWP(name, ct, index, n, o="AND"):
    tags = tuple(getWSTAGS_f(name))
    length = len(tags)
    count = 0
    index = int(index)
    if length < 1:
        return
    if length == 1:
        tags = """({t})""".format(t=tags[0])
    if index < 0:
        index = 0
        count = -1
    where = ""
    if ct == "d" or ct == "x" or ct == "s" or ct == "m":
        where = """ t2.category="{c}" """.format(c=ct)
    if ct == "ms" or ct == "sm":
        where = """ ( t2.category="s" or t2.category= "m" ) """
    if ct == "md" or ct == "dm":
        where = """ ( t2.category="d" or t2.category= "m" ) """
    query = """
    select t1.path from downloaded t1
    inner join categories t2
    on t1.name = t2.name
    where t1.name in
    (
    select wallpaper from wTags where tag in {t}
    GROUP BY wallpaper having count(*) >= {ll}
    )
    and {c}
    LIMIT {i},{n}
    """.format(
        t=tags, ll=length, i=index, n=n, c=where
    )
    if o == "OR":
        query = """
        select t1.path from downloaded t1
        inner join categories t2
        on t1.name = t2.name
        where t1.name in
        (
            select DISTINCT wallpaper from wTags where tag in {t}
        )
        and {c}
        LIMIT {i},{n}
        """.format(
            t=tags, ll=length, i=index, n=n, c=where
        )

    try:
        con = connectDB()
        c = con.cursor()
        c.execute(query)
        rows = c.fetchall()
        if count == -1:
            print(len(rows))
        else:
            for row in rows:
                print(row[0])
        c.close()
    except sqlite3.Error as error:
        eprint("@%s: %s" % (inspect.stack()[0][3], error))
    finally:
        if con:
            con.close()


def unTAGGed():
    try:
        con = connectDB()
        c = con.cursor()
        c.execute(
            """select t1.path from downloaded t1
        left join wtags t2
        on t1.name = t2.wallpaper
        WHERE t2.id IS NULL and t1.path <> ""
        """
        )
        # and  printf("%d", t1.name) <> t1.name ;
        rows = c.fetchall()
        for row in rows:
            print(row[0])
        c.close()
    except sqlite3.Error as error:
        eprint("@%s: %s" % (inspect.stack()[0][3], error))
    finally:
        if con:
            con.close()


def getTagName(tag):
    try:
        con = connectDB()
        c = con.cursor()
        c.execute(
            """select name from tags where tag="{tag}"
         """.format(
                tag=tag
            )
        )
        row = c.fetchone()
        if row:
            print(row[0])
        c.close()
    except sqlite3.Error as error:
        eprint("@%s: %s" % (inspect.stack()[0][3], error))
    finally:
        if con:
            con.close()


def wallpaperTags(wallpaper):
    try:
        con = connectDB()
        c = con.cursor()
        c.execute(
            """select tag from wtags where wallpaper="{w}"
                  """.format(
                w=wallpaper
            )
        )
        rows = c.fetchall()
        for row in rows:
            print(row[0])
        c.close()
    except sqlite3.Error as error:
        eprint("@%s: %s" % (inspect.stack()[0][3], error))
    finally:
        if con:
            con.close()


def changeList(mid, mlist, category):
    try:
        con = connectDB()
        c = con.cursor()
        c.execute(
            """update favslist
        set name="{mlist}", category="{c}"
        where id="{mid}"
        """.format(
                mlist=mlist, c=category, mid=mid
            )
        )
        con.commit()
        c.close()
    except sqlite3.Error as error:
        eprint("@%s: %s" % (inspect.stack()[0][3], error))
    finally:
        if con:
            con.close()


def myfuncSwitch(arg):
    cmd = arg[1]
    switcher = {
        "addpass": addPass,
        "addfav": addFav,
        "rmfav": rmFav,
        "addfavlist": addFavList,
        "getfav": getFav,
        "getfavs": getFavs,
        "getfcount": getFcount,
        "add": addFile,
        "downloaded": fileExists,
        "get": getFileByName,
        "geti": getFileByID,
        "fixcategory": fixCategory,
        "last": lastName,
        "resetRemoved": resetRemoved,
        "getrandom": getRandom,
        "getfavname": getFavName,
        "getfavlist": getFavList,
        "getfavlistbyname": getFavListByName,
        "wh_set": wHistory_set,
        "wh_get": wHistory_get,
        "getcategorybyname": getCategoryByName,
        "getorderedcount": getOrederedCount,
        "getordered": getOredered,
        "uncategorised": getUncategorised,
        "authenticate": authenticate,
        "getwebids": getWebIds,
        "changelist": changeList,
        "getallfavs": getAllFavs,
        "getdir": getDir,
        "getdircount": getDirCount,
        "getdirs": getDirs,
        "getall": getALL,
        "orphanedfavs": orphanedFavs,
        "gettagc": getTagC,
        "gettagid": getTagID,
        "gettagname": getTagName,
        "getfcategory": getFCategory,
        "fixpath": fixPath,
        "createtag": createTag,
        "gettags": getTags,
        "gettagsbystars": getTagsByStars,
        "gettagslike": getTagsLike,
        "addwtag": addWTAG,
        "updatepaths": updatePaths,
        "addwstag": addWSTAG,
        "getwstags": getWSTAGS,
        "getwstagswp": getWSTAGSWP,
        "rmwstag": rmWSTAG,
        "rmwtag": rmWTAG,
        "star": starTag,
        "wallpapertags": wallpaperTags,
        "untagged": unTAGGed,
        "adddim": addDim,
    }
    func = switcher.get(cmd)
    func(*arg[2:])


def main():
    createDB()
    myfuncSwitch(sys.argv)


if __name__ == "__main__":
    main()
