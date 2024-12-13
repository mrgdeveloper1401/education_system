def course_name(instance, filename):
    name = instance.course.tile.replace(" ", "_")
    date = instance.created_at.strftime("%Y/%m/%d")
    return f"video/{name}/{date}/{filename}"


def practice_name(instance, filename):
    name = instance.practice_title.replace(" ", "_")
    date = instance.created_at.strftime("%Y/%m/%d")
    return f"practice/{name}/{date}/{filename}"
