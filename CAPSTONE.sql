CREATE DATABASE FUREVERFAMILY;
GO

USE FUREVERFAMILY
GO

CREATE TABLE USERS (
	ID INT IDENTITY(1,1) PRIMARY KEY,
	[NAME] NVARCHAR(100) NOT NULL UNIQUE,
	[PASSWORD] NVARCHAR(255) NOT NULL,
	ROLE NVARCHAR(50) NOT NULL DEFAULT 'adopter',
	DATE_CREATED DATETIME DEFAULT GETDATE()
)
/*admin account for reference
	name: admin
	pass: admin123
*/



-- Businesses Table (Grooming, Pet Stores, Vets, etc.)
CREATE TABLE BUSINESSES (
    ID INT IDENTITY(1,1) PRIMARY KEY,
    OWNER_ID INT FOREIGN KEY REFERENCES USERS(ID) ON DELETE CASCADE,
    BUSINESS_NAME NVARCHAR(255) NOT NULL UNIQUE,
    CATEGORY NVARCHAR(100) CHECK (Category IN ('Grooming', 'Pet Store', 'Vet Clinic', 'Training')),
    [LOCATION] NVARCHAR(255),
    CONTACT NVARCHAR(100),
    IS_PREMIUM BIT DEFAULT 0,  -- For Subscription Model
    DATE_CREATED DATETIME DEFAULT GETDATE()
);


-- Transactions Table (For Commission-Based Earnings)
CREATE TABLE TRANSACTIONS (
    ID INT IDENTITY(1,1) PRIMARY KEY,
    ADOPTER_ID INT FOREIGN KEY REFERENCES USERS(ID) ON DELETE SET NULL,
    BUSINESS_ID INT FOREIGN KEY REFERENCES BUSINESSES(ID) ON DELETE NO ACTION, -- Prevents cycle error
    AMOUNT DECIMAL(10,2) NOT NULL,
    COMMISSION DECIMAL(10,2) NOT NULL DEFAULT 0, -- Percentage of transaction
    TRANSACTION_DATE DATETIME DEFAULT GETDATE()
);

-- Subscriptions Table (For Recurring Payments from Businesses)
CREATE TABLE SUBSCRIPTIONS (
    ID INT IDENTITY(1,1) PRIMARY KEY,
    BUSINESS_ID INT FOREIGN KEY REFERENCES BUSINESSES(ID) ON DELETE CASCADE,
    [PLAN] NVARCHAR(50) CHECK ([PLAN] IN ('Free', 'Premium')),
    PRICE DECIMAL(10,2) NOT NULL DEFAULT 0,
    START_DATE DATETIME DEFAULT GETDATE(),
    END_DATE DATETIME NOT NULL
);

-- Featured Listings Table (For Paid Ads from Businesses)
CREATE TABLE FEATURED_LISTINGS (
    ID INT IDENTITY(1,1) PRIMARY KEY,
    BUSINESS_ID INT FOREIGN KEY REFERENCES BUSINESSES(ID) ON DELETE CASCADE,
    PRICE DECIMAL(10,2) NOT NULL,
    START_DATE DATETIME DEFAULT GETDATE(),
    END_DATE DATETIME NOT NULL
);

--Pet table
CREATE TABLE PETS (
	IMAGE NVARCHAR(255) NULL, -- Store image path
    ID INT IDENTITY(1,1) PRIMARY KEY,
    PET_NAME NVARCHAR(100) NOT NULL,
    AGE INT NOT NULL,
    SEX NVARCHAR(10) CHECK (SEX IN ('Male', 'Female')),
    STATUS NVARCHAR(50) DEFAULT 'Available',
    DATE_ADDED DATETIME DEFAULT GETDATE(),
	SHELTER NVARCHAR(255) NOT NULL
);

DROP TABLE PETS

SELECT * FROM PETS


UPDATE USERS
SET ROLE = 'admin'
WHERE NAME = 'admin'


SELECT * FROM USERS


SELECT NAME, PASSWORD FROM users;