def insertion_sort_by_field(students, field):
    for index in range(1, len(students)):
        key_student = students[index]
        position = index - 1

        # Shift larger values right until the key belongs at this position.
        while position >= 0 and students[position][field] > key_student[field]:
            students[position + 1] = students[position]
            position -= 1

        students[position + 1] = key_student

    return students


def binary_search_by_name(sorted_by_name_list, name):
    low = 0
    high = len(sorted_by_name_list) - 1

    while low <= high:
        mid = low + (high - low) // 2
        student = sorted_by_name_list[mid]

        if student["name"] == name:
            return student
        if student["name"] < name:
            low = mid + 1
        else:
            high = mid - 1

    return -1


def format_roster_report(students):
    lines = []
    for student in students:
        lines.append(f"[Age {student['age']}] {student['name']} <{student['email']}>")
    return "\n".join(lines)


def count_students_meeting_min_age(students, min_age):
    count = 0
    for student in students:
        if student["age"] >= min_age:
            count += 1
    return count
