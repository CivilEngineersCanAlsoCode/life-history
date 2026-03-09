--liquibase formatted sql

--changeset author:rdube26:insert_ira_pty_type_grp
INSERT INTO ira_pty_type_grp (ira_type_grp_cd, pty_type_grp_nm, ira_pty_type_grp_ctgy_cd) VALUES ('ASSOC', 'Associations', '');
INSERT INTO ira_pty_type_grp (ira_type_grp_cd, pty_type_grp_nm, ira_pty_type_grp_ctgy_cd) VALUES ('COMPLT', 'Companies, Limited', '');
INSERT INTO ira_pty_type_grp (ira_type_grp_cd, pty_type_grp_nm, ira_pty_type_grp_ctgy_cd) VALUES ('COMP', 'Companies, Private', '');
INSERT INTO ira_pty_type_grp (ira_type_grp_cd, pty_type_grp_nm, ira_pty_type_grp_ctgy_cd) VALUES ('COMPEL', 'Companies, Private - EMEA/LAC ', '');
INSERT INTO ira_pty_type_grp (ira_type_grp_cd, pty_type_grp_nm, ira_pty_type_grp_ctgy_cd) VALUES ('COOP', 'Cooperatives', '');
INSERT INTO ira_pty_type_grp (ira_type_grp_cd, pty_type_grp_nm, ira_pty_type_grp_ctgy_cd) VALUES ('CORPLT', 'Corporations, Limited ', '');
INSERT INTO ira_pty_type_grp (ira_type_grp_cd, pty_type_grp_nm, ira_pty_type_grp_ctgy_cd) VALUES ('CORP', 'Corporations, Private ', '');
INSERT INTO ira_pty_type_grp (ira_type_grp_cd, pty_type_grp_nm, ira_pty_type_grp_ctgy_cd) VALUES ('CORPEL', 'Corporations, Private - EMEA/LAC  ', '');
INSERT INTO ira_pty_type_grp (ira_type_grp_cd, pty_type_grp_nm, ira_pty_type_grp_ctgy_cd) VALUES ('PUBLIC', 'Companies & Corporations, Public  ', 'PT');
INSERT INTO ira_pty_type_grp (ira_type_grp_cd, pty_type_grp_nm, ira_pty_type_grp_ctgy_cd) VALUES ('BANK', 'Financial Institutions', '');
INSERT INTO ira_pty_type_grp (ira_type_grp_cd, pty_type_grp_nm, ira_pty_type_grp_ctgy_cd) VALUES ('FOUND', 'Foundations ', '');
INSERT INTO ira_pty_type_grp (ira_type_grp_cd, pty_type_grp_nm, ira_pty_type_grp_ctgy_cd) VALUES ('GOV', 'Government', 'GOV');
INSERT INTO ira_pty_type_grp (ira_type_grp_cd, pty_type_grp_nm, ira_pty_type_grp_ctgy_cd) VALUES ('GROUP', 'Interest Groups ', '');
INSERT INTO ira_pty_type_grp (ira_type_grp_cd, pty_type_grp_nm, ira_pty_type_grp_ctgy_cd) VALUES ('JOINT', 'Joint Ventures  ', '');
INSERT INTO ira_pty_type_grp (ira_type_grp_cd, pty_type_grp_nm, ira_pty_type_grp_ctgy_cd) VALUES ('NONPRO', 'Non-Profit/Charity', '');
INSERT INTO ira_pty_type_grp (ira_type_grp_cd, pty_type_grp_nm, ira_pty_type_grp_ctgy_cd) VALUES ('OTHER', 'Other ', '');
INSERT INTO ira_pty_type_grp (ira_type_grp_cd, pty_type_grp_nm, ira_pty_type_grp_ctgy_cd) VALUES ('PARTNR', 'Partnerships', '');
INSERT INTO ira_pty_type_grp (ira_type_grp_cd, pty_type_grp_nm, ira_pty_type_grp_ctgy_cd) VALUES ('PARTEL', 'Partnerships - EMEA/LAC ', '');
INSERT INTO ira_pty_type_grp (ira_type_grp_cd, pty_type_grp_nm, ira_pty_type_grp_ctgy_cd) VALUES ('PARTPU', 'Partnerships, Public  ', 'PT');
INSERT INTO ira_pty_type_grp (ira_type_grp_cd, pty_type_grp_nm, ira_pty_type_grp_ctgy_cd) VALUES ('SOCIET', 'Societies ', '');
INSERT INTO ira_pty_type_grp (ira_type_grp_cd, pty_type_grp_nm, ira_pty_type_grp_ctgy_cd) VALUES ('SOLE', 'Sole Proprietorships  ', 'TR');
INSERT INTO ira_pty_type_grp (ira_type_grp_cd, pty_type_grp_nm, ira_pty_type_grp_ctgy_cd) VALUES ('TRUSTS', 'Trusts', '');
INSERT INTO ira_pty_type_grp (ira_type_grp_cd, pty_type_grp_nm, ira_pty_type_grp_ctgy_cd) VALUES ('SOE', 'State-Owned ', 'SOE');
