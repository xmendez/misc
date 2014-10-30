<%@ page import="java.sql.*" %>
<%
   String connectionURL = "jdbc:mysql://localhost:3306/apt-me?user=root;password=c0qipafa";
   Connection connection = null;
   Statement statement = null;
   ResultSet rs = null;
   %>

   

    <%
    Class.forName("com.mysql.jdbc.Driver").newInstance();
    connection = DriverManager.getConnection(connectionURL, "root", "");
    statement = connection.createStatement();
    rs = statement.executeQuery("SELECT * FROM users where id=" + request.getParameter("id"));

    while (rs.next()) {
       out.println(rs.getString("username")+"");
    }

    rs.close();
    %>

