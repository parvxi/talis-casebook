-- The Roastery Heist: quiz data schema + seed
DROP TABLE IF EXISTS badge_logs, orders, shipments, beans, staff CASCADE;

CREATE TABLE staff (
  staff_id    INT PRIMARY KEY,
  full_name   TEXT NOT NULL,
  role        TEXT NOT NULL,
  hired_on    DATE NOT NULL,
  badge_level INT  NOT NULL
);

CREATE TABLE beans (
  bean_id        INT PRIMARY KEY,
  lot_name       TEXT NOT NULL,
  origin_country TEXT NOT NULL,
  variety        TEXT NOT NULL,
  process        TEXT NOT NULL,          -- Washed / Natural / Honey / Anaerobic
  price_per_kg   NUMERIC(6,2) NOT NULL,
  kg_in_stock    NUMERIC(7,1) NOT NULL
);

CREATE TABLE shipments (
  shipment_id    INT PRIMARY KEY,
  bean_id        INT NOT NULL REFERENCES beans(bean_id),
  arrived_on     DATE NOT NULL,
  kg             NUMERIC(7,1) NOT NULL,
  warehouse_zone CHAR(1) NOT NULL         -- A, B, C
);

CREATE TABLE orders (
  order_id   INT PRIMARY KEY,
  bean_id    INT NOT NULL REFERENCES beans(bean_id),
  customer   TEXT NOT NULL,
  kg         NUMERIC(6,1) NOT NULL,
  ordered_on DATE NOT NULL
);

CREATE TABLE badge_logs (
  log_id    INT PRIMARY KEY,
  staff_id  INT NOT NULL REFERENCES staff(staff_id),
  zone      CHAR(1) NOT NULL,
  direction TEXT NOT NULL CHECK (direction IN ('in','out')),
  swiped_at TIMESTAMP NOT NULL
);

INSERT INTO staff VALUES
 (1,'Amira Haddad',  'Head Roaster',     '2019-03-04',3),
 (2,'Tomás Rivera',  'Warehouse Lead',   '2020-07-13',3),
 (3,'Priya Nair',    'Barista',          '2024-01-22',1),
 (4,'Jonah Fields',  'Green Buyer',      '2021-11-01',3),
 (5,'Lena Okafor',   'Quality Control',  '2022-05-16',2),
 (6,'Marcus Lee',    'Night Security',   '2023-09-09',2),
 (7,'Sofia Petrova', 'Logistics',        '2024-06-03',2),
 (8,'Ahmed Zaki',    'Barista',          '2025-02-10',1);

INSERT INTO beans VALUES
 (1,'Guji Highlands',    'Ethiopia',  'Heirloom',   'Natural',   24.50, 310.0),
 (2,'Yirgacheffe Konga', 'Ethiopia',  'Heirloom',   'Washed',    22.00, 265.5),
 (3,'Huila Reserve',     'Colombia',  'Caturra',    'Washed',    18.75, 420.0),
 (4,'Finca La Esperanza','Colombia',  'Gesha',      'Washed',    96.00,  18.0),
 (5,'Nyeri AA',          'Kenya',     'SL28',       'Washed',    27.30, 150.0),
 (6,'Boquete Gesha',     'Panama',    'Gesha',      'Natural',  142.00,  12.0),
 (7,'Sidamo Sun-Dried',  'Ethiopia',  'Heirloom',   'Natural',   21.40, 198.0),
 (8,'Minas Pulped',      'Brazil',    'Yellow Bourbon','Honey',  14.90, 640.0),
 (9,'Cerrado Estate',    'Brazil',    'Catuai',     'Natural',   13.20, 580.0),
 (10,'Antigua Valley',   'Guatemala', 'Bourbon',    'Washed',    19.60, 230.0),
 (11,'Tarrazú Anaerobic','Costa Rica','Catuai',     'Anaerobic', 38.00,  45.0),
 (12,'Kochere Micro-Lot','Ethiopia',  'Heirloom',   'Anaerobic', 41.50,  30.0);

INSERT INTO shipments VALUES
 (101,1,'2026-09-02',200.0,'A'),
 (102,3,'2026-09-04',300.0,'A'),
 (103,8,'2026-09-05',400.0,'B'),
 (104,6,'2026-09-15', 12.0,'C'),
 (105,4,'2026-09-15', 18.0,'C'),
 (106,11,'2026-09-18', 45.0,'C'),
 (107,12,'2026-09-18', 30.0,'C'),
 (108,9,'2026-09-20',380.0,'B'),
 (109,5,'2026-09-22',150.0,'A'),
 (110,2,'2026-09-25',265.5,'A'),
 (111,10,'2026-09-28',230.0,'A'),
 (112,7,'2026-10-01',198.0,'A'),
 (113,1,'2026-10-03',110.0,'A'),
 (114,3,'2026-10-06',120.0,'B'),
 (115,8,'2026-10-08',240.0,'B');

INSERT INTO orders VALUES
 (501,1,'Bull City Coffee',  40.0,'2026-10-02'),
 (502,3,'Ninth Street Cafe', 60.0,'2026-10-02'),
 (503,8,'Campus Grounds',   120.0,'2026-10-03'),
 (504,1,'Campus Grounds',    25.0,'2026-10-05'),
 (505,5,'Bull City Coffee',  30.0,'2026-10-06'),
 (506,9,'Ninth Street Cafe', 90.0,'2026-10-07'),
 (507,2,'Bull City Coffee',  35.0,'2026-10-08'),
 (508,3,'Campus Grounds',    80.0,'2026-10-09'),
 (509,10,'Ninth Street Cafe',45.0,'2026-10-10'),
 (510,8,'Bull City Coffee',  70.0,'2026-10-11'),
 (511,7,'Campus Grounds',    20.0,'2026-10-12'),
 (512,1,'Ninth Street Cafe', 50.0,'2026-10-13');

-- Badge logs: Zone C (the vault) over the week of the heist (night of Oct 11 -> Oct 12)
INSERT INTO badge_logs VALUES
 (1, 2,'A','in', '2026-10-10 07:58:00'),
 (2, 2,'A','out','2026-10-10 16:05:00'),
 (3, 5,'C','in', '2026-10-10 10:15:00'),
 (4, 5,'C','out','2026-10-10 10:42:00'),
 (5, 6,'B','in', '2026-10-10 22:00:00'),
 (6, 6,'C','in', '2026-10-10 23:10:00'),
 (7, 6,'C','out','2026-10-10 23:14:00'),
 (8, 6,'B','out','2026-10-11 06:00:00'),
 (9, 4,'C','in', '2026-10-11 09:30:00'),
 (10,4,'C','out','2026-10-11 09:55:00'),
 (11,1,'A','in', '2026-10-11 08:02:00'),
 (12,1,'A','out','2026-10-11 17:20:00'),
 (13,7,'C','in', '2026-10-11 14:00:00'),
 (14,7,'C','out','2026-10-11 14:20:00'),
 (15,6,'B','in', '2026-10-11 22:01:00'),
 (16,6,'C','in', '2026-10-11 23:05:00'),
 (17,6,'C','out','2026-10-11 23:09:00'),
 (18,7,'C','in', '2026-10-12 01:12:00'),
 (19,7,'C','out','2026-10-12 01:58:00'),
 (20,6,'B','out','2026-10-12 06:02:00'),
 (21,2,'C','in', '2026-10-12 08:10:00'),
 (22,2,'C','out','2026-10-12 08:25:00'),
 (23,3,'A','in', '2026-10-12 08:55:00'),
 (24,3,'A','out','2026-10-12 15:00:00'),
 (25,7,'C','in', '2026-10-13 02:05:00'),
 (26,7,'C','out','2026-10-13 02:40:00'),
 (27,8,'A','in', '2026-10-13 09:00:00'),
 (28,8,'A','out','2026-10-13 15:30:00'),
 (29,6,'C','in', '2026-10-12 23:20:00'),
 (30,6,'C','out','2026-10-12 23:24:00');
