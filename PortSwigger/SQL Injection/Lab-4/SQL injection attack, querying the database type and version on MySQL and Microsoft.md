
Description : This lab contains a SQL injection vulnerability in the product category filter. You can use a UNION attack to retrieve the results from an injected query.

To solve the lab, display the database version string.


## Solution

I started the lab and there is a normal homepage

![[PortSwigger/SQL Injection/Lab-4/Attachments/HomePage.png]]

After clicking on one of the categories we see that there is a parameter appears on the URL called `category`

![[PortSwigger/SQL Injection/Lab-4/Attachments/Parameter.png]]

I added a `'` to check if it is really vulnerable to `SQLI` and I got an error and this is a good sign

![[ERROR.png]]

we know that we need to do a `UNION SQLI` so let's figure out how many columns we have by using `ORDER BY NUM --+` we will use `--+` as comment because it's `MYSQL` 

```sql
Pets' order by 1--+
```

now we will keep increasing the number until we get an error

![[OrderBy Error.png]]

since we got error on number 3 that means we have 2 columns and now we need to know what type of data they return

```sql
Pets' UNION SELECT NULL,NULL--+
Pets' UNION SELECT 'A',NULL--+@@version
Pets' UNION SELECT NULL,'A'--+
```
After trying all of these payloads we didn't get error on any of them so now we know the 2 columns retrieve `string` 
Now let's try and get the version

```sql
Pets' UNION SELECT 'A',@@version--+
```

![[Solved4.png]]