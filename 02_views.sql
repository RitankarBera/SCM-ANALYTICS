-- =====================================================================
-- 02_views.sql
-- One view per dashboard requirement. Power BI (or the HTML dashboard
-- in this project) connects to these views only -- never to raw tables
-- directly. Because every visual is built on top of a view, refreshing
-- the underlying data (re-running the ETL) and hitting "Refresh" in
-- Power BI/the dashboard updates every report page at once, from the
-- same single source of truth.
-- =====================================================================

-- ---------------------------------------------------------------
-- 1. VENDOR / SUPPLIER PERFORMANCE SCORE + ON-TIME DELIVERY
-- ---------------------------------------------------------------
DROP VIEW IF EXISTS vw_VendorPerformance;
CREATE VIEW vw_VendorPerformance AS
SELECT
    v.VendorCode,
    v.VendorName,
    v.Vertical,
    v.State,
    v.PaymentTerms,
    v.VendorRatingInternal,
    COUNT(DISTINCT po.PONo)                                        AS TotalPOs,
    ROUND(SUM(po.TotalAmount), 2)                                   AS TotalSpendINR,
    ROUND(AVG(julianday(g.GRNDate) - julianday(po.PODate)), 1)      AS AvgActualLeadDays,
    ROUND(AVG(julianday(po.PromisedDeliveryDate) - julianday(po.PODate)), 1) AS AvgPromisedLeadDays,
    ROUND(100.0 * SUM(CASE WHEN g.GRNDate <= po.PromisedDeliveryDate THEN 1 ELSE 0 END)
          / NULLIF(COUNT(g.GRNNo), 0), 1)                           AS OnTimeDeliveryPct,
    ROUND(100.0 * SUM(g.RejectedQty) / NULLIF(SUM(g.ReceivedQty), 0), 2) AS RejectionRatePct,
    ROUND(100.0 * SUM(CASE WHEN i.PaymentStatus = 'Overdue' THEN 1 ELSE 0 END)
          / NULLIF(COUNT(i.InvoiceNo), 0), 1)                       AS InvoiceOverduePct,
    -- Composite score out of 100: on-time 40% + quality(1-rejection) 35% + rating 25%
    ROUND(
        0.40 * COALESCE(100.0 * SUM(CASE WHEN g.GRNDate <= po.PromisedDeliveryDate THEN 1 ELSE 0 END) / NULLIF(COUNT(g.GRNNo),0), 0) +
        0.35 * (100 - COALESCE(100.0 * SUM(g.RejectedQty) / NULLIF(SUM(g.ReceivedQty),0), 0)) +
        0.25 * (v.VendorRatingInternal / 5.0 * 100)
    , 1) AS SupplierPerformanceScore
FROM Vendor_Master v
LEFT JOIN PO_Data po        ON po.VendorCode = v.VendorCode
LEFT JOIN GRN_Data g        ON g.PONo = po.PONo
LEFT JOIN Invoice_Data i    ON i.PONo = po.PONo
GROUP BY v.VendorCode, v.VendorName, v.Vertical, v.State, v.PaymentTerms, v.VendorRatingInternal;

-- ---------------------------------------------------------------
-- 2. PR PROCESSING DASHBOARD
-- ---------------------------------------------------------------
DROP VIEW IF EXISTS vw_PR_Summary;
CREATE VIEW vw_PR_Summary AS
SELECT
    strftime('%Y-%m', PRDate)  AS Month,
    Vertical, DeptName, ProjectName, Priority, Status,
    COUNT(*)                    AS PRCount,
    SUM(RequestedQty)           AS TotalQtyRequested
FROM PR_Data
GROUP BY Month, Vertical, DeptName, ProjectName, Priority, Status;

-- ---------------------------------------------------------------
-- 3. PO PROCESSING DASHBOARD
-- ---------------------------------------------------------------
DROP VIEW IF EXISTS vw_PO_Summary;
CREATE VIEW vw_PO_Summary AS
SELECT
    strftime('%Y-%m', PODate)  AS Month,
    Vertical, VendorName, Status,
    COUNT(*)                    AS POCount,
    ROUND(SUM(TotalAmount), 2)  AS TotalPOValue,
    ROUND(AVG(TotalAmount), 2)  AS AvgPOValue
FROM PO_Data
GROUP BY Month, Vertical, VendorName, Status;

-- ---------------------------------------------------------------
-- 4. GRN PROCESSING DASHBOARD
-- ---------------------------------------------------------------
DROP VIEW IF EXISTS vw_GRN_Summary;
CREATE VIEW vw_GRN_Summary AS
SELECT
    strftime('%Y-%m', GRNDate) AS Month,
    Vertical, WarehouseCode, QCStatus,
    COUNT(*)                    AS GRNCount,
    SUM(ReceivedQty)            AS TotalReceivedQty,
    SUM(AcceptedQty)            AS TotalAcceptedQty,
    SUM(RejectedQty)            AS TotalRejectedQty,
    ROUND(100.0 * SUM(RejectedQty) / NULLIF(SUM(ReceivedQty), 0), 2) AS RejectionRatePct
FROM GRN_Data
GROUP BY Month, Vertical, WarehouseCode, QCStatus;

-- ---------------------------------------------------------------
-- 5. INVOICE PROCESSING DASHBOARD
-- ---------------------------------------------------------------
DROP VIEW IF EXISTS vw_Invoice_Summary;
CREATE VIEW vw_Invoice_Summary AS
SELECT
    strftime('%Y-%m', InvoiceDate) AS Month,
    Vertical, PaymentStatus,
    COUNT(*)                        AS InvoiceCount,
    ROUND(SUM(TotalAmount), 2)      AS TotalInvoiceValue,
    ROUND(AVG(julianday(PaymentDate) - julianday(PaymentDueDate)), 1) AS AvgPaymentDelayDays
FROM Invoice_Data
GROUP BY Month, Vertical, PaymentStatus;

-- ---------------------------------------------------------------
-- 6. WAREHOUSE INVENTORY DASHBOARD + INVENTORY AGING
-- ---------------------------------------------------------------
DROP VIEW IF EXISTS vw_WarehouseInventory;
CREATE VIEW vw_WarehouseInventory AS
SELECT
    WarehouseCode, WarehouseName, Vertical, ItemCode, ItemDescription,
    StockQty, ReorderLevel, StockStatus, AgingDays, StockValueINR,
    CASE
        WHEN AgingDays <= 30 THEN '0-30 days'
        WHEN AgingDays <= 60 THEN '31-60 days'
        WHEN AgingDays <= 90 THEN '61-90 days'
        ELSE '90+ days'
    END AS AgingBucket
FROM Inventory_Data;

-- ---------------------------------------------------------------
-- 7. DELIVERY TIME DASHBOARD + AVERAGE LEAD TIME DASHBOARD
-- ---------------------------------------------------------------
DROP VIEW IF EXISTS vw_DeliveryTime;
CREATE VIEW vw_DeliveryTime AS
SELECT
    po.PONo, po.PODate, po.Vertical, po.VendorName,
    g.GRNDate,
    julianday(po.PromisedDeliveryDate) - julianday(po.PODate) AS PromisedLeadDays,
    julianday(g.GRNDate) - julianday(po.PODate)                AS ActualLeadDays,
    julianday(g.GRNDate) - julianday(po.PromisedDeliveryDate)  AS DelayDays,
    CASE WHEN g.GRNDate <= po.PromisedDeliveryDate THEN 'On-Time' ELSE 'Delayed' END AS DeliveryStatus
FROM PO_Data po
JOIN GRN_Data g ON g.PONo = po.PONo;

-- ---------------------------------------------------------------
-- 8. TOTAL PROCUREMENT CYCLE TIME DASHBOARD (PR -> PO -> GRN -> Invoice)
-- ---------------------------------------------------------------
DROP VIEW IF EXISTS vw_ProcurementCycleTime;
CREATE VIEW vw_ProcurementCycleTime AS
SELECT
    pr.PRNo, po.PONo, g.GRNNo, inv.InvoiceNo,
    pr.Vertical, pr.DeptName, pr.ProjectName,
    julianday(po.PODate)        - julianday(pr.PRDate)   AS PR_to_PO_Days,
    julianday(g.GRNDate)        - julianday(po.PODate)   AS PO_to_GRN_Days,
    julianday(inv.InvoiceDate)  - julianday(g.GRNDate)   AS GRN_to_Invoice_Days,
    julianday(inv.InvoiceDate)  - julianday(pr.PRDate)   AS TotalCycleDays
FROM PR_Data pr
JOIN PO_Data po     ON po.PRNo = pr.PRNo
JOIN GRN_Data g     ON g.PONo = po.PONo
LEFT JOIN Invoice_Data inv ON inv.GRNNo = g.GRNNo;

-- ---------------------------------------------------------------
-- 9. MATERIAL PRICE / RATE ANALYSIS DASHBOARD
-- ---------------------------------------------------------------
DROP VIEW IF EXISTS vw_PriceRateAnalysis;
CREATE VIEW vw_PriceRateAnalysis AS
SELECT
    Month, Vertical, ItemCode, ItemDescription, VendorCode,
    UnitPrice, StandardPrice,
    ROUND(100.0 * (UnitPrice - StandardPrice) / NULLIF(StandardPrice, 0), 2) AS PriceVariancePct
FROM Price_History;

-- ---------------------------------------------------------------
-- 10. SPEND ANALYTICS (Monthly / Dept-Project / Category / Budget vs Actual)
-- ---------------------------------------------------------------
DROP VIEW IF EXISTS vw_MonthlySpend;
CREATE VIEW vw_MonthlySpend AS
SELECT strftime('%Y-%m', PODate) AS Month, ROUND(SUM(TotalAmount), 2) AS TotalSpend
FROM PO_Data WHERE Status != 'Cancelled' GROUP BY Month;

DROP VIEW IF EXISTS vw_SpendByCategory;
CREATE VIEW vw_SpendByCategory AS
SELECT Vertical AS Category, ROUND(SUM(TotalAmount), 2) AS TotalSpend, COUNT(*) AS POCount
FROM PO_Data WHERE Status != 'Cancelled' GROUP BY Vertical;

DROP VIEW IF EXISTS vw_SpendByDeptProject;
CREATE VIEW vw_SpendByDeptProject AS
SELECT po.DeptCode, d.DeptName, po.ProjectCode, d.ProjectName,
       ROUND(SUM(po.TotalAmount), 2) AS TotalSpend
FROM PO_Data po
JOIN Department_Project_Master d ON d.DeptCode = po.DeptCode
WHERE po.Status != 'Cancelled'
GROUP BY po.DeptCode, d.DeptName, po.ProjectCode, d.ProjectName;

DROP VIEW IF EXISTS vw_BudgetVsActual;
CREATE VIEW vw_BudgetVsActual AS
SELECT
    d.ProjectCode, d.ProjectName, d.BudgetAllocatedINR,
    ROUND(COALESCE(SUM(po.TotalAmount), 0), 2)                              AS ActualSpendINR,
    ROUND(d.BudgetAllocatedINR - COALESCE(SUM(po.TotalAmount), 0), 2)       AS VarianceINR,
    ROUND(100.0 * COALESCE(SUM(po.TotalAmount), 0) / d.BudgetAllocatedINR, 1) AS UtilizationPct
FROM Department_Project_Master d
LEFT JOIN PO_Data po ON po.ProjectCode = d.ProjectCode AND po.Status != 'Cancelled'
GROUP BY d.ProjectCode, d.ProjectName, d.BudgetAllocatedINR;

-- ---------------------------------------------------------------
-- 11. PROCUREMENT PERFORMANCE / ORDER FULFILMENT DASHBOARD
-- ---------------------------------------------------------------
DROP VIEW IF EXISTS vw_OrderFulfilment;
CREATE VIEW vw_OrderFulfilment AS
SELECT
    strftime('%Y-%m', pr.PRDate) AS Month,
    COUNT(*)                                                      AS TotalPRs,
    SUM(CASE WHEN pr.Status = 'Converted to PO' THEN 1 ELSE 0 END) AS ConvertedToPO,
    ROUND(100.0 * SUM(CASE WHEN pr.Status = 'Converted to PO' THEN 1 ELSE 0 END) / COUNT(*), 1) AS PRFulfilmentPct,
    SUM(CASE WHEN pr.Status = 'Rejected' THEN 1 ELSE 0 END)        AS RejectedPRs,
    SUM(CASE WHEN pr.Status = 'Pending Approval' THEN 1 ELSE 0 END) AS PendingPRs
FROM PR_Data pr
GROUP BY Month;

-- ---------------------------------------------------------------
-- 12. OPERATIONS KPI DASHBOARD (blended operational KPIs)
-- ---------------------------------------------------------------
DROP VIEW IF EXISTS vw_OperationsKPI;
CREATE VIEW vw_OperationsKPI AS
SELECT
    (SELECT COUNT(*) FROM PR_Data)                                             AS TotalPRs,
    (SELECT COUNT(*) FROM PO_Data WHERE Status != 'Cancelled')                 AS TotalPOs,
    (SELECT ROUND(SUM(TotalAmount),2) FROM PO_Data WHERE Status != 'Cancelled') AS TotalProcurementSpend,
    (SELECT COUNT(*) FROM GRN_Data)                                            AS TotalGRNs,
    (SELECT ROUND(100.0*SUM(RejectedQty)/NULLIF(SUM(ReceivedQty),0),2) FROM GRN_Data) AS OverallRejectionPct,
    (SELECT COUNT(*) FROM Invoice_Data)                                        AS TotalInvoices,
    (SELECT ROUND(100.0*SUM(CASE WHEN PaymentStatus='Overdue' THEN 1 ELSE 0 END)/COUNT(*),2) FROM Invoice_Data) AS InvoiceOverduePct,
    (SELECT ROUND(AVG(julianday(g.GRNDate)-julianday(po.PODate)),1)
        FROM PO_Data po JOIN GRN_Data g ON g.PONo = po.PONo)                   AS AvgLeadTimeDays,
    (SELECT ROUND(100.0*SUM(CASE WHEN g.GRNDate<=po.PromisedDeliveryDate THEN 1 ELSE 0 END)/COUNT(*),1)
        FROM PO_Data po JOIN GRN_Data g ON g.PONo = po.PONo)                   AS OnTimeDeliveryPctOverall;

-- ---------------------------------------------------------------
-- 13. EXCEPTION / RISK DASHBOARD
-- ---------------------------------------------------------------
DROP VIEW IF EXISTS vw_ExceptionRisk;
CREATE VIEW vw_ExceptionRisk AS
SELECT 'Delayed Delivery' AS ExceptionType, po.PONo AS RefNo, po.VendorName AS Party,
       po.Vertical, julianday(g.GRNDate)-julianday(po.PromisedDeliveryDate) AS Severity,
       po.PODate AS EventDate
FROM PO_Data po JOIN GRN_Data g ON g.PONo = po.PONo
WHERE g.GRNDate > po.PromisedDeliveryDate
UNION ALL
SELECT 'GRN Rejection', g.GRNNo, g.VendorCode, g.Vertical,
       ROUND(100.0*g.RejectedQty/NULLIF(g.ReceivedQty,0),1), g.GRNDate
FROM GRN_Data g WHERE g.RejectedQty > 0
UNION ALL
SELECT 'Overdue Invoice', i.InvoiceNo, i.VendorName, i.Vertical,
       julianday('now')-julianday(i.PaymentDueDate), i.InvoiceDate
FROM Invoice_Data i WHERE i.PaymentStatus = 'Overdue'
UNION ALL
SELECT 'Price Spike (>15% above standard)', ph.ItemCode, ph.VendorCode, ph.Vertical,
       ROUND(100.0*(ph.UnitPrice-ph.StandardPrice)/NULLIF(ph.StandardPrice,0),1), ph.Month
FROM Price_History ph WHERE ph.UnitPrice > ph.StandardPrice * 1.15
UNION ALL
SELECT 'Below Reorder Stock', inv.ItemCode, inv.WarehouseCode, inv.Vertical,
       inv.ReorderLevel - inv.StockQty, inv.LastReceivedDate
FROM Inventory_Data inv WHERE inv.StockStatus = 'Below Reorder';

-- ---------------------------------------------------------------
-- 14. MONTHLY PROCUREMENT TREND DASHBOARD
-- ---------------------------------------------------------------
DROP VIEW IF EXISTS vw_MonthlyProcurementTrend;
CREATE VIEW vw_MonthlyProcurementTrend AS
SELECT
    strftime('%Y-%m', po.PODate) AS Month,
    COUNT(*)                      AS POCount,
    ROUND(SUM(po.TotalAmount),2)  AS TotalSpend,
    COUNT(DISTINCT po.VendorCode) AS ActiveVendors
FROM PO_Data po
WHERE po.Status != 'Cancelled'
GROUP BY Month;

-- ---------------------------------------------------------------
-- 15. EXECUTIVE / MANAGEMENT DASHBOARD (top KPI tiles)
-- ---------------------------------------------------------------
DROP VIEW IF EXISTS vw_ExecutiveSummary;
CREATE VIEW vw_ExecutiveSummary AS
SELECT * FROM vw_OperationsKPI;

-- ---------------------------------------------------------------
-- 16. PROJECT OUTCOMES / COST OPTIMIZATION DASHBOARD
--     Savings = (Standard/benchmark price x qty) - (Actual PO value),
--     realised through negotiated/blanket rates, consolidated ordering,
--     and multi-vendor rate comparison enabled by this project.
-- ---------------------------------------------------------------
DROP VIEW IF EXISTS vw_CostOptimization;
CREATE VIEW vw_CostOptimization AS
SELECT
    po.Vertical,
    ROUND(SUM(m.StandardPrice * po.OrderedQty), 2)   AS BenchmarkCost,
    ROUND(SUM(po.TotalAmount), 2)                    AS ActualCost,
    ROUND(SUM(m.StandardPrice * po.OrderedQty) - SUM(po.TotalAmount), 2) AS SavingsINR,
    ROUND(100.0 * (SUM(m.StandardPrice * po.OrderedQty) - SUM(po.TotalAmount))
          / NULLIF(SUM(m.StandardPrice * po.OrderedQty), 0), 2)         AS SavingsPct
FROM PO_Data po
JOIN Material_Master m ON m.ItemCode = po.ItemCode
WHERE po.Status != 'Cancelled'
GROUP BY po.Vertical;
