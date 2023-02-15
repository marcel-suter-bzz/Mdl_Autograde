import os
import shelve
from datetime import date

import requests
from dotenv import load_dotenv

from grade import Grade


def main():
    load_dotenv()
    with shelve.open(
            filename=os.getenv('GRADES'),
            flag='w'
    ) as grades_db:
        keys = list(grades_db.keys())
        for key in keys:
            grade = Grade()
            grade.from_dict(grades_db[key])
            age_days = (date.today() - grade.updated).days
            if age_days > 30:
                del grades_db[key]
            elif grade.assignmentid != 0 and grade.points >= 0.0:
                update_moodle(grade)
                grade.points = -1
                grades_db[key] = grade.to_dict()


def update_moodle(grade):
    """
    update the points in the moodle assignment
    :param grade:
    :return:
    """
    url = os.getenv('MOODLEURL') + '?wstoken=' + os.getenv('MOODLETOKEN') + \
          '&wsfunction=mod_assign_save_grade&moodlewsrestformat=json'
    data = {
        'assignmentid': grade.assignmentid,
        'userid': grade.userid,
        'grade': grade.points,
        'attemptnumber': -1,
        'addattempt': 0,
        'workflowstate': 'graded',
        'applytoall': 1
    }

    if os.environ['DEBUG'] == 'False':
        response = requests.post(url, params=data)
        content = response.json()
    else:
        print('update_moodle', data)

if __name__ == '__main__':
    main()
