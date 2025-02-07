import pandas as pd
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'education_system.envs.development')
django.setup()

from course.models import Course, Category

read_course_data = pd.read_csv("edit_course_data.csv")

# read_course_data['course_price'] = read_course_data['course_price'].replace(r"\$", "", regex=True)


# print(read_course_data.columns)
# read_course_data.rename(columns={'category_id': "category_id"}, inplace=True)
# read_course_data.to_csv("edit_course_data.csv", index=False)

list_data_add = []
for i, j in read_course_data.iterrows():
    list_data_add.append(Course(
        category_id=j['category_id'],
        course_name=j['course_name'],
        course_duration=j['course_duration'],
        course_description=j['course_description'],
        course_price=j['course_price'],
    )
    )
# Course.objects.bulk_create(list_data_add)
