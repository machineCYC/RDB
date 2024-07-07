# 01-InsetWithMultipleTable

This file will show the common way to inset the data into mysql with multiple tables

- Using SQL cli to inset the data
    - check the ans.sql
- Using Python sqlalchemy to inset the data
    - check the main.py

The testing data is in the data.txt file, and use the bleow SQL to test if your data has been entered properly with the following SQL statement.

```
SELECT `User`.name, Course.title, Member.role
FROM `User` JOIN Member JOIN Course
ON `User`.user_id = Member.user_id AND Member.course_id = Course.course_id
ORDER BY Course.title, Member.role DESC, `User`.name
```

Running the database.sql to create the database, and running the tables to create the tables which we will use
