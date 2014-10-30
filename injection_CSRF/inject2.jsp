<%@ page import = "java.sql.*"%>
<%@ page import = "java.io.*"%>

<%

DriverManager.registerDriver(new oracle.jdbc.driver.OracleDriver());
//register driver
Class.forName("sun.jdbc.odbc.JdbcOdbcDriver");
//get the database connection
Connection con =
DriverManager.getConnection("jdbc:oracle:thin:@172.18.1.173:1521:ORCL", "scott", "tiger");
// Create statement
Statement stmt = con.createStatement ();
ResultSet rs = stmt.executeQuery ("select * from dept where deptno=" +  request.getParameter("id"));
%>

<html>
<body>

<h1>injectable

<%
// Iterar mientras haya datos.
out.println("hello" );
%>

<%
while (rs.next ())
{
	out.println(rs.getString ("dname"));
}

%>

</body>
</html>
