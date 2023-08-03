import os
import time
import mysql
import mysql.connector

import exceptions


class SqlOrm:
    """all universal query for db and work with exceptions"""

    def __init__(self):
        self.cnx = SqlOrm.reconnect()
        self.repeat_connect = 0

    @staticmethod
    def reconnect():
        """reconnect if there are problems"""

        connect_data = {
            'user': os.environ.get('DB_USER'),
            'password': os.environ.get('DB_PASSWORD'),
            'host': os.environ.get('DB_HOST'),
            'database': os.environ.get('DB_DATABASE'),
            'raise_on_warnings': True
        }

        return mysql.connector.connect(**connect_data)

    def _select_query(self, query, arguments=None) -> list:
        """universal select query"""

        try:
            cursor = self.cnx.cursor()
            if arguments is None:
                cursor.execute(query)
            else:
                cursor.execute(query, arguments)

        except mysql.connector.errors.OperationalError:
            time.sleep(1)

            # control repeat connection
            if self.repeat_connect == 10:
                raise mysql.connector.errors.OperationalError()

            # repeat connect to db
            self.cnx = SqlOrm.reconnect()
            self.repeat_connect += 1

            # repeat select query
            return self._select_query(query, arguments)

        # if connection is good
        self.repeat_connect = 0

        # get data from query
        data_list = []
        for i in cursor:
            data_list.append(i)

        return data_list

    def _update_query(self, query, arguments=None):
        """universal update query"""

        try:
            cursor = self.cnx.cursor()
            if arguments is None:
                cursor.execute(query)
            else:
                cursor.execute(query, arguments)

            self.cnx.commit()

        except mysql.connector.errors.OperationalError:
            time.sleep(1)

            # control repeat connection
            if self.repeat_connect == 10:
                raise mysql.connector.errors.OperationalError()

            # repeat connect to db
            self.cnx = SqlOrm.reconnect()
            self.repeat_connect += 1

            # repeat select query
            self._update_query(query, arguments)


class SqlQuery(SqlOrm):
    """use sql query for work"""

    def get_queue(self):
        """get task from db"""

        query = ("SELECT id, resource_id , entity_id  "
                 "FROM queue WHERE type_id = 11 AND status_id = 1 ORDER BY id LIMIT 1")

        data_from_query = super()._select_query(query=query)

        # get data from query
        data = None
        for i in data_from_query:
            data = {
                'id': i[0],
                'resource_id': i[1],
                'entity_id': i[2]
            }

        if data is None:
            raise exceptions.TaskNotFound()

        return data

    def get_row_for_result(self, id_queue):
        """get row from db for write result"""

        query = "SELECT * FROM queue_position_yandex_map WHERE queue_id = %s"
        data_from_db = super()._select_query(query, (str(id_queue), ))

        # get data from query
        id_for_result = None
        for i in data_from_db:
            id_for_result = i[0]

        if id_for_result is None:
            raise exceptions.ErrorDataDb()

        return id_for_result

    def get_yandex_id(self, entity_id):
        """get id of yandex organisation"""

        query = "SELECT yandex_id, longitude, latitude FROM itemcampagin WHERE id = %s"
        data_from_query = super()._select_query(query, (entity_id,))

        # control coordinates data
        data = None
        for i in data_from_query:
            data = {
                'yandex_id': i[0],
                'longitude': i[1],
                'latitude': i[2]
            }

        if data is None:
            raise exceptions.ErrorDataDb()

        return data

    def get_keyword_coordinates(self, resource_id, entity_id):
        """get keyword and coordinates"""

        # get keyword and coordinates(test)
        query = "SELECT keyword, coordinates FROM position_yandex_map WHERE id = %s"
        data_from_query = super()._select_query(query, (str(resource_id), ))

        # work with data
        data = None
        for i in data_from_query:
            data = {
                'keyword': i[0],
                'coordinates': i[1]
            }

        if data is None:
            raise exceptions.ErrorDataDb()

        # get id of organisation in yandex maps
        data_with_id = self.get_yandex_id(entity_id)
        if data_with_id is None:
            raise exceptions.ErrorDataDb()

        # work with coordinates
        if data.get('coordinates') is None:

            # edit format of coordinates
            data.pop('coordinates')
            data.update({'longitude': data_with_id.get('longitude')})
            data.update({'latitude': data_with_id.get('latitude')})

        else:
            # edit coordinates data
            str_coordinates = data.pop('coordinates')
            data.update({
                'longitude': str_coordinates.split(', ')[1],
                'latitude': str_coordinates.split(', ')[0]
            })

        # get yandex id to main data
        data.update({'yandex_id': data_with_id.get('yandex_id')})

        return data

    def update_status_task(self, task_id, status_id):
        """update status_id for queue"""

        query = "UPDATE queue SET status_id = %s WHERE id = %s"
        super()._update_query(query, (str(status_id), str(task_id)))

    def update_status_task_other(self, queue_id, status_id):
        """update status_id for queue_position_yandex_map"""

        query = "UPDATE queue_position_yandex_map SET status_id = %s WHERE queue_id = %s"
        super()._update_query(query, (str(status_id), str(queue_id)))

    def set_position(self, rad2, rad5, rad10, queue_id):
        """set position on yandex maps"""

        # control types of rad
        if rad2 is None:
            r_2 = 'NULL'
        else:
            r_2 = rad2

        if rad5 is None:
            r_5 = 'NULL'
        else:
            r_5 = rad5

        if rad10 is None:
            r_10 = 'NULL'
        else:
            r_10 = rad10

        # make query
        query = ("UPDATE queue_position_yandex_map "
                 "SET rad_2 = " + str(r_2) + ", rad_5 = " + str(r_5) + ", "
                 "rad_10 = " + str(r_10) + " "
                 "WHERE queue_id = " + str(queue_id))

        super()._update_query(query)
