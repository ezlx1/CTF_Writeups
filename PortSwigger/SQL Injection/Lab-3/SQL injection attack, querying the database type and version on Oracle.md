

Description : This lab contains a SQL injection vulnerability in the product category filter. You can use a UNION attack to retrieve the results from an injected query.

To solve the lab, display the database version string.



## Solution

After starting up the lab we see a home page with paragraphs and a filtering buttons
After clicking on the `Pets` we see that there is a parameter showed up on the URL
And we want to do `UNION SQLI`



' UNION SELECT banner, null FROM v$version --




![[Solved3.png]]