-- =====================================================================
-- 01_schema.sql
-- Core tables mirroring SAP B1 exports used by the procurement project.
-- Written in ANSI/SQLite-compatible SQL; column types map directly onto
-- SQL Server types if pointing this at the real SAP B1 (MSSQL/HANA) DB:
--   TEXT -> NVARCHAR, REAL -> DECIMAL(18,2), plain DATE strings -> DATE
-- =====================================================================

DROP TABLE IF EXISTS Vendor_Master;
CREATE TABLE Vendor_Master (
    VendorCode          TEXT PRIMARY KEY,
    VendorName          TEXT,
    Vertical            TEXT,
    City                TEXT,
    State               TEXT,
    GSTIN               TEXT,
    ContactPerson       TEXT,
    Phone               TEXT,
    Email               TEXT,
    OnboardDate         DATE,
    PaymentTerms        TEXT,
    VendorRatingInternal REAL,
    IsActive            TEXT
);

DROP TABLE IF EXISTS Material_Master;
CREATE TABLE Material_Master (
    ItemCode        TEXT PRIMARY KEY,
    ItemDescription TEXT,
    Vertical        TEXT,
    UOM             TEXT,
    StandardPrice   REAL,
    HSNCode         TEXT,
    PreferredBrand  TEXT,
    ItemGroup       TEXT
);

DROP TABLE IF EXISTS Department_Project_Master;
CREATE TABLE Department_Project_Master (
    DeptCode            TEXT PRIMARY KEY,
    DeptName            TEXT,
    ProjectCode         TEXT,
    ProjectName         TEXT,
    BudgetAllocatedINR  REAL
);

DROP TABLE IF EXISTS Warehouse_Master;
CREATE TABLE Warehouse_Master (
    WarehouseCode TEXT PRIMARY KEY,
    WarehouseName TEXT
);

DROP TABLE IF EXISTS PR_Data;
CREATE TABLE PR_Data (
    PRNo            TEXT PRIMARY KEY,
    PRDate          DATE,
    DeptCode        TEXT,
    DeptName        TEXT,
    ProjectCode     TEXT,
    ProjectName     TEXT,
    ItemCode        TEXT,
    ItemDescription TEXT,
    Vertical        TEXT,
    RequestedQty    INTEGER,
    UOM             TEXT,
    RequiredByDate  DATE,
    RequestedBy     TEXT,
    Priority        TEXT,
    Status          TEXT
);

DROP TABLE IF EXISTS PO_Data;
CREATE TABLE PO_Data (
    PONo                    TEXT PRIMARY KEY,
    PODate                  DATE,
    PRNo                    TEXT,
    VendorCode              TEXT,
    VendorName              TEXT,
    Vertical                TEXT,
    ItemCode                TEXT,
    ItemDescription         TEXT,
    OrderedQty              INTEGER,
    UOM                     TEXT,
    UnitPrice               REAL,
    TotalAmount             REAL,
    Currency                TEXT,
    PromisedDeliveryDate    DATE,
    PaymentTerms            TEXT,
    ApprovedBy              TEXT,
    Status                  TEXT,
    DeptCode                TEXT,
    ProjectCode             TEXT,
    FOREIGN KEY (PRNo) REFERENCES PR_Data(PRNo),
    FOREIGN KEY (VendorCode) REFERENCES Vendor_Master(VendorCode)
);

DROP TABLE IF EXISTS GRN_Data;
CREATE TABLE GRN_Data (
    GRNNo           TEXT PRIMARY KEY,
    GRNDate         DATE,
    PONo            TEXT,
    VendorCode      TEXT,
    WarehouseCode   TEXT,
    ItemCode        TEXT,
    ItemDescription TEXT,
    Vertical        TEXT,
    ReceivedQty     INTEGER,
    AcceptedQty     INTEGER,
    RejectedQty     INTEGER,
    UOM             TEXT,
    InspectedBy     TEXT,
    QCStatus        TEXT,
    FOREIGN KEY (PONo) REFERENCES PO_Data(PONo)
);

DROP TABLE IF EXISTS Invoice_Data;
CREATE TABLE Invoice_Data (
    InvoiceNo       TEXT PRIMARY KEY,
    InvoiceDate     DATE,
    PONo            TEXT,
    GRNNo           TEXT,
    VendorCode      TEXT,
    VendorName      TEXT,
    Vertical        TEXT,
    InvoiceAmount   REAL,
    TaxAmount       REAL,
    TotalAmount     REAL,
    PaymentDueDate  DATE,
    PaymentStatus   TEXT,
    PaymentDate     DATE,
    DeptCode        TEXT,
    ProjectCode     TEXT,
    FOREIGN KEY (PONo) REFERENCES PO_Data(PONo),
    FOREIGN KEY (GRNNo) REFERENCES GRN_Data(GRNNo)
);

DROP TABLE IF EXISTS Inventory_Data;
CREATE TABLE Inventory_Data (
    WarehouseCode   TEXT,
    WarehouseName   TEXT,
    ItemCode        TEXT,
    ItemDescription TEXT,
    Vertical        TEXT,
    UOM             TEXT,
    StockQty        INTEGER,
    ReorderLevel    INTEGER,
    LastReceivedDate DATE,
    LastIssuedDate  DATE,
    AgingDays       INTEGER,
    UnitValue       REAL,
    StockValueINR   REAL,
    StockStatus     TEXT
);

DROP TABLE IF EXISTS Price_History;
CREATE TABLE Price_History (
    Month           TEXT,
    Vertical        TEXT,
    ItemCode        TEXT,
    ItemDescription TEXT,
    VendorCode      TEXT,
    UnitPrice       REAL,
    StandardPrice   REAL
);
