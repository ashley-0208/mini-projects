-- Create database
CREATE DATABASE StudentDB;
GO

-- Use the database
USE StudentDB;
GO

-- Create table
CREATE TABLE StudentInfo (
    ID INT IDENTITY(1,1) PRIMARY KEY,
    FullName NVARCHAR(100) NOT NULL,
    StudentNUM NVARCHAR(20) NOT NULL UNIQUE,
    Major NVARCHAR(50) NOT NULL,
    Semester INT NOT NULL
);
