--liquibase formatted sql

--changeset author:rdube26:insert_ira_occpt
INSERT INTO ira_occpt (ira_occpt_cd , occptnm, creat_user_id, creat_ts) VALUES ('LL', 'Surveyor/ Bookkeeper/ Accounting/ Consultant', 'SYSTEM', '2021-11-23T16:08:03.154-07:00')
