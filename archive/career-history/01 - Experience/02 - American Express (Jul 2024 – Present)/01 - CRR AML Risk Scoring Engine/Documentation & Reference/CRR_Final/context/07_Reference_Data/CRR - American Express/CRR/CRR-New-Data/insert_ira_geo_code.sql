--liquibase formatted sql


--changeset author:rdube26:insert_ira_geo_code
INSERT INTO ira_geo_div (ira_geo_div_cd, geo_div_nm) VALUES ('EMEA', 'Europe Middle East Africa');
INSERT INTO ira_geo_div (ira_geo_div_cd, geo_div_nm) VALUES ('JAPA', 'Japan Asia Pacific & Australia');
INSERT INTO ira_geo_div (ira_geo_div_cd, geo_div_nm) VALUES ('LACC', 'Latin America Caribbean Canada');
INSERT INTO ira_geo_div (ira_geo_div_cd, geo_div_nm) VALUES ('US', 'United States');
INSERT INTO ira_geo_div (ira_geo_div_cd, geo_div_nm) VALUES ('AMER', ' ');
