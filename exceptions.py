class TaskNotFound(Exception):
    """error if there are no new tasks in the database"""

    pass


class ErrorDataDb(Exception):
    """error in struct of data in db"""

    pass
