/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package code;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;

/**
 *
 * @author User
 */
public class DBconnection {
    
    public static Connection connect(){
        Connection conn;
        conn = null;
        try {
            Class.forName("com.mysql.cj.jdbc.Driver"); // Use the updated MySQL driver
            conn = DriverManager.getConnection("jdbc:mysql://localhost:3306/arsoftware", "root", "");
            
        } catch (SQLException|ClassNotFoundException e) {
            System.out.println("There were errors while connecting to DB");
            
            
        }
        return conn;
    }
}
