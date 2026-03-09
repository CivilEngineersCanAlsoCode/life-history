--liquibase formatted sql

--changeset author:rdube26:insert_assess_sta
INSERT INTO assess_sta (assess_sta_cd, assess_sta_nm)
VALUES (1, 'New Score');
INSERT INTO assess_sta (assess_sta_cd, assess_sta_nm)
VALUES (2, 'Production Score');
